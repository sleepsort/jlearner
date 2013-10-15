#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import random
import sys
import os
import glob

USAGE= '''
  usage:
    ./dict.py [TEST_OPTION] [TEST_CORPUS]

    TEST_OPTION:
      -im  : Chinese->Kana using input method (default)
      -bt  : Chinese->Kana using buttons

    TEST_CORPUS:
      data files in data/dict (lesson06.dat as default)
'''

BUTTON_COLUMNS = 11

DEFAULT_COLOR = "black"
SUCCESS_COLOR = "black"
FAIL_COLOR = "red"
FONT_BASE = "Fixsys"
#FONT_BASE = "AdobeFangsongStd"
#FONT_BASE = "AdobeHeitiStd"
#FONT_BASE = "AdobeSongStd"
#FONT_BASE = "DroidSansMono"
#FONT_BASE = "Times"
DEFAULT_FONT = "%s 15" % FONT_BASE
SUCCESS_FONT = "%s 15 bold" % FONT_BASE
FAIL_FONT = "%s 15 bold" % FONT_BASE
DEFAULT_FONT_MIDDLE = "%s 10" % FONT_BASE
DEFAULT_FONT_LARGE = "%s 15 bold" % FONT_BASE

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
    problem = "__"
    cnt = 1 
    for ch in kana[1:]:
      if cnt == 10:
        problem += "\n"
        cnt = 0
      else:
        problem += " "
      if not Util.isPunct(ch):
        problem += "__"
      else:
        problem += ch
      cnt += 1
    return problem

  @staticmethod
  def reformat(longstr):
    if not longstr:
      return longstr
    changed = ""
    cnt = 0
    for ch in longstr:
      if cnt == 10:
        changed += "\n"
        cnt = 0
      changed += ch
      cnt += 1
    return changed

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
    completed = (text.find("__") == -1)
    return (text, completed)

  @staticmethod
  def delSolutionChar(problem):
    text = problem
    pos = text.find("__")
    updated = (pos != 0)
    if pos == -1:
      text = text[:-1] + "__"
    elif pos != 0:
      if Util.isPunct(text[pos-2:pos-1]):
        pos -= 2
      text = text[:pos-2] + "__" + text[pos-1:]
    print text
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
    truth = truth.replace(u'　', '')
    truth = truth.replace(u'，', '')
    truth = truth.replace(u'。', '')
    truth = truth.replace(u' ', '')
    test = test.replace(u'　', '')
    test = test.replace(u'，', '')
    test = test.replace(u'。', '')
    test = test.replace(u' ', '')
    return truth == test 

class DictProcessor():
  def __init__(self, filepaths):
    self.files = filepaths
    self.pending = []
    self.filenum = -1 
    self.linenum = -1 

  def readline(self):
    while True:
      self.linenum += 1
      if self.linenum >= len(self.pending):
        self.filenum += 1
        if self.filenum >= len(self.files):
          return None
        try:
          data = open(self.files[self.filenum], 'rb').read()
        except IOError, message:
          print >> sys.stderr, "File cound not be opened:", message
          sys.exit(1)
        data = data.decode("utf-8")
        self.pending = data.splitlines(0)
        if len(self.pending) <= 1 or self.pending[0].find("#DICT") == -1:
          self.linenum = len(self.pending)
          continue 
        self.linenum = 1
      fields = self.pending[self.linenum].split()
      if len(fields) <= 2:
        print >> sys.stderr, "bogus line? %s" % fields
        continue
      return fields

class DictItem(object):
  def __init__(self, kana=None, accent=None, kanji=None, romaji=None, chinese=None):
    self.kana = kana
    self.accent = accent
    self.kanji = kanji
    self.romaji = romaji
    self.chinese = chinese

  def copy(self, other):
    self.kana = other.kana
    self.accent = other.accent
    self.kanji = other.kanji
    self.romaji = other.romaji
    self.chinese = other.chinese

