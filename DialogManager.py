#!/usr/bin/env python3
import PhraseCompare as pa
import subprocess,random,utils,time
from logStub import logD

####################################################################
##########################   Лирика   ##############################
####################################################################
#TODO: Вынести в отдельный файл, например knowledger

def bashExec(q):#Выполнить в терминале, вернуть строку ответа
	return subprocess.check_output(q,shell=True).decode("UTF-8")

def isEnglish(txt):#Узнать язык: русский(-1) или английский(1)
	en="qwertyuiopasdfghjklzxcvbnm"
	ru="йцукенгшщзфывапролджэячсмитьбю"
	enc=0
	ruc=0
	txtl=txt.replace(" ","").lower()
	for i in en:
		enc+=txtl.count(i)
	for i in ru:
		ruc+=txtl.count(i)
	res=(enc-ruc)/(len(txtl)+0.0001)
	return (res+1)/2

def sendfstub(t,i):
	print(str(i)+"-> "+t)
	return True

def typefstub(i):
	print("Набираю сообщение...")

####################################################################
#######################   Конец Лирики   ###########################
####################################################################

dialAdapters=[]#Хранит адапетры диалогов

logD("Load Kurisu dialog adapter")
kurisu=pa.getAnswerByFile2("data/kurisu.preprocessed")#Чувствителен к чётным/нечётным строкам. Будет неудобно, если вдруг Амадей ответит не за свою роль
dialAdapters.append(kurisu)
logD("Load general dialog adapter")
gener=pa.getAnswerByFile("data/general.preprocessed")
dialAdapters.append(gener)
logD("Load trubot dialog adapter")
trubot=pa.getAnswerByFile("data/trubot.preprocessed")
dialAdapters.append(trubot)
logD("Load subs")
subsadapt=pa.getAnswerByFile("data/subs.preprocessed")
dialAdapters.append(subsadapt)
logD("Dialog adapters loaded")

def fixTxtIfNeed(txt):
	arr=utils.str2arr(txt)
	for w in arr:
		if(not utils.getStartForm(w) in utils.dictionw):
			return utils.checkText(txt)
	return txt

def getAnsswerByDialsit(cont,dialsit):#Ответ по всем адаптерам и knowledger
	global dialAdapters#TODO: Раcпараллелить
	answers=[]
	answersscore=[]
	for adapt in dialAdapters:
		sc,ans=adapt.getAnswerByDial(dialsit)
		answers.append(ans)
		answersscore.append(sc)
		if(sc>0.85):#Достаточно точное совпадение
			debuginfo="\nРассматриваемые варианты: "+str(answers)+"\n"+str(answersscore)
			return sc,ans,debuginfo
	msc=max(answersscore)
	debuginfo="\nРассматриваемые варианты: "+str(answers)+"\n"+str(answersscore)
	return msc,answers[answersscore.index(msc)],debuginfo

