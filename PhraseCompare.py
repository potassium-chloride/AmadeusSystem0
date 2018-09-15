#!/usr/bin/env python3
import time,utils,subprocess,sys,json,random,re

#Тут реализуем объект, который по заданной последовательности сообщений ищет наиболее подходящий ответ
'''Пусть дан файл с последовательностью сообщений следующего формата:

...
Привет/pause Как дела?
Нормально
Что нового?

Что делаешь?
Статью читаю
...

/pause -- разные сообщения
\n -- перевод строки, экранируется перед записью в файл
/type -- отправить статус о наборе сообщения, но ничего не отправлять. Скорее всего, будет добавляться в диалог вручную
Пустая строка -- обрыв диалога, не учитывается

Задача: быстро и эффективно искать совпадения в диалогах и выдать наиболее подходящий ответ
'''

def compareWords(w1,w2):#Да, *****, ещё одна!
	if(w1['word']==w2['word']):return 1.0#Точное совпадение
	if(w1['startform']==w2['startform']):return 0.9
	mans=1.0
	l1=len(w1['syns'])
	l2=len(w2['syns'])
	for i in range(l1):
		if(w1['syns'][i]==w2['word']):
			mans=0.85-0.1*i
			l2=min(l2,i)
			break
	for i in range(l2):
		if(w2['syns'][i]==w1['word']):
			return 0.85-0.1*i
	if(mans<1):return mans
	if(w1['root']==w2['root']):return 0.04
	return 0#Связи не найдено

compPhrasesParam1=1.4#Подгоночный параметр

reglink=re.compile("([\w0-9]+\.[\w0-9]+){1,4}")#Example: html5pattern.com

class dialline():
	orig=""
	words=[]#Это массив dict
	def __init__(self,s):#Из строки с нуля
		global reglink
		if(type(s)==str):
			self.orig=s
			if(len(self.orig)>0 and self.orig[-1]=='\n'):self.orig=self.orig[:-1]
			self.words=[].copy()
			self.tokenizedwords=[].copy()
			arr=utils.str2arr(s)
			links=re.findall(reglink,s)
			for i in arr:
				d={}
				tmpl=""
				for link in links:
					if(link.count(i)>0):
						tmpl=link
						break
				if(tmpl!=""):#Для ссылок несколько иная обработка
					d['word']=tmpl
					d['startform']=tmpl
					d['root']=tmpl
					d['semload']=utils.getSemanticLoad_low(tmpl)
					d['syns']=""
					self.words.append(d)
					continue
				d['word']=i
				d['startform']=utils.getStartForm(i)
				inf=utils.wordInfo(i)
				d['root']=inf['root']
				d['semload']=utils.getSemanticLoad_low(i)
				if(inf['parts'].count('|гл|')>0):d['semload']*=1.1
				if(inf['parts'].count('|мест|')+inf['parts'].count('|числ|')>0):d['semload']*=0.9
				d['syns']=inf['syns']
				self.words.append(d)
		elif(type(s)==dict):#Из сохранённого
			self.orig=s['orig']
			if(len(self.orig)>0 and self.orig[-1]=='\n'):self.orig=self.orig[:-1]
			self.words=s['words']
		else:
			print("Invalid constructor object")
	def __str__(self):
		return str({'orig':self.orig,'words':self.words})
	def __repr__(self):
		return "<Dialline: \""+self.orig+"\">"
	def compareWithMe(self,dl,faster=False):#1800 пар в секунду, до 3600 пар в секунду по сокращённому (faster=True) варианту
		tmp=(len(self.orig)+2)/(len(dl.orig)+2)
		if(tmp>2.0 or tmp<0.5):return 0#Примерно будем считать, что никакой связи
		if(self.orig==dl.orig):return 1
		l1=len(self.words)
		l2=len(dl.words)
		summa=[]
		summaw=[]
		for i in range(l1):
			tmparr=[]
			tmpwarr=[]
			w1=self.words[i]
			for j in range(max(0,i-2),min(l2,i+2)):
				w2=dl.words[j]
				diff=compareWords(w1,w2)
				if(diff==0):continue
				diff*=(1.0-compPhrasesParam1*abs(i/l1-j/l2))
				if(diff<0):continue
				w=w1['semload']+w2['semload']
				tmparr.append(diff)
				tmpwarr.append(w)
			if(len(tmparr)==0):
				summa.append(-w1['semload']*1.6)#Штраф в случае отсутствия слова в заданном диапазоне
				summaw.append(w1['semload']*1.6)
				continue
			tmpm=max(tmparr)
			tmpmw=tmpwarr[tmparr.index(tmpm)]
			summa.append(tmpm*tmpmw)
			summaw.append(tmpmw)
		tmpres=sum(summa)/(sum(summaw)+0.1)
		if(faster):return tmpres
		for i in range(l2):
			tmparr=[]
			tmpwarr=[]
			w2=dl.words[i]
			for j in range(max(0,i-2),min(l1,i+2)):
				w1=self.words[j]
				diff=compareWords(w1,w2)
				if(diff==0):continue
				diff*=(1.0-compPhrasesParam1*abs(i/l2-j/l1))
				if(diff<0):continue
				w=w1['semload']+w2['semload']
				tmparr.append(diff)
				tmpwarr.append(w)
			if(len(tmparr)==0):
				summa.append(-w2['semload'])#Штраф в случае отсутствия слова в заданном диапазоне
				summaw.append(w2['semload'])
				continue
			tmpm=max(tmparr)
			tmpmw=tmpwarr[tmparr.index(tmpm)]
			summa.append(tmpm*tmpmw)
			summaw.append(tmpmw)
		return sum(summa)/(sum(summaw)+0.1)

