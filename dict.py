#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import random
import sys

USAGE= '''
  usage:
    ./dict.py [TEST_OPTION] [TEST_CORPUS]

    TEST_OPTION:
      -im  : Chinese->Kana using input method (default)
      -bt  : Chinese->Kana using buttons
      -rj  : Kana->Romaji

    TEST_CORPUS:
      data files in data/dict (lesson5.dat as default)
'''

BUTTON_COLUMNS = 11
TIMEOUT = 30

SUCCESS_COLOR = "red"
DEFAULT_COLOR = "black"
SUCCESS_FONT = "Fixsys 15 bold"
DEFAULT_FONT = "Fixsys 10"
DEFAULT_FONT_LARGE = "Fixsys 30"

class Util():
  kanas = {}
  @staticmethod
  def loadKanaDict(filepath):
    try:
      data = open(filepath, "rb").read()
    except IOError, message:
      print >> sys.stderr, "File could not be opened:", message
      sys.exit(1)
    data = data.decode("utf-8")
    records = data.splitlines(0)
    dic = {}
    for record in records:                # format each line
      fields = record.split()
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        Util.kanas[fields[0]] = fields[1]

  @staticmethod
  def generateProblem(kana):
    problem = ""
    for ch in kana:
      if not Util.isPunct(ch):
        problem += '__ '
      else:
        problem += ch + ' ' 
    return problem

  @staticmethod
  def isPunct(ch):
    return unicode(ch) in [u'，', u'。']

  @staticmethod
  def isTyoon(ch):
    return unicode(ch) in [u'ー']

  @staticmethod
  def isSokuon(ch):
    return unicode(ch) in [u'っ', u'ッ']

  @staticmethod
  def isYoon(ch):
    return unicode(ch) in [u'ゃ', u'ゅ', u'ょ', u'ャ', u'ュ', u'ョ']

  @staticmethod
  def addSolutionChar(problem, kana): 
    text = problem.replace("__", kana, 1)
    completed = (text.find("__ ") == -1)
    return (text, completed)

  @staticmethod
  def delSolutionChar(problem):
    text = problem
    pos = text.find("__ ")
    updated = (pos != 0)
    if pos == -1:
      text = text[:-2] + "__ "
    elif pos != 0:
      if Util.isPunct(text[pos-2:pos-1]):
        pos -= 2
      text = text[:pos-2] + "__ " + text[pos:]
    return (text, updated)

  @staticmethod
  def kanaToRomaji(kana):
    romaji = []
    repeat = False
    size = 0
    for ch in kana:
      if Util.isPunct(ch):
        romaji.append(" ")
      elif Util.isTyoon(ch):
        romaji.append("~")
      elif Util.isSokuon(ch):
        repeat = True
        romaji.append("z")
      elif Util.isYoon(ch):
        last = romaji[size - 1]
        if last == 'chi':
          romaji[size - 1] = 't'  # tya, tyu, tyo
        elif last == 'ji':
          romaji[size - 1] = 'z'  # zya, zyu, zyo
        else:
          romaji[size - 1] = last[:1]
        romaji.append(Util.kanas[ch])
      else:
        cur = Util.kanas[ch]
        if repeat:
          romaji[size - 1] = cur[:1]
          repeat = False
        romaji.append(cur)
      size += 1
    return ''.join(romaji)
 
  @staticmethod
  def matchRomaji(truth, test):
    if len(truth) != len(test):
      return False
    for (x, y) in zip(truth, test):
      if x == '~' and y in ['i', 'u', 'o']:
        continue
      if x != y:
        return False
    return True

  @staticmethod
  def matchKana(truth, test):
    return truth == test