class Dialog():
	privScore=0.1#Какая уверенность для ответа в личной беседе
	pubScore=0.7#Какая уверенность для ответа в беседе с несколькими участниками
	lastCall=-1
	isAnswered=True#Тут опасный баг! UPD: Теперь нет вроде
	t1=0
	def __repr__(self):
		tmp=self.__ident
		if(type(tmp)!=str):tmp=str(tmp)
		return "<Dialog id="+tmp+">"
	def __init__(self,context=[],identificator=0,sendfunction=sendfstub,typefunction=typefstub):
		logD("Вызван конструктор диалога")
		self.__context=context.copy()#Клбчевые слова разговора
		self.__ident=identificator#Уникальный идентификатор собеседника
		self.__sendf=sendfunction#Функция отправки. Первым аргументом передаётся текст, вторым -- идентификатор
		self.__typef=typefunction#Функция тайпинга. Передаётся 1 аргумент -- идентификатор
		self.__debuginfo=""
		self.__lastsent=""#Последнее отправленное сообщение
		self.dialsit=['\n','\n'].copy()#Последние несколько фраз, более 5 точно нет смысла
	def sendAnswer(self,txt,isClear=False):#Если isClear=True, то сообщение отправляется сразу и без проверок
		if(txt==""):
			self.isAnswered=False
			logD("Null Answer")
			return
		if(isClear):
			self.__sendf(txt,self.__ident)
			return
		if(self.__lastsent==txt):
			if(utils.getSemanticLoad(txt)<0.3):
				self.isAnswered=False
				logD("Null Answer")
				return
		self.__lastsent=txt
		#TODO: Ставить в женский род
		txtarr=txt.replace("\n","").split("/pause")
		lag=time.time()-self.t1
		self.__debuginfo+="\nВремя поиска ответа: "+str(lag)+" c"
		if(len(txtarr[0])>5):
			self.__typef(self.__ident)
		realanstxt=txtarr[0].replace("/pause","").replace("\\n","\n")
		self.__sendf(realanstxt,self.__ident)
		if(len( txt.replace("/pause","").replace("\\n","").replace(" ","").replace("\n","") )>0):
			self.isAnswered=True
			self.dialsit.append(txt)
		else:
			self.isAnswered=False#Если реальный текст для отправки пустой или состоит из символа перевода строки, то это не ответ
			logD("Null Answer")
			return
		for i in txtarr[1:]:
			self.__typef(self.__ident)
			if(i=="/pause" or i=="" or i=="/typing"):#просто пауза
				time.sleep(0.25)
				continue
			sleepytime=0.05+0.05*len(i)
			time.sleep(min(sleepytime,5))#отправка статуса о наборе соообщения обычно 5 секунд (например, в Телеграме)
			while(sleepytime>5):
				self.__typef(self.__ident)
				sleepytime-=5
				time.sleep(min(sleepytime,5))
			i=i.replace("/pause","").replace("/typing","").replace("\\n","\n")
			if(len(i)>0):
				i=i[0].upper()+i[1:]
			self.__sendf(i,self.__ident)
	def getAnswer(self,txt,pictxt="",isPrivate=True):#isPrivate решает, молчать в случае сомнений или отвечать
		self.t1=time.time()
		if(len(txt)==0):
			return
		if(txt[:6]=='/start'):
			self.sendAnswer("Я "+random.choice(["Курису Макисэ","Макисэ Курису"])+". Рада познакомиться"+random.choice(["."," )"," ^-^"," ^-^"]))
			return
		if(txt[:6]=='/debug'):
			self.sendAnswer("**Отладочная информация**:\n"+self.__debuginfo,isClear=True)#Отправка отладочной информации
			return
		if(self.lastCall>0 and time.time()-self.lastCall>1000):
			logD("Clear dial situation (a lot time)")
			self.dialsit=['\n','\n'].copy()
		self.lastCall=time.time()
		txt=fixTxtIfNeed(txt)#Позря старается не обращаться к Яндекс.Спеллеру
		self.__debuginfo=""
		self.__debuginfo+="\nТекст: \""+txt+"\""
		self.__debuginfo+="\nТекст с картинки: \""+pictxt+"\""
		if(isEnglish(txt)>0.5):
			txt=utils.entoru(txt)#Перевод на русский
			self.__debuginfo+="\nОригинал на английском, перевод: \""+txt+"\""
		if(isEnglish(pictxt)>0.5):
			pictxt=utils.entoru(pictxt)#Перевод на русский текста с картинки
			self.__debuginfo+="\nОригинал картинки на английском, перевод: \""+txt+"\""
		self.__context+=utils.getMainTheme(txt)
		if(len(self.__context)>10):self.__context=self.__context[-10:]
		self.__debuginfo+="\nТекущий контекст: "+str(self.__context)
		#Тело
		if(self.isAnswered):self.dialsit.append(txt)
		else:self.dialsit[-1]+="/pause "+txt
		if(len(self.dialsit)>4):self.dialsit=self.dialsit[-4:]#Рассматриваются 4 последних фразы диалога
		self.__debuginfo+="\nТекущий dialsit: "+str(self.dialsit)
		msc,ans,dbg=getAnsswerByDialsit(self.__context,self.dialsit)#Непосредственно получение ответа
		self.__debuginfo+=dbg
		if(msc>self.pubScore or (msc>self.privScore and isPrivate)):
			self.sendAnswer(ans)
			return
		self.isAnswered=False
	def debug(self):
		return self.__debuginfo
#		self.sendAnswer("**Отладочная информация**:\n"+self.__debuginfo,isClear=True)

#Чтобы можно было просто вызывать
dialogs=[]
dialogids=[]
def getDialogById(ident,context=[],sendfunction=sendfstub,typefunction=typefstub):#Если существует диалог, то вернёт его. Если нет -- создаст
	if(dialogids.count(ident)>0):
		return dialogs[dialogids.index(ident)]
	dialogs.append(Dialog(context,ident,sendfunction,typefunction))
	dialogids.append(ident)
	return dialogs[-1]