def buildPreprocessedFile(fin,fout):
	fl=open(fin,"r")
	lns=fl.readlines()
	fl.close()
	fl=open(fout,"w")
	for i in lns:
		fl.write(str(dialline(i))+"\n")
	fl.close()

def line2dict(s):
	s=s.replace("\t","").replace("\n","").replace("\"","\\\"").replace("'","\"")
	return json.loads(s)

def comparePhrases(p1,p2):#Для отладки
	dl1=dialline(p1)
	dl2=dialline(p2)
	return dl1.compareWithMe(dl2)

import math
from logStub import logD

tmppp=0

def weightFunction(k):
#	print(k)
	return math.exp(k*1.5)#Характеризует, как долго бот будет помнить дилог, из-за моих кривых ручонок требуем роста функции, а не затухания

class getAnswerByFile():
	diallines=[]
	source=""
	def __init__(self,fname):#fname -- уже обработанный файл
		self.source=fname
		self.diallines=[].copy()#Потому что реализация ООП в Питоне -- то ещё минное поле! Fuck u, bitch object!
		fl=open(fname,'r')
		lns=fl.readlines()
		fl.close()
		for i in lns:
			try:
				t=line2dict(i)
				self.diallines.append(dialline(t))
			except Exception as e:
				logD(e)
				logD(i)
	def __repr__(self):
		return "<Phrase Compare -> "+self.source+">"
	def getAnswerByDial(self,arr):#arr -- массив фраз в диалоге. Метод пытается продолжить его
		dialarr=[]
		for i in arr:
			dialarr.append(dialline(i))
		maxval=0
		maxval_2=0
		maxvalarr=[]
		maxposarr=[]
		dial_l=len(dialarr)
		weights=weightFunction(dial_l-1)
		for i in range(dial_l-2,-1,-1):
			weights+=weightFunction(i)
		logD(str(weights))
		for pos in range(len(self.diallines)-dial_l+1):
			summ=weightFunction(dial_l-1)*self.diallines[pos+dial_l-1].compareWithMe(dialarr[dial_l-1],faster=True)
			if(summ<maxval_2):continue#Дальнейшая проверка не имеет смысла: не перегонит... Наверное
			for i in range(dial_l-2,-1,-1):#С последней фразы начинаем поиск
				summ+=weightFunction(i)*self.diallines[pos+i].compareWithMe(dialarr[i],faster=True)
			if(summ>=maxval):
				maxvalarr.append(summ)
				maxposarr.append(pos)
				maxval=summ
				maxval_2=maxval/(dial_l+1)
		newmaxvalarr=[]
		newmaxposarr=[]
		tmpmaxval=0.8*maxval#Самое долгое уже позади, можно расслабиться
		for k in range(len(maxvalarr)):
			if(maxvalarr[k]>tmpmaxval):
				newmaxvalarr.append(maxvalarr[k])
				newmaxposarr.append(maxposarr[k])#По-хорошему, устроить ещё одну проверку при faster=False, но пофиг
		if(len(newmaxposarr)==0):return 0,""
		tmpp=random.randrange(len(newmaxposarr))
		score=newmaxvalarr[tmpp]/weights
		ind=newmaxposarr[tmpp]+dial_l
		if(ind>=len(self.diallines)):return score,""
		return score,self.diallines[ind].orig

