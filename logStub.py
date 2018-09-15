#!/usr/bin/env python3
import sys,time

#Модуль для логирования. По сути нужен для глобального изменения направления выхлопа

def ttt():
	return time.strftime("[%H:%M:%S]: ")

lastMessage=""

def logD(m):
	global lastMessage
	if(type(m)!=str):m=str(m)
	lastMessage=m
	sys.stderr.write(ttt()+m+'\n')

#При необходимости функцию можно переопределить. Например, для веб-сервера на Desktop
