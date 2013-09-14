#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import random
import time
import codecs
import sys

USAGE= '''
  usage:
    ./run.py [TEST_OPTION] [RANDOM_OPTION]
    
    TEST_OPTION:
      -hr  : Hiragana->Romaji test (default)
      -kr  : Katakana->Romaji test
      -rh  : Romaji->Hiragana test
      -rk  : Romaji->Katakana test

    RANDOM_OPTION:
      -s   : shuffle character table
'''

BUTTON_COLUMNS = 5
TIMEOUT = 3

SUCCESS_COLOR = "red"
DEFAULT_COLOR = "black"
SUCCESS_FONT = "Fixsys 15 bold"
DEFAULT_FONT = "Fixsys 15"
DEFAULT_FONT_LARGE = "Fixsys 30"

class JLearner(Frame):
  def __init__(self, type='-hr', shuffle=''):
    """Create and grid several components into the frame"""
    Frame.__init__(self)
    self.pack(expand = NO, fill = BOTH)
    self.master.title("Japanese Learning")
    self.master.geometry("300x700")

    self.master.rowconfigure(0, weight = 1)
    self.master.columnconfigure(0, weight = 1)
    self.grid(sticky = W+E+N+S)

    self.wrong = 0
    self.right = 0
    self.dic = {}
    self.copy = {}

    self.shuffle = shuffle
    self.type = type
    self.buttons = {}
    self.row = 0
    self.key = "empty"
    self.alarm = None

    if type == '-kr' or type == '-rk':
      self.dic = self.init(r"data/katakana.dat")
    else:
      self.dic = self.init(r"data/hiragana.dat")
    self.copy = dict(self.dic)

    self.suggestText = StringVar()
    self.suggestText.set(self.key)
    suggestLabel = Label(self, textvariable = self.suggestText)
    suggestLabel["width"] = 20
    suggestLabel["height"] = 3
    suggestLabel["font"] = DEFAULT_FONT_LARGE
    suggestLabel.grid(rowspan = 2, columnspan=BUTTON_COLUMNS, sticky = W+E+N+S)

    if type == '-hr' or type == '-kr':
      hintText = u"Romanization:"
    else:
      hintText = u"Answer with button."
    hintText = hintText.encode("utf-8")
    hintLabel = Label(self, text = hintText)
    hintLabel["width"] = 25
    hintLabel["height"] = 1
    hintLabel.grid(row = self.row + 3, column = 0, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)

    if type == '-hr' or type == '-kr':
      self.inputText = StringVar()
      inputPane = Entry(self, textvariable = self.inputText)
      inputPane["width"]=10
      inputPane.grid(row = self.row+3, column = BUTTON_COLUMNS/2+1, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)
      inputPane.bind("<Return>", self.confirmKana)
      inputPane.bind("<Escape>",self.cancel)
      inputPane.focus_set()

      confirmButton = Button(self, text = "Confirm", width = 25)
      confirmButton.grid(row = self.row+5, column = 0, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)
      confirmButton["width"] = 10
      confirmButton.bind("<ButtonRelease>", self.confirmKana)

      cancelButton = Button(self, text = "Cancel")
      cancelButton.grid(row = self.row+5, column = BUTTON_COLUMNS/2+1, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)
      cancelButton["width"] = 10
      cancelButton.bind("<ButtonRelease>", self.cancel)

    # make second row/column expand
    self.rowconfigure(self.row + 1, weight = 1)
    for i in range(0, BUTTON_COLUMNS):
      self.columnconfigure(i, weight = 1)
    self.next()

  def setTimeout(self):
    if self.type == '-rh' or self.type == '-rk':
      key = self.dic.keys()[self.dic.values().index(self.key)]
    else:
      key = self.key
    self.fail(key)
    self.next()

  def confirmRomaji(self, event):
    self.after_cancel(self.alarm)
    text = event.widget["text"]
    if text not in self.dic:
      return
    key = self.dic.keys()[self.dic.values().index(self.key)]
    if self.key != self.dic[text]:
      self.fail(key)
    else:
      self.success(key)
    self.next()

  def confirmKana(self, event):
    self.after_cancel(self.alarm)
    input = self.inputText.get()
    if input != self.dic[self.key]:
      self.fail(self.key)
    else:
      self.success(self.key)
    self.inputText.set("")
    self.next()

  def fail(self, key):
    showerror("Message", u"No no no!\n"+key+":"+self.dic[key])
    showerror("Message", u"Remember!\n"+key+":"+self.dic[key])
    self.wrong = self.wrong + 1

  def success(self, key):
    showinfo("Message", u"Right!")
    self.right = self.right + 1
    self.buttons[key]["foreground"] = SUCCESS_COLOR
    self.buttons[key]["font"] = SUCCESS_FONT
    del self.dic[key]

  def retry(self, event):
    event.widget["foreground"] = DEFAULT_COLOR
    event.widget["font"] = DEFAULT_FONT
    self.dic[event.widget["text"]] = self.copy[event.widget["text"]]

  def cancel(self, event):
    self.quit()

  def next(self):
    if len(self.dic):
      key = random.choice(self.dic.keys())
      if self.type == '-rh' or self.type == '-rk':
        self.key = self.dic[key]
      else:
        self.key = key
      self.suggestText.set(self.key)
      self.alarm = self.after(TIMEOUT * 1000, self.setTimeout)
      return
    info = u"Complete!\n";
    info += "Result:\t";
    info += "Right Answers:\t%s\n" % str(self.right)
    info += "\tWrong Answers:\t%s\n" % str(self.wrong)
    showinfo("Message", info)
    self.quit()

  def init(self, filename):
    try:
      file = open(filename, "rb").read()
    except IOError, message:
      print >> sys.stderr, "File could not be opened:", message
      sys.exit(1)
    if file[:3] == codecs.BOM_UTF8:     # Byte Order Map in utf-8 file (created in Windonws)
      file = file[3:]
    file = file.decode("utf-8")
    records = file.splitlines(0)
    map = {}
    n = len(self.buttons)
    if shuffle == '-s':
      random.shuffle(records)
    for record in records:              # format each line
      fields = record.split()
      button = Button(self, text = "  ")
      button["font"] = DEFAULT_FONT
      row = self.row + n / BUTTON_COLUMNS
      column = n % BUTTON_COLUMNS
      button.grid(row = row, column = column, sticky = W+E+N+S)
      if len(fields) != 0 and fields[0][0] != '#':  # ignore lines with heading '#'
        map[fields[0]] = fields[1]
        button["text"] = fields[0]
        if self.type == '-rh' or self.type == '-rk':
          button.bind("<ButtonRelease>", self.confirmRomaji)
        else:
          button.bind("<ButtonRelease>", self.retry)
        self.buttons[fields[0]] = button
      n = n + 1
    self.row += (n + BUTTON_COLUMNS - 1) / BUTTON_COLUMNS
    return map

def main(type, shuffle):
  JLearner(type, shuffle).mainloop()
if __name__ == "__main__":
  type = '-hr'
  shuffle = ''
  if len(sys.argv) > 1:
    type = sys.argv[1]
  if len(sys.argv) > 2:
    shuffle = sys.argv[2]
  if type not in ['-hr', '-kr', '-rk', '-rh']:
    print USAGE
    sys.exit(1)
  if shuffle not in ['', '-s']:
    print USAGE
    sys.exit(1)
  main(type, shuffle)
