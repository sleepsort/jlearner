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
      data files in data/dict (lesson09.dat as default)

    SPECIAL_OPTION:
      -m   : hide number of kanas
'''

COLUMNS = 11

FONT_BASE = "Fixsys"
#FONT_BASE = "DroidSansMono"

DEFAULT_FONT = "%s 15" % FONT_BASE
SUCCESS_FONT = "%s 15 bold" % FONT_BASE
FAIL_FONT    = "%s 15 bold" % FONT_BASE
DEFAULT_FONT_MIDDLE = "%s 13" % FONT_BASE
DEFAULT_FONT_LARGE  = "%s 15 bold" % FONT_BASE

DEFAULT_COLOR = "black"
SUCCESS_COLOR = "black"
FAIL_COLOR    = "red"

DEFAULT_KANA_PATH = r"data/kana/mixed.dat"

class Util():
  kanas = {}
  @staticmethod
  def load_kana_dict(filepath):
    try:
      data = open(filepath, "rb").read().decode("utf-8")
    except IOError, message:
      print >> sys.stderr, "Kana file could not be opened:", message
      sys.exit(1)
    records = data.splitlines(0)
    dic = {}
    for record in records:                # format each line
      fields = record.split()
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        Util.kanas[fields[0]] = fields[1]

  @staticmethod
  def generate_problem(kana, hide_length):
    problem = ""
    for idx, ch in enumerate(kana):
      if Util.ispunct(ch):
        problem += ch
      else:
        problem += "__"
      if (idx+1) % 10 == 0:
        problem += "\n"
      else:
        if hide_length:
          problem += "_"
        else:
          problem += " "
    return problem[:-1]

  @staticmethod
  def reformat(longstr):
    if not longstr:
      return longstr
    slice = [longstr[i:i+10] for i in range(0, len(longstr), 10)]
    return "\n".join(slice)

  @staticmethod
  def ispunct(ch):
    return unicode(ch) in u'，。〜'

  @staticmethod
  def istyoon(ch):
    return unicode(ch) in u'ー'

  @staticmethod
  def issokuon(ch):
    return unicode(ch) in u'っッ'

  @staticmethod
  def isyoon(ch):
    return unicode(ch) in u'ゃゅょャュョ'

  @staticmethod
  def add_solution_char(problem, kana):
    text = problem.replace("__", kana, 1)
    completed = (text.find("__") == -1)
    return (text, completed)

  @staticmethod
  def del_solution_char(problem):
    text = problem
    pos = text.find("__")
    updated = (pos != 0)
    if pos == -1:
      text = text[:-1] + "__"
    elif pos != 0:
      if Util.ispunct(text[pos-2:pos-1]):
        pos -= 2
      text = text[:pos-2] + "__" + text[pos-1:]
    return (text, updated)

  @staticmethod
  def kana_to_romaji(kana):
    romaji = []
    repeat = False
    for i, ch in enumerate(kana):
      if Util.ispunct(ch):
        romaji.append(" ")
      elif Util.istyoon(ch):
        romaji.append("-")
      elif Util.issokuon(ch):
        repeat = True
        romaji.append("z")
      elif Util.isyoon(ch):
        last = romaji[i - 1]
        if last == 'chi':
          romaji[i - 1] = 't'  # tya, tyu, tyo
        elif last == 'ji':
          romaji[i - 1] = 'z'  # zya, zyu, zyo
        else:
          romaji[i - 1] = last[:1]
        romaji.append(Util.kanas[ch])
      else:
        cur = Util.kanas[ch]
        if repeat:
          romaji[i - 1] = cur[:1]
          repeat = False
        romaji.append(cur)
    return ''.join(romaji)

  @staticmethod
  def match_romaji(truth, test):
    for noise in ',.~ \n\t':
      truth = truth.replace(noise, '')
      test = test.replace(noise, '')
    if len(truth) != len(test):
      return False
    for (x, y) in zip(truth, test):
      if x == '-' and y in '-aiueo':
        continue
      if x != y:
        return False
    return True

  @staticmethod
  def match_kana(truth, test):
    for noise in u'　，。〜 \n\t':
      truth = truth.replace(noise, '')
      test = test.replace(noise, '')
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
          data = open(self.files[self.filenum], 'rb').read().decode("utf-8")
        except IOError, message:
          print >> sys.stderr, "Dict file cound not be opened:", message
          sys.exit(1)
        self.pending = data.splitlines(0)
        if len(self.pending) <= 1 or self.pending[0].find("#DICT") == -1:
          self.linenum = len(self.pending)
          continue
        self.linenum = 1
      fields = self.pending[self.linenum].split()
      if len(fields) <= 2:
        #print >> sys.stderr, "Bogus line? %s" % fields
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
  def load_problem_dict(filepaths):
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
    for i, item in enumerate(oldlogs):
      oldlogs[i] = item.replace('\\', '/')
    oldlogs = set(oldlogs)
    oldlogs.remove(exclude)
    done = set()
    for name in oldlogs:
      data = open(name, 'rb').read().decode("utf-8")
      records = data.splitlines(0)
      if not records or records[0].find('#LOG') == -1:
        print >> sys.stderr,"%s isn't a valid log file, ignored!" % name
      else:
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
          passed, failed, key = int(line[0]), int(line[1]), line[2]
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
      flag, key = int(fields[0]), fields[1]
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
  def __init__(self, option_type, hide_length):
    self.option_type = option_type
    self.hide_length = hide_length
    self.pended = set(Dict.dicts.keys())
    self.failed = set()
    self.key  = None
    self.totalpass = 0
    self.totalfail = 0
    infix = option_type[1:]
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
      item = Dict.dicts[key]
      self.key = key
      return totalpass, total, Util.generate_problem(key, self.hide_length), item.chinese
    self.logger.merge()
    return totalpass, total, None, None

  def test(self, input):
    key, item = self.key, Dict.dicts[self.key]
    print item.kana, 
    if item.accent:
      print "(%s)" % item.accent,
    if item.kanji:
      print item.kanji,
    if self.option_type == '-im' and item.kanji:
      solution = item.kanji
    else:
      solution = key
    if item.romaji:
      fake = item.romaji
    else:
      fake = Util.kana_to_romaji(key)
    print fake,
    print "{%s}" % input
    success = Util.match_kana(solution, input)
    success = success or Util.match_romaji(fake, input)
    if success:
      self.totalpass += 1
      self.logger.write(1, key)
    else:
      self.totalfail += 1
      self.failed.add(key)
      self.logger.write(0, key)
    self.pended.remove(key)
    item = DictItem()
    item.copy(Dict.dicts[key])
    item.kana = Util.reformat(item.kana)
    item.kanji = Util.reformat(item.kanji)
    return item, success

  def stats(self):
    return self.totalpass, self.totalfail

class JLearner(Frame):
  def __init__(self, option1, option2, dict_files):
    """Create and grid several components into the frame"""
    Frame.__init__(self)

    Util.load_kana_dict(DEFAULT_KANA_PATH)
    Dict.load_problem_dict(dict_files)

    self.option_type = option1
    self.hide_length = option2
    self.dict_files = dict_files

    self.runner = Runner(option1, option2)

    # text variables that might be updated in real time
    self.active_text = {"kana" : StringVar(), "accent"  : StringVar(),
                        "misc" : StringVar(), "chinese" : StringVar(),
                       "input" : StringVar(), "counter" : StringVar()}

    # widgets that might change style in real time
    self.active_widgets = {"kana" : None, "misc"    : None,
                          "input" : None, "chinese" : None }
   
    self.init_widgets()

    self.lock = False
    # TODO: when dict is empty, without this we have problem
    # quit the program properly
    self.after(50, self.next)

  def init_widgets(self):
    self.bind_all("<Escape>", self.del_kana)
    self.pack(expand = NO, fill = BOTH)
    self.master.title("Japanese Learning")
    if self.option_type == '-im':
      self.master.geometry("350x200")
    else:
      self.master.geometry("350x800")
    self.master.rowconfigure(0, weight = 1)
    self.master.columnconfigure(0, weight = 1)
    self.grid(sticky = W+E+N+S)

    self.row = 0
    kana_pane = Label(self)
    kana_pane["textvariable"] = self.active_text["kana"]
    kana_pane["height"] = 2
    kana_pane["font"] = DEFAULT_FONT_LARGE
    pad_pane = Label(self)
    pad_pane["text"] = ""
    pad_pane["width"] = 2
    pad_pane.grid(row = self.row, rowspan = 2, column = 0, columnspan = 1)
    kana_pane.grid(row = self.row, rowspan = 2, column = 1, columnspan = COLUMNS - 2, sticky = W+E+N+S)
    accent_pane = Label(self)
    accent_pane["textvariable"] = self.active_text["accent"]
    accent_pane["width"] = 2
    accent_pane.grid(row = self.row, rowspan = 2, column = COLUMNS - 1, columnspan = 1)
    self.active_widgets["kana"] = kana_pane
    self.row += 2;

    misc_pane = Label(self)
    misc_pane["textvariable"] = self.active_text["misc"]
    misc_pane["height"] = 2
    misc_pane["font"] = DEFAULT_FONT_MIDDLE
    misc_pane.grid(row = self.row, rowspan = 2, columnspan = COLUMNS, sticky = W+E+N+S)
    self.active_widgets["misc"] = misc_pane
    self.row += 2;

    chinese_pane = Label(self)
    chinese_pane["textvariable"] = self.active_text["chinese"]
    chinese_pane["height"] = 2
    chinese_pane["font"] = DEFAULT_FONT_MIDDLE
    chinese_pane.grid(row = self.row, rowspan = 2, columnspan = COLUMNS, sticky = W+E+N+S)
    self.active_widgets["chinese"] = chinese_pane
    self.row += 2;

    counter_pane = Label(self)
    counter_pane["textvariable"] = self.active_text["counter"]
    if self.option_type == '-im':
      input_pane = Entry(self)
      input_pane["textvariable"] = self.active_text["input"]
      input_pane.grid(row = self.row, column = 1, columnspan = COLUMNS - 2, sticky = W+E+N+S)
      input_pane.focus_set()
      input_pane.bind("<Return>", self.test)
      confirm_button = Button(self)
      confirm_button["text"] = "ok"
      confirm_button["width"] = 1
      confirm_button.bind("<ButtonRelease>", self.test)
      confirm_button.grid(row = self.row + 1, column = COLUMNS - 2, columnspan = 1, sticky = W+E+N+S)
      counter_pane.grid(row = self.row + 1, columnspan = 3, column = 1, sticky = W+E+N+S)
      self.row = self.row + 2;
    else:
      input_pane = Label(self)
      input_pane["textvariable"] = self.active_text["kana"]
      input_pane.focus_set()
      self.init_buttons()
      counter_pane.grid(row = self.row, columnspan = 3, column = COLUMNS - 3)
    self.active_widgets["input"] = input_pane

    self.rowconfigure(self.row, weight = 1)
    for i in range(0, COLUMNS):
      self.columnconfigure(i, weight = 1)

  def test(self, event):
    if self.lock:
      return
    self.lock = True
    item, success = self.runner.test(self.active_text["input"].get())
    kana = item.kana
    misc = " [%s]" % item.kanji if item.kanji else ""
    accent = "%s" % item.accent if item.accent else ""
    self.active_text["kana"].set(kana)
    self.active_text["misc"].set(misc)
    self.active_text["accent"].set(accent)
    if success:
      self.active_widgets["kana"]["foreground"] = SUCCESS_COLOR
      self.active_widgets["kana"]["font"] = SUCCESS_FONT
      self.active_widgets["misc"]["foreground"] = SUCCESS_COLOR
      self.active_widgets["misc"]["font"] = SUCCESS_FONT
      self.active_widgets["input"]["state"] = 'disabled'
      self.after(800, self.next)
    else:
      if not item.kanji:
        self.active_widgets["kana"]["foreground"] = FAIL_COLOR
        self.active_widgets["kana"]["font"] = FAIL_FONT
      else:
        self.active_widgets["misc"]["foreground"] = FAIL_COLOR
        self.active_widgets["misc"]["font"] = FAIL_FONT
      self.active_widgets["input"]["state"] = 'disabled'
      self.after(4000, self.next)

  def add_kana(self, event):
    if not self.lock:
      kana = event.widget["text"]
      text = self.active_text["kana"].get()
      text, complete = Util.add_solution_char(text, kana)
      self.active_text["kana"].set(text)
      if complete:
        newtext = text.replace(' ', '')
        self.active_text["input"].set(newtext)
        self.test(event)

  def del_kana(self, event):
    if not self.lock:
      text = self.active_text["kana"].get()
      text, update = Util.del_solution_char(text)
      self.active_text["kana"].set(text)

  def next(self):
    self.lock = False
    passed, total, hint, problem = self.runner.next()
    if problem:
      self.active_text["kana"].set(hint)
      self.active_text["misc"].set("")
      self.active_text["accent"].set("")
      self.active_text["chinese"].set(problem)
      self.active_text["counter"].set("%d / %d" % (passed, total))
      self.active_text["input"].set("")
      self.active_widgets["kana"]["foreground"] = DEFAULT_COLOR
      self.active_widgets["kana"]["font"] = DEFAULT_FONT
      self.active_widgets["misc"]["foreground"] = DEFAULT_COLOR
      self.active_widgets["misc"]["font"] = DEFAULT_FONT
      self.active_widgets["input"]["state"] = 'normal'
    else:
      passed, failed = self.runner.stats()
      info = "Well done!\n\n"
      info += "Result:\n"
      info += "  pass: %d  fail: %d\n" % (passed, failed)
      showinfo("Message", info)
      self.quit()

  def init_buttons(self):
    try:
      data = open(DEFAULT_KANA_PATH, "rb").read().decode("utf-8")
    except IOError, message:
      print >> sys.stderr, "Kana file could not be opened:", message
      sys.exit(1)
    records = data.splitlines(0)
    row = self.row
    for i, record in enumerate(records):
      fields = record.split()
      button = Button(self, text = "  ")
      button["font"] = DEFAULT_FONT_MIDDLE
      row = self.row + i / COLUMNS
      column = i % COLUMNS
      button.grid(row = row, column = column, sticky = W+E+N+S)
      if fields and fields[0][0] != '#':  # ignore lines with heading '#'
        button["text"] = fields[0]
        button.bind("<ButtonRelease>", self.add_kana)
    del_button = Button(self)
    del_button["text"] = "<- BackSpace(ESC)"
    del_button.grid(row = row + 1, column = 0, columnspan = 5)
    del_button.bind("<ButtonRelease>", self.del_kana);
    self.row += (len(records) + COLUMNS - 1) / COLUMNS

def main(option_type1, option_type2, dict_files):
  JLearner(option_type1, option_type2, dict_files).mainloop()

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
  option2 = set(options) & set(['-m'])
  option2 = list(option2)

  if options and not option1 and not option2:
    print USAGE
    sys.exit(1)

  option_type1 = '-im'
  option_type2 = ''
  dict_files = ['data/dict/lesson09.dat']

  if option1:
    option_type1 = option1[0]
  if option2:
    option_type2 = option2[0]
  if files:
    dict_files = files

  main(option_type1, option_type2, dict_files)