class getAnswerByFile2():#Тоже самое, только считается, что нечётная строка -- собеседник, чётная -- ответ Амадея. Если что -- подгонять путём вставки пустой строки
	diallines=[]
	source=""
	def __init__(self,fname):#fname -- уже обработанный файл
		self.source=fname
		self.diallines=[].copy()#Потому что реализация ООП в Питоне -- то ещё минное поле! Fuck u, bitch object!
		fl=open(fname,'r')
		lns=fl.readlines()
		fl.close()
		for i in lns:
			try:
				t=line2dict(i)
				self.diallines.append(dialline(t))
			except Exception as e:#pass
				logD(e)
				logD(i)
	def __repr__(self):
		return "<Phrase Compare 2 -> "+self.source+">"
	def getAnswerByDial(self,arr):#arr -- массив фраз в диалоге. Метод пытается продолжить его
		dialarr=[]
		for i in arr:
			dialarr.append(dialline(i))
		maxval=0
		maxval_2=0
		maxvalarr=[]
		maxposarr=[]
		dial_l=len(dialarr)
		weights=weightFunction(dial_l-1)
		for i in range(dial_l-2,-1,-1):
			weights+=weightFunction(i)
		logD(str(weights))
		for pos in range(len(self.diallines)-dial_l+1):
			if( (pos+dial_l)%2==0 ):continue#Через строку
			summ=weightFunction(dial_l-1)*self.diallines[pos+dial_l-1].compareWithMe(dialarr[dial_l-1],faster=True)
			if(summ<maxval_2):continue#Дальнейшая проверка не имеет смысла: не перегонит... Наверное
			for i in range(dial_l-2,-1,-1):#С последней фразы начинаем поиск
				summ+=weightFunction(i)*self.diallines[pos+i].compareWithMe(dialarr[i],faster=True)
			if(summ>=maxval):
				maxvalarr.append(summ)
				maxposarr.append(pos)
				maxval=summ
				maxval_2=maxval/(dial_l+1)
		newmaxvalarr=[]
		newmaxposarr=[]
		tmpmaxval=0.8*maxval#Самое долгое уже позади, можно расслабиться
		for k in range(len(maxvalarr)):
			if(maxvalarr[k]>tmpmaxval):
				newmaxvalarr.append(maxvalarr[k])
				newmaxposarr.append(maxposarr[k])#По-хорошему, устроить ещё одну проверку при faster=False, но пофиг
		if(len(newmaxposarr)==0):return 0,""
		tmpp=random.randrange(len(newmaxposarr))
		score=newmaxvalarr[tmpp]/weights
		ind=newmaxposarr[tmpp]+dial_l
		if(ind>=len(self.diallines)):return score,""
		return score,self.diallines[ind].orig

#TODO: Допилить, чтобы текст с картинки тоже учитывал
