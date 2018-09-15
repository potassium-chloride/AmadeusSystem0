#!/usr/bin/env python3
import DialogManager as dm
from logStub import logD
import sys

logD("Loaded!")

#Простейший способ вызвать диалог в терминале
def sendfun(msg,ident):
	if(len(msg)<3):msg=msg+"  "
	sys.stdout.write('\r\033[1;33mKurisu\033[0m: '+msg+'\n')

def typfun(ident):
	sys.stdout.write("typing...")

d=dm.Dialog(sendfunction=sendfun,typefunction=typfun)

while(True):
	try:
		usermsg=input("\n\033[1;33mYou\033[0m: ")
		d.getAnswer(usermsg)
	except KeyboardInterrupt:
		print("Exit")
		sys.exit(0)
