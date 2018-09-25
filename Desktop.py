#!/usr/bin/env python3
from logStub import logD
import sys,os,threading

logsarr=[]

from web import server

def startGUI():
	os.system('xdg-open "web/index.html" 2>/dev/null')
	t = threading.Thread(target=server.mainloop)
	t.daemon = True
	t.start()
	server.answer="hideSplash();"

startGUI()

import DialogManager as dm

from DesktopFeatures.SoundRecognize import parser
parser.sphinxcmd='pocketsphinx_continuous -inmic yes -hmm DesktopFeatures/SoundRecognize/zero_ru.cd_cont_4000 -dict DesktopFeatures/SoundRecognize/ru-kurisu.dic -lm DesktopFeatures/SoundRecognize/ru-kurisu-min.lm -samprate 16000 -logfn /dev/null'#Патчим свой же модуль. shrug


logD("Loaded!")

import APIkeys,urllib.request
#https://tech.yandex.ru/speechkit/cloud/ -- Yandex Speech Kit Tecnology
def say(msg,voice="jane",emotion="neutral",speed=1):
	global logsarr
	logsarr.append("Kurisu: "+msg)
	if(len(logsarr)>25):logsarr=logsarr[-25:]
	server.answer="hideSplash();startSay();try{setLogs("+str(logsarr)+");}catch(e){console.log(e);}"
	try:
		msg=msg.replace("мадей","мадэй")
		msg=msg.replace("акисэ","акисэ+")
		msg=msg.replace("ИИ","И.И.")
		url="https://tts.voicetech.yandex.net/generate?key="+APIkeys.YandexSpeechKit+"&text"+urllib.parse.urlencode([("",msg)])+"&format=wav&lang=ru-RU&speaker="+voice+"&speed="+str(speed)+"&emotion="+emotion
		os.system("wget \""+url+"\" -O /tmp/yandexspeech.wav 2>/dev/null")
		os.system("play /tmp/yandexspeech.wav speed 1.1 2>/dev/null")
	except Exception as e:
		logD(e)
		os.system('espeak -vru+f1 -s 160 "'+msg.replace("\""," ")+'" 2>/dev/null')
	server.answer="stopSay();try{setLogs("+str(logsarr)+");}catch(e){console.log(e);}"


#Простейший способ вызвать диалог в терминале
def sendfun(msg,ident):
	if(len(msg)<3):msg=msg+"  "
	sys.stdout.write('\r\033[1;33mKurisu\033[0m: '+msg+'\n')
	say(msg)
	parser.isGetSpeech=True
	

def typfun(ident):
	sys.stdout.write("typing...")

dm.dialAdapters.append(dm.pa.getAnswerByFile("data/trubot.preprocessed"))#Угарать))))

d=dm.Dialog(sendfunction=sendfun,typefunction=typfun)
d.timePar0=0.01
d.timePar1=0

def onSpeechRec(s):
	global logsarr
	logD("Text: "+s)
	try:
		logsarr.append("You: "+s)
		if(len(logsarr)>25):logsarr=logsarr[-25:]
		sys.stdout.write('\r\033[1;33mYou\033[0m: '+s+'\n')
		s=s.replace("amadeus","амадеус").replace("kurisu","Курису")
		isPriv=(s.count("урису")+s.count("акис")+s.lower().count("ассистент")+s.count("мадей")+s.count("мадеус")+s.count("ристина")>0)
		d.getAnswer(s,isPrivate=True)
	except Exception as e:
		logD(e)

parser.onSpeech=onSpeechRec
try:
	#parser.mainloop()
	parser.mainloopAgressive()
except KeyboardInterrupt:
	d.localdial.updateSource()
