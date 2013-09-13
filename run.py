#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import random
import operator
import sys
import codecs
import copy

COLUMNS_OF_BUTTONS=5
dic={}
class Japanese_Learning( Frame ):
  def __init__( self):
    """Create and grid several components into the frame"""
    Frame.__init__( self )
    self.pack( expand = NO, fill = BOTH )
    self.master.title( "Japanese Learning" )
    self.master.geometry( "300x700" )

    # main frame fills entire container, expands if necessary
    self.master.rowconfigure( 0, weight = 1 )
    self.master.columnconfigure( 0, weight = 1 )
    self.grid( sticky = W+E+N+S )

    self.wrong=IntVar()
    self.right=IntVar()
    self.dic={}

    self.button=[]
    self.buttonIndex={}
    self.maxrow=0
    
    #self.initializeData(r"data/hiragana.dat")
    self.initializeData(r"data/katakana.dat")
    self.dic=copy.deepcopy(dic)
    self.resultText=StringVar()
    self.suggestLabel = Label(self, textvariable = self.resultText)
    self.suggestLabel["width"]=20
    self.suggestLabel["height"]=3
    self.suggestLabel["font"]="Fixsys 30"
    self.suggestLabel.grid( rowspan = 2, columnspan=COLUMNS_OF_BUTTONS,sticky = W+E+N+S )
    
    x=u"Romanization:"
    x=x.encode( "utf-8" )
    self.label1=Label(self,text=x)
    self.label1["width"]=10
    self.label1["height"]=1
    self.label1.grid(row=self.maxrow+3,column=0,columnspan=COLUMNS_OF_BUTTONS/2,sticky = W+E+N+S)

    self.inputText = Entry(self)
    self.inputText["width"]=10
    self.inputText.grid( row=self.maxrow+3, column=COLUMNS_OF_BUTTONS/2+1,columnspan=COLUMNS_OF_BUTTONS/2,sticky = W+E+N+S )
    self.inputText.bind("<Return>", self.checkResult)
    self.inputText.bind("<Escape>",self.cancel)

    self.confirmButton = Button( self, text = "Confirm", 
      width = 25 )
    self.confirmButton.grid( row = self.maxrow+5,column=0,columnspan=COLUMNS_OF_BUTTONS/2,sticky = W+E+N+S )
    self.confirmButton["width"]=10
    self.confirmButton.bind("<ButtonRelease>", self.checkResult)

    self.cancelButton = Button( self, text = "Cancel" )
    self.cancelButton.grid( row = self.maxrow+5, column=COLUMNS_OF_BUTTONS/2+1,columnspan=COLUMNS_OF_BUTTONS/2,sticky = W+E+N+S )
    self.cancelButton["width"]=10
    self.cancelButton.bind("<ButtonRelease>", self.cancel)

    # make second row/column expand
    self.rowconfigure( self.maxrow+1, weight = 1 )
    for i in range(0,COLUMNS_OF_BUTTONS):
      self.columnconfigure( i, weight = 1 )
    self.getMessage()
    
  def checkResult(self,event):
    self.input=self.inputText.get()
    if(self.element=="empty"):
      return
    if(self.input != self.dic[self.element]):
      showinfo("Message", u"No no no\n"+self.element+":"+self.dic[self.element])
      self.wrong=self.wrong+1
    else:
      showinfo("Message", u"Right!")
      self.right=self.right+1
      self.button[self.buttonIndex[self.element]]["foreground"]="red"
      self.button[self.buttonIndex[self.element]]["font"]+=" bold"
      del self.dic[self.element]
    self.inputText.delete(0,len(self.input))
    self.getMessage()
    #print str(self.right)+":"+str(len( self.dic ))
    if (len(self.dic)==0):
      showinfo("Message", u"Complete!\n"+"Result:\t"+
          "Right Answer:\t"+str(self.right)+"\n"+"\t"
          "Wrong Answer:\t"+str(self.wrong))
      self.quit()
  def cancel(self,event):
    self.quit()
  def getMessage(self):
    if(len( self.dic )):
      i=random.randrange( 1, len( self.dic )+1)
      self.element=self.getElement(i)
      self.resultText.set(self.element)
    else:
      self.element="empty"
  def getElement(self,n):
    iter=self.dic.__iter__()
    element=StringVar()
    while(n):
      element=iter.next()
      n=n-1
    return element
  def initializeData(self,filename):
    self.wrong=0
    self.right=0
    try:
      file = open( filename, "rb" ).read()  # open file in write mode
    except IOError, message:                # file open failed
      print >> sys.stderr, "File could not be opened:", message
      sys.exit( 1 )
    if file[:3] == codecs.BOM_UTF8:         # first weird char in utf-8 file
      file = file[3:]
    file=file.decode("utf-8")
    records=file.splitlines(0)
    i=len(self.button)
    for record in records:                  # format each line
      fields = record.split()
      if (len(fields)!=0):
        dic[fields[0]]=fields[1]
        self.button.append(Button(self,text = fields[0]))
        self.buttonIndex[fields[0]]=i
        self.button[i].bind("<ButtonRelease>", self.retryWord)
      else:
        self.button.append(Button(self,text = "  "))
      self.button[i].grid(row=self.maxrow+i/COLUMNS_OF_BUTTONS,column=operator.mod(i,COLUMNS_OF_BUTTONS),sticky=W+E+N+S)
      self.button[i]["font"]="Fixsys 15"
      
      i=i+1
    self.maxrow+=(i+COLUMNS_OF_BUTTONS-1)/COLUMNS_OF_BUTTONS
  def retryWord(self,event):
    event.widget["foreground"]="black"
    event.widget["font"]="Fixsys 15"
    #print event.widget["text"]
    self.dic[event.widget["text"]]=dic[event.widget["text"]]
def main():
  Japanese_Learning().mainloop()   
if __name__ == "__main__":
  main()