class JLearner(Frame):
  def __init__(self, optionType='-im', dictFiles=[]):
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

    self.optionType = optionType
    self.dictFiles = dictFiles 
    self.row = 0
    self.key = "empty"
    self.alarm = None

    self.suggestText = StringVar()
    self.suggestText.set(self.key)
    suggestLabel = Label(self, textvariable = self.suggestText)
    suggestLabel["width"] = 20
    suggestLabel["height"] = 3
    suggestLabel["font"] = DEFAULT_FONT_LARGE
    suggestLabel.grid(row = self.row, rowspan = 2, columnspan=BUTTON_COLUMNS, sticky = W+E+N+S)
    self.row = self.row + 2;

    self.inputText = StringVar()
    #inputPane = Entry(self, textvariable = self.inputText)
    #inputPane["width"] = 10 
    #inputPane.grid(row = self.row, column = 1, columnspan = BUTTON_COLUMNS - 2, sticky = W+E+N+S)
    self.inputText.set(u"__ __ __ __ __ ， __ __ __ __ __ __ ")
    inputLabel = Label(self, textvariable = self.inputText)
    inputLabel["width"] = 25
    inputLabel["height"] = 1
    inputLabel.grid(row = self.row, rowspan = 2, columnspan = BUTTON_COLUMNS, sticky = W+E+N+S)

    self.row = self.row + 2;
    self.initButtons(r"data/kana/mixed.dat")
    Util.loadKanaDict(r"data/kana/mixed.dat")

    #if optionType == '-hr' or optionType == '-kr':
    #  self.inputText = StringVar()
    #inputPane.bind("<Return>", self.confirmKana)
    #inputPane.bind("<Escape>",self.cancel)
    #inputPane.focus_set()

    #  confirmButton = Button(self, text = "Confirm", width = 25)
    #  confirmButton.grid(row = self.row+5, column = 0, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)
    #  confirmButton["width"] = 10
    #  confirmButton.bind("<ButtonRelease>", self.confirmKana)

    #  cancelButton = Button(self, text = "Cancel")
    #  cancelButton.grid(row = self.row+5, column = BUTTON_COLUMNS/2+1, columnspan = BUTTON_COLUMNS/2, sticky = W+E+N+S)
    #  cancelButton["width"] = 10
    #  cancelButton.bind("<ButtonRelease>", self.cancel)

    # make second row/column expand
    self.rowconfigure(self.row, weight = 1)
    for i in range(0, BUTTON_COLUMNS):
      self.columnconfigure(i, weight = 1)
    self.next()

  def inputKana(self, event):
    kana = event.widget["text"]
    text = self.inputText.get()
    text, complete = Util.addSolutionChar(text, kana)
    self.inputText.set(text)
    if complete:
      newtext = text.replace(' ', '')
      print Util.kanaToRomaji(newtext)

  def deleteKana(self, event):
    text = self.inputText.get()
    text, update = Util.delSolutionChar(text)
    self.inputText.set(text)

  def next(self):
    return

  def cancel(self, event):
    self.quit()

  def initButtons(self, filename):
    try:
      data = open(filename, "rb").read()
    except IOError, message:
      print >> sys.stderr, "File could not be opened:", message
      sys.exit(1)
    data = data.decode("utf-8")
    records = data.splitlines(0)
    n = 0
    for record in records:                # format each line
      fields = record.split()
      button = Button(self, text = "  ")
      button["font"] = DEFAULT_FONT
      row = self.row + n / BUTTON_COLUMNS
      column = n % BUTTON_COLUMNS
      button.grid(row = row, column = column, sticky = W+E+N+S)
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        Util.generateProblem(fields[0])
        button["text"] = fields[0]
        button.bind("<ButtonRelease>", self.inputKana)
      n = n + 1
    button = Button(self, text = "⬅ BackSpace")
    button.grid(row = row + 1, column = 0, columnspan=4, sticky = W+E+N+S)
    button.bind("<ButtonRelease>", self.deleteKana);
    n = n + 1
    self.row += (n + BUTTON_COLUMNS - 1) / BUTTON_COLUMNS

def main(optionType, dictFiles):
  JLearner(optionType, dictFiles).mainloop()

if __name__ == "__main__":
  argv = sys.argv[1:]
  
  options = []
  files = []
  for x in argv:
    if x.find('-') != -1:
      options.append(x)
    else:
      files.append(x)

  option1 = set(options) & set(['-im', '-bt', '-rj'])
  option1 = list(option1)

  if options and not option1:
    print USAGE
    sys.exit(1)

  optionType = '-hr'
  dictFiles = ['data/dict/lesson5.dat']

  if option1:
    optionType = option1[0]

  main(optionType, dictFiles)