class Dict():
  dicts = {}

  @staticmethod
  def loadProblemDict(filepaths):
    processor = DictProcessor(filepaths)
    line = processor.readline()
    while line:
      accent, kana, kanji, romaji, chinese = [None] * 5
      accent = line[0]
      kana = line[1]
      what = line[2]
      if what[0] == '[' and what[-1] == ']':
        kanji = what
      elif what[0] == '<' and what[-1] == '>':
        romaji = what
      if len(line) > 3:
        what = line[3]
        if what[0] == '<' and what[-1] == '>':
          romaji = what
      chinese = set(line) - set((accent, kana, kanji, romaji))
      chinese = ' '.join(list(chinese))
      if accent == '?':
        accent = None 
      if kanji:
        kanji = kanji[1:-1]
      if romaji:
        romaji = romaji[1:-1]
      Dict.dicts[kana] = DictItem(kana, accent, kanji, romaji, chinese)
      line = processor.readline()

class Logger(object):
  def __init__(self, infix):
    self.id = os.getpid()
    self.infix = infix
    self.filename = 'log/dict.%s.%d.tmp' % (infix, self.id);
    self.file = open(self.filename, 'w', 0)
    print >> self.file, "#LOG <flag> <key>"
    self.done = self.cleanup(self.filename)

  def cleanup(self, exclude):
    oldlogs = glob.glob("log/dict.%s.*.tmp" % self.infix)
    for index, item in enumerate(oldlogs):
      oldlogs[index] = item.replace('\\', '/')
    oldlogs = set(oldlogs)
    oldlogs.remove(exclude)
    done = set()
    for name in oldlogs:
      data = open(name, 'rb').read()
      data = data.decode("utf-8")
      records = data.splitlines(0)
      if not records or records[0].find('#LOG') == -1:
        print >> sys.stderr,"%s isn't a valid log file, ignored!" % name
        continue
      for line in records[1:]:
        line = line.strip()
        print >> self.file, line.encode('utf-8')
        fields = line.split()
        if fields[0] == '1':  # ignore passed items
          done.add(fields[1])
      os.remove(name)
    return done

  def write(self, flag, key):
    info = "%s %s" % (flag, key)
    print >> self.file, info.encode('utf-8')

  def merge(self):
    if self.file:
      self.file.close()
    collect = {}
    try:
      file = open('log/dict.%s.dat' % self.infix, 'rb')
      if file.readline().find('#LOG') == -1:
        print >> sys.stderr, "Previous log file invalid"
        file.close()
      else:
        for line in file:
          line = line.strip().split()
          passed, failed = int(line[0]), int(line[1])
          key = line[2]
          if key not in collect:
            collect[key] = [passed, failed]
          else:
            collect[key][0] += passed
            collect[key][1] += failed
        file.close()
    except IOError, message:
      print >> sys.stderr, "File could not be opened:", message
    newdata = open(self.filename, 'r')
    newdata.readline()
    for record in newdata:
      fields = record.split()
      flag = int(fields[0])
      key = fields[1]
      if key not in collect:
        collect[key] = [0, 0]
      if flag == 0:
        collect[key][1] += 1
      else:
        collect[key][0] += 1
    newdata.close()
    file = open('log/dict.%s.dat' % self.infix, 'w', 0)
    print >> file, "#LOG <pass> <fail> <key>"

    for key in sorted(collect.iterkeys()):
      val = collect[key]
      info = "%3d %3d   %s" % (val[0], val[1], key)
      print >> file, info
    file.close()
    os.remove(self.filename)


class Runner(object):
  def __init__(self, optionType):
    self.optionType = optionType
    self.pended = set(Dict.dicts.keys())
    self.failed = set()
    self.key  = None
    self.item = None
    self.totalpass = 0
    self.totalfail = 0
    infix = optionType[1:]
    self.logger = Logger(infix)
    self.pended = self.pended - self.logger.done

  def next(self):
    if not self.pended and self.failed:
      self.pended = self.failed
      self.failed = set()
    totalpass = self.totalpass
    total = totalpass + len(self.failed) + len(self.pended)
    if self.pended:
      key = random.sample(self.pended, 1)[0]
      self.item = Dict.dicts[key]
      self.key = key
      return totalpass, total, Util.generateProblem(key), self.item.chinese
    self.logger.merge() 
    return totalpass, total, None, None

  def testMatch(self, input):
    key, item = self.key, self.item
    if self.optionType == '-im' and item.kanji:
      solution = item.kanji
    else:
      solution = key
    if Util.matchKana(solution, input):
      success = True
      self.totalpass += 1
      self.logger.write(1, key)
    else:
      success = False
      self.totalfail += 1
      self.failed.add(key)
      self.logger.write(0, key)
    self.pended.remove(key)
    item = DictItem()
    item.copy(self.item)
    item.kana = Util.reformat(item.kana)
    item.kanji = Util.reformat(item.kanji)
    return item, success

  def stats(self):
    return self.totalpass, self.totalfail

