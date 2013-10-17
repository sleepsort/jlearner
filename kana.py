#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import random
import sys

USAGE= '''
  usage:
    ./kana.py [TEST_OPTION] [RANDOM_OPTION]

    TEST_OPTION:
      -hr  : Hiragana->Romaji test (default)
      -kr  : Katakana->Romaji test
      -rh  : Romaji->Hiragana test
      -rk  : Romaji->Katakana test

    RANDOM_OPTION:
      -s   : shuffle character table
'''

COLUMNS = 5
TIMEOUT = 3

FONT_BASE = "Fixsys"
#FONT_BASE = "DroidSansMono"

DEFAULT_FONT_LARGE = "%s 30" % FONT_BASE
DEFAULT_FONT = "%s 15"      % FONT_BASE
SUCCESS_FONT = "%s 15 bold" % FONT_BASE

DEFAULT_COLOR = "black"
SUCCESS_COLOR = "red"

class JLearner(Frame):
  def __init__(self, option_type='-hr', option_shuffle=''):
    """Create and grid several components into the frame"""
    Frame.__init__(self)

    self.option_shuffle = option_shuffle
    self.option_type = option_type

    self.wrong = 0
    self.right = 0
    self.pending = {}
    self.backup = {}

    self.active_text = {"suggest" : StringVar(), "input" : StringVar()}

    self.key = "empty"
    self.alarm = None

    self.active_text["suggest"].set(self.key)

    self.init_widgets()

    self.after(50, self.next())

  def init_widgets(self):
    self.pack(expand = NO, fill = BOTH)
    self.master.title("Japanese Learning")
    self.master.geometry("300x700")

    self.master.rowconfigure(0, weight = 1)
    self.master.columnconfigure(0, weight = 1)
    self.grid(sticky = W+E+N+S)

    self.buttons = {}
    self.row = 0

    if option_type == '-kr' or option_type == '-rk':
      self.pending = self.init_buttons(r"data/kana/katakana.dat")
    else:
      self.pending = self.init_buttons(r"data/kana/hiragana.dat")
    self.backup = dict(self.pending)

    suggest_pane = Label(self)
    suggest_pane["textvariable"] = self.active_text["suggest"]
    suggest_pane["width"] = 20
    suggest_pane["font"] = DEFAULT_FONT_LARGE
    suggest_pane.grid(row = self.row, rowspan = 2, columnspan=COLUMNS, sticky = W+E+N+S)
    self.rowconfigure(self.row, weight = 1)
    self.row += 2

    if option_type == '-hr' or option_type == '-kr':
      hint_text = u"Input Romaji:"
    else:
      hint_text = u"Answer with button."
    hint_text = hint_text.encode("utf-8")
    hint_pane = Label(self, text = hint_text)
    hint_pane["width"] = 25
    hint_pane["height"] = 1
    hint_pane.grid(row = self.row, column = 0, columnspan = COLUMNS/2, sticky = W+E+N+S)

    if option_type == '-hr' or option_type == '-kr':
      input_pane = Entry(self)
      input_pane["textvariable"] = self.active_text["input"]
      input_pane["width"]=10
      input_pane.grid(row = self.row, column = COLUMNS/2+1, columnspan = COLUMNS/2, sticky = W+E+N+S)
      input_pane.bind("<Return>", self.test_kana)
      input_pane.bind("<Escape>",self.cancel)
      input_pane.focus_set()
      self.row += 2

      confirm_button = Button(self, text = "Confirm", width = 25)
      confirm_button.grid(row = self.row, column = 0, columnspan = COLUMNS/2, sticky = W+E+N+S)
      confirm_button["width"] = 10
      confirm_button.bind("<ButtonRelease>", self.test_kana)

      cancel_button = Button(self, text = "Cancel")
      cancel_button.grid(row = self.row, column = COLUMNS/2+1, columnspan = COLUMNS/2, sticky = W+E+N+S)
      cancel_button["width"] = 10
      cancel_button.bind("<ButtonRelease>", self.cancel)

    for i in range(0, COLUMNS):
      self.columnconfigure(i, weight = 1)

  def set_timeout(self):
    if self.option_type == '-rh' or self.option_type == '-rk':
      key = self.pending.keys()[self.pending.values().index(self.key)]
    else:
      key = self.key
    self.fail(key)
    self.next()

  def test_romaji(self, event):
    self.after_cancel(self.alarm)
    text = event.widget["text"]
    if text not in self.pending:
      return
    key = self.pending.keys()[self.pending.values().index(self.key)]
    if self.key != self.pending[text]:
      self.fail(key)
    else:
      self.success(key)
    self.next()

  def test_kana(self, event):
    self.after_cancel(self.alarm)
    text = self.active_text["input"].get()
    if text != self.pending[self.key]:
      self.fail(self.key)
    else:
      self.success(self.key)
    self.active_text["input"].set("")
    self.next()

  def fail(self, key):
    self.wrong += 1
    showerror("Message", u"No no no!\n"+key+":"+self.pending[key])
    showerror("Message", u"Remember!\n"+key+":"+self.pending[key])

  def success(self, key):
    showinfo("Message", u"Right!")
    self.right += 1
    self.buttons[key]["foreground"] = SUCCESS_COLOR
    self.buttons[key]["font"] = SUCCESS_FONT
    del self.pending[key]

  def retry(self, event):
    event.widget["foreground"] = DEFAULT_COLOR
    event.widget["font"] = DEFAULT_FONT
    self.pending[event.widget["text"]] = self.backup[event.widget["text"]]

  def cancel(self, event):
    self.quit()

  def next(self):
    if self.pending:
      key = random.choice(self.pending.keys())
      if self.option_type == '-rh' or self.option_type == '-rk':
        self.key = self.pending[key]
      else:
        self.key = key
      self.active_text["suggest"].set(self.key)
      self.alarm = self.after(TIMEOUT * 1000, self.set_timeout)
      return
    self.log(r"log/kana.dat")
    self.quit()

  def log(self, filename):
    tests = [u'あ->a', u'ア->a', u'a->あ', u'a->ア']
    values = [[0,0], [0,0], [0,0], [0,0]]
    try:
      data = open(filename, "rb")
      for i, line in enumerate(data.readlines()):
        line = line.strip().split(':')[1]
        line = line.strip().replace(' ', '=').split("=")
        values[i][0] = int(line[1])
        values[i][1] = int(line[3])
    except Exception, e:
      pass

    if self.option_type == '-hr':
      prefix = tests[0]
    elif self.option_type == '-kr':
      prefix = tests[1]
    elif self.option_type == '-rh':
      prefix = tests[2]
    else:
      prefix = tests[3]

    count = dict(zip(tests, values))
    count[prefix][0] += self.right
    count[prefix][1] += self.wrong

    write = open(filename, "w").write
    for key in tests:
      write("%s: pass=%d fail=%d\n" % (key.encode('utf-8'), count[key][0], count[key][1]))

    info = "Complete!\n\n";
    info += "Result:\n";
    info += "pass:=%d fail=%d\n\n" % (self.right, self.wrong)
    info += "Total Summary:\n"
    info += "\tpass\tfail\n"
    for key in tests:
      info += "%s:\t%d\t%d\n" % (key.encode('utf-8'), count[key][0], count[key][1])
    showinfo("Message", info)

  def init_buttons(self, filename):
    try:
      data = open(filename, "rb").read().decode("utf-8")
    except IOError, message:
      print >> sys.stderr, "File could not be opened:", message
      sys.exit(1)
    records = data.splitlines(0)
    if option_shuffle == '-s':
      random.shuffle(records)
    dic = {}
    for i, record in enumerate(records):
      fields = record.split()
      button = Button(self, text = "  ")
      button["font"] = DEFAULT_FONT
      row = self.row + i / COLUMNS
      column = i % COLUMNS
      button.grid(row = row, column = column, sticky = W+E+N+S)
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        dic[fields[0]] = fields[1]
        button["text"] = fields[0]
        if self.option_type == '-rh' or self.option_type == '-rk':
          button.bind("<ButtonRelease>", self.test_romaji)
        else:
          button.bind("<ButtonRelease>", self.retry)
        self.buttons[fields[0]] = button
    self.row += (len(records) + COLUMNS - 1) / COLUMNS
    return dic

def main(option_type, option_shuffle):
  JLearner(option_type, option_shuffle).mainloop()

if __name__ == "__main__":
  argv = sys.argv[1:]

  option1 = set(argv) & set(['-hr', '-kr', '-rk', '-rh'])
  option2 = set(argv) & set(['-s'])
  option1 = list(option1)
  option2 = list(option2)

  if argv and not option1 and not option2:
    print USAGE
    sys.exit(1)

  option_type = '-hr'
  option_shuffle = ''

  if option1:
    option_type = option1[0]
  if option2:
    option_shuffle = option2[0]

  main(option_type, option_shuffle)