class JLearner(Frame):
  def __init__(self, optionType='-im', dictFiles=[]):
    """Create and grid several components into the frame"""
    Frame.__init__(self)

    self.bind_all("<Escape>", self.deleteKana)
    self.pack(expand = NO, fill = BOTH)
    self.master.title("Japanese Learning")
    if optionType == '-im':
      self.master.geometry("300x200")
    else:
      self.master.geometry("350x700")
    self.master.rowconfigure(0, weight = 1)
    self.master.columnconfigure(0, weight = 1)
    self.grid(sticky = W+E+N+S)
    self.lock = False

    Util.loadKanaDict(r"data/kana/mixed.dat")
    Dict.loadProblemDict(dictFiles)

    self.runner = Runner(optionType)
    self.activeText = {"kana" : StringVar(), "accent"  : StringVar(), 
                       "misc" : StringVar(), "chinese" : StringVar(), 
                      "input" : StringVar(), "counter" : StringVar() }
    self.activeWidgets = {}

    self.row = 0
    KanaPane = Label(self)
    KanaPane["textvariable"] = self.activeText["kana"]
    KanaPane["height"] = 2
    KanaPane["font"] = DEFAULT_FONT_LARGE
    PadPane = Label(self)
    PadPane["text"] = ""
    PadPane["width"] = 2 
    PadPane.grid(row = self.row, rowspan = 2, column = 0, columnspan = 1)
    KanaPane.grid(row = self.row, rowspan = 2, column = 1, columnspan = BUTTON_COLUMNS - 2, sticky = W+E+N+S)
    AccentPane = Label(self)
    AccentPane["textvariable"] = self.activeText["accent"]
    AccentPane["width"] = 2 
    AccentPane.grid(row = self.row, rowspan = 2, column = BUTTON_COLUMNS - 1, columnspan = 1)
    self.activeWidgets["kana"] = KanaPane
    self.row += 2;

    MiscPane = Label(self)
    MiscPane["textvariable"] = self.activeText["misc"]
    MiscPane["height"] = 2
    MiscPane["font"] = DEFAULT_FONT_MIDDLE
    MiscPane.grid(row = self.row, rowspan = 2, columnspan=BUTTON_COLUMNS, sticky = W+E+N+S)
    self.activeWidgets["misc"] = MiscPane
    self.row += 2;

    ChinesePane = Label(self)
    ChinesePane["textvariable"] = self.activeText["chinese"]
    ChinesePane["height"] = 2
    ChinesePane["font"] = DEFAULT_FONT_MIDDLE
    ChinesePane.grid(row = self.row, rowspan = 2, columnspan=BUTTON_COLUMNS, sticky = W+E+N+S)
    self.activeWidgets["chinese"] = ChinesePane
    self.row += 2;

    CounterPane = Label(self)
    CounterPane["textvariable"] = self.activeText["counter"]
    if optionType == '-im':
      InputPane = Entry(self)
      InputPane["textvariable"] = self.activeText["input"]
      InputPane.grid(row = self.row, column = 1, columnspan = BUTTON_COLUMNS - 2, sticky = W+E+N+S)
      InputPane.focus_set()
      InputPane.bind("<Return>", self.testMatch)
      ConfirmButton = Button(self)
      ConfirmButton["text"] = "ok"
      ConfirmButton["width"] = 1
      ConfirmButton.bind("<ButtonRelease>", self.testMatch)
      ConfirmButton.grid(row = self.row + 1, column = BUTTON_COLUMNS - 2, columnspan = 1, sticky = W+E+N+S)
      CounterPane.grid(row = self.row + 1, columnspan = 3, column = 1, sticky = W+E+N+S)
      self.row = self.row + 2;
    else:
      InputPane = Label(self)
      InputPane["textvariable"] = self.activeText["kana"]
      InputPane.focus_set()
      self.initButtons(r"data/kana/mixed.dat")
      CounterPane.grid(row = self.row, columnspan = 3, column = BUTTON_COLUMNS - 3)
    self.activeWidgets["input"] = InputPane

    self.rowconfigure(self.row, weight = 1)
    for i in range(0, BUTTON_COLUMNS):
      self.columnconfigure(i, weight = 1)
    # TODO: when dict is empty, without this we have problem
    # quit the program properly
    self.after(50, self.next) 

  def testMatch(self, event):
    item, success = self.runner.testMatch(self.activeText["input"].get())
    kana = item.kana
    accent = ""
    misc = ""
    if item.kanji:
      misc = " [%s]" % item.kanji
    if item.accent:
      accent = "%s" % item.accent
    self.activeText["kana"].set(kana)
    self.activeText["misc"].set(misc)
    self.activeText["accent"].set(accent)
    if success:
      self.activeWidgets["kana"]["foreground"] = SUCCESS_COLOR
      self.activeWidgets["kana"]["font"] = SUCCESS_FONT
      self.activeWidgets["misc"]["foreground"] = SUCCESS_COLOR
      self.activeWidgets["misc"]["font"] = SUCCESS_FONT
      self.activeWidgets["input"]["state"] = 'disabled'
      self.lock = True
      self.after(800, self.next)
    else:
      if not item.kanji:
        self.activeWidgets["kana"]["foreground"] = FAIL_COLOR
        self.activeWidgets["kana"]["font"] = FAIL_FONT
      else:
        self.activeWidgets["misc"]["foreground"] = FAIL_COLOR
        self.activeWidgets["misc"]["font"] = FAIL_FONT
      self.activeWidgets["input"]["state"] = 'disabled'
      self.lock = True
      self.after(2000, self.next)

  def inputKana(self, event):
    if not self.lock:
      kana = event.widget["text"]
      text = self.activeText["kana"].get()
      text, complete = Util.addSolutionChar(text, kana)
      self.activeText["kana"].set(text)
      if complete:
        newtext = text.replace(' ', '')
        self.activeText["input"].set(newtext)
        self.testMatch(event)

  def deleteKana(self, event):
    if not self.lock:
      text = self.activeText["kana"].get()
      text, update = Util.delSolutionChar(text)
      self.activeText["kana"].set(text)

  def next(self):
    self.lock = False
    passed, total, hint, problem = self.runner.next()
    if problem:
      self.activeText["kana"].set(hint)
      self.activeText["misc"].set("")
      self.activeText["accent"].set("")
      self.activeText["chinese"].set(problem)
      self.activeText["counter"].set("%d / %d" % (passed, total))
      self.activeText["input"].set("")
      self.activeWidgets["kana"]["foreground"] = DEFAULT_COLOR
      self.activeWidgets["kana"]["font"] = DEFAULT_FONT
      self.activeWidgets["misc"]["foreground"] = DEFAULT_COLOR
      self.activeWidgets["misc"]["font"] = DEFAULT_FONT
      self.activeWidgets["input"]["state"] = 'normal'
    else:
      passed, failed = self.runner.stats()
      info = "Well done!\n\n"
      info += "Result:\n"
      info += "  pass: %d  fail: %d\n" % (passed, failed)
      showinfo("Message", info)
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
      button["font"] = DEFAULT_FONT_MIDDLE
      row = self.row + n / BUTTON_COLUMNS
      column = n % BUTTON_COLUMNS
      button.grid(row = row, column = column, sticky = W+E+N+S)
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        Util.generateProblem(fields[0])
        button["text"] = fields[0]
        button.bind("<ButtonRelease>", self.inputKana)
      n = n + 1
    button = Button(self, text = "⬅ BackSpace")
    button.grid(row = row + 1, column = 0, columnspan=4)
    button.bind("<ButtonRelease>", self.deleteKana);
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

  option1 = set(options) & set(['-im', '-bt'])
  option1 = list(option1)

  if options and not option1:
    print USAGE
    sys.exit(1)

  optionType = '-im'
  dictFiles = ['data/dict/lesson06.dat']

  if option1:
    optionType = option1[0]
  if files:
    dictFiles = files

  main(optionType, dictFiles)
