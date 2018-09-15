#!/usr/bin/env python3
print("Load utils...")
import math,time,json,urllib.request,subprocess,re,APIkeys,pymorphy2
from logStub import logD

'''
bashExec -- Выполнить в терминале
getJSON -- Возвращает JSON по заданному адресу
getHTML -- Возвращает HTML по заданному адресу
deleteEnd -- Удалить окончание у слова
getStartForm -- Узнать начальную форму слова
onlyword -- обрезает слово, убирая все не-буквы
wordInfo(w) -- получить JSON с информацией о слове: его формах, корне и синонимах
str2arr -- возвращает массив слов в строке
addmood -- добавляет в базу информацию о настроении слов в данной строке
savemoodset -- сохранение базы данных о настроениях слов
checkText -- проверяет текст на наличие ошибок и исправляет их, используя Яндекс.Спеллер https://tech.yandex.ru/speller/
'''

def ttt():
	return time.strftime("[%H:%M:%S]: ")

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

#Получить JSON из адреса
def getJSON(url,ttl=5):
	try:
		bts = urllib.request.urlopen(url)
		s=bts.read().decode('UTF-8')
		bts.close()
		return json.loads(s)
	except Exception as e:
		logD("JSON error: "+str(e))
		if(ttl>0):
			time.sleep(0.4)
			return getJSON(url,ttl-1)
	return json.loads("{}")

def getHTML(url,ttl=5):
	try:
		bts = urllib.request.urlopen(url)
		s=bts.read().decode('UTF-8')
		bts.close()
		return s
	except Exception as e:
		logD("HTML error: "+str(e))
		if(ttl>0):
			time.sleep(0.4)
			return getHTML(url,ttl-1)
	return ""

def isEnglish(txt):#Simple method for check Language (RU/EN)
	en="qwertyuiopasdfghjklzxcvbnm"
	ru="йцукенгшщзфывапролджэячсмитьбю"
	enc=0
	ruc=0
	txtl=txt.replace(" ","").lower()
	for i in en:
		enc+=txtl.count(i)
	for i in ru:
		ruc+=txtl.count(i)
	res=(enc-ruc)/len(txtl)
	return (res+1)/2

#Утилита удаления окончаний слов
end3=["ing","ier"]
end2=["ed","er","es"]
end1=["s"]
def deleteEnd(w):#TODO:Обращение к готовому словарю или Морфию
	if(not isEnglish(w)):
		return pymorphy2.utils.longest_common_substring(wordInfo(w)['forms'])#TODO: test it
	if(len(w)<3):
		return w
	tmp=w[-3:]
	if(len(w)>3):
		if(tmp in end3):
			return w[:-3]
	tmp=w[-2:]
	if(tmp in end2):
		return w[:-2]
	tmp=w[-1:]
	if(tmp in end1):
		return w[:-1]
	return w

morph = pymorphy2.MorphAnalyzer()#Use it for calls to pymorphy2
'''Korobov M.: Morphological Analyzer and Generator for Russian and
Ukrainian Languages // Analysis of Images, Social Networks and Texts,
pp 320-332 (2015).'''
def getStartForm(w):#Узнать начальную форму
	try:
		p=morph.parse(w)[0]#https://habr.com/post/176575/ -- Спасибо )))
		if('PRTF' in p.tag):#Причастие?
			return p.inflect({'sing', 'nomn'}).word
		return p.normal_form
	except Exception as e:
		logD("Morph error: "+str(e))
	wd=deleteEnd(w)
	if(wd==w):return w
	end=w[len(wd):]
	if(end in ["ишь","ите","ьте","ить","ат","ят","ит"]):
		return wd+"ить"
	if(end in ["ешь","ете","ать","ут","ют","ет"]):
		return wd+"ать"
	return w

def onlyword(w):#Утилита обрезки слова
	return str2arr(w)[0]#Ненуаче? )

#Загрузка словаря по частям речи
dictionw=[]
dictioni=[]
try:
	fl=open("utilsdata/dictionary","r")
	diction=fl.readlines()
	fl.close()
	for i in diction:
		tmp=i.split("\t")
		dictionw.append(tmp[0].replace("\t",""))#str(w).replace("'","\"")
		dictioni.append(json.loads(tmp[1].replace("\t","").replace("\n","").replace("'","\"")))
except Exception as e:
	logD("Warning: utilsdata/dictionary not found or bad, "+str(e))

reg1=re.compile('>\w\w*<')
def wordInfo_wiki(w):
	oldw=w#Для фикса какого-то бага, связанного с добавлением одного слова несколько раз
	logD("Info: word '"+w+"' not found in dictionary, try to find in Wiktionary")
	time.sleep(0.7)#TODO: Delete it in release
	url="https://ru.wiktionary.org/w/api.php?action=opensearch&format=json&formatversion=2&search"+urllib.parse.urlencode([("",w)])+"&namespace=0&limit=5&suggest=true"
	j=getJSON(url)
	if(len(j[1])==0):
		w=getStartForm(w)
		url="https://ru.wiktionary.org/w/api.php?action=opensearch&format=json&formatversion=2&search"+urllib.parse.urlencode([("",w)])+"&namespace=0&limit=5&suggest=true"
		j=getJSON(url)
	if(len(j[1])>0 and j[1][0]!=w.lower()):#Python ленив, он не будет проверять второе, если первое ложь
		w=getStartForm(w)
		url="https://ru.wiktionary.org/w/api.php?action=opensearch&format=json&formatversion=2&search"+urllib.parse.urlencode([("",w)])+"&namespace=0&limit=5&suggest=true"
		j=getJSON(url)
	if(len(j[1])>0 and len(j[1][0])-len(w)<2):
		url=j[3][0]
		time.sleep(0.1)
		h=getHTML(url)
		try:h=h[:h.index("id=\"Этимология")]
		except:pass
		d={}
		d["word"]=j[1][0]#Слово в нач.форме
		d["parts"]=""#Возможные части речи
		if(h.count("Существительное")>0):d["parts"]+="|сущ"
		if(h.count("Прилагательное")>0):d["parts"]+="|прил"
		if(h.count("Причастие")>0):d["parts"]+="|прич"
		if(h.count("Глагол")>0):d["parts"]+="|гл"
		if(h.count("Наречие")>0 or h.count("естоименное наречие")>0):d["parts"]+="|нар"
		if(h.count("Деепричастие")>0):d["parts"]+="|деепр"
		if(h.count("Предлог")>0):d["parts"]+="|предл"
		if(h.count("Местоимение")>0):d["parts"]+="|мест"
		if(h.count("Числительное")>0):d["parts"]+="|числ"
		d["parts"]+="|"
		d["syns"]=[]#Синонимы и гипонимы
		try:
			tmp=h.index('id="Синонимы"')
			tmp=h[tmp+14:tmp+1014]
			if(tmp.count("Антонимы")>0):tmp=tmp[:tmp.index("Антонимы")]#Защита от следующего раздела
			tmp=re.findall(reg1,tmp.replace(">править<",""))
			for i in tmp:
				tt=onlyword(i).lower()
				if(tt in d["syns"]):continue
				d["syns"].append(tt)
		except Exception as e:
			logD("Warn: Cannot get synonims, "+str(e))
		try:
			tmp=h.index('id="Гипонимы"')
			tmp=h[tmp+14:tmp+1014]
			if(tmp.count("Родственные слова")>0):tmp=tmp[:tmp.index("Родственные слова")]#Защита от следующего раздела
			tmp=re.findall(reg1,tmp.replace(">править<",""))
			for i in tmp:
				tt=onlyword(i)
				if(tt in d["syns"]):continue
				d["syns"].append(tt)
		except Exception as e:
			logD("Warn: Cannot get hyponims, "+str(e))
		d["root"]=""#Корень слова
		try:
			tmp=h.index("Корень:")
			d["root"]=re.findall(re.compile('<b>-\w\w*-<'),h[tmp+7:tmp+70])[0][4:-2]
		except Exception as e:
			logD("Warn: Cannot get word root, "+str(e))
		d["forms"]=[]#Словоформы
		try:
			if(d["parts"].count("|сущ|")+d["parts"].count("|мест|")+d["parts"].count("|числ|")>0):
				tmp=h.index(">падеж</a>")
				tmp=h[tmp:tmp+2500]
				try:tmp=tmp[:tmp.rindex("</table>")]
				except:pass
				tmp=re.findall(re.compile('>\w\w*\W\w*\\n<'),tmp)
				for i in tmp:
					tt=onlyword(i)
					if(tt in d["forms"]):continue
					d["forms"].append(tt)
			if(d["parts"].count("|гл|")>0):
				tmp=h.index(">наст.</a>")
				tmp=h[tmp:tmp+2500]
				try:tmp=tmp[:tmp.rindex("</table>")]
				except:pass
				tmp=re.findall(re.compile('>\w\w*\W\w*\\n<'),tmp)
				for i in tmp:
					tt=onlyword(i)
					if(tt in d["forms"]):continue
					d["forms"].append(tt)
		except Exception as e:
			logD("Warn: Cannot get word forms, "+str(e))
			p=morph.parse(w)
			for i in p[0].lexeme:
				if(i.word in d["forms"]):continue
				d["forms"].append(i.word)
				if(len(d["forms"])==14):break
		if(not oldw in d["forms"] and oldw!=d["word"]):d["forms"].append(oldw)#Фикс бага с несколькими добавлениями одного слова
		if(d["root"]=="" and d["parts"].count("сущ")+d["parts"].count("при")+d["parts"].count("гл")+d["parts"].count("деепр")+d["parts"].count("нар")>0 and len(d["forms"])>2):
			d["root"]=pymorphy2.utils.longest_common_substring(d['forms'])#Угадывание корня, если его не нашли в Вики
		d['comm']="wiki"#Комментарий. Сейчас тут указывается источник информации
		d=patchWord(d)#Возможно, ещё надо доработать
		dictionw.append(oldw)
		dictioni.append(d)
		if(d["word"] in dictionw):#Глюк, исследовать
			return d
		try:bashExec("echo \""+w+"\t"+str(d)+"\" >> utilsdata/dictionary")
		except Exception as e:logD("Warn: Cannot add word to dictionary, "+str(e))
		return d
	logD("Bad word: "+w+", it doesn't found in Wiki")
	logD(j)
	d={}
	d["word"]=getStartForm(w)#Stub
	d["parts"]=""
	d["forms"]=[]
	p=morph.parse(w)
	for i in p[0].lexeme:
		if(i.word in d["forms"]):continue
		d["forms"].append(i.word)
		if(len(d["forms"])==13):break
	tmp=""
	for i in p:
		try:tmp+=i.tag.POS+","
		except:pass#Лень разбираться, что тут не так
	if(tmp.count("NOUN")>0):d["parts"]+="|сущ"
	if(tmp.count("ADJ")>0):d["parts"]+="|прил"
	if(tmp.count("VERB")+tmp.count("INFN")>0):d["parts"]+="|гл"
	if(tmp.count("PRT")>0):d["parts"]+="|прич"
	if(tmp.count("GRND")>0):d["parts"]+="|деепр"
	if(tmp.count("NUMR")>0):d["parts"]+="|числ"
	if(tmp.count("NPRO")>0):d["parts"]+="|мест"
	if(tmp.count("PREP")>0):d["parts"]+="|предл"
	if(tmp.count("ADVB")>0):d["parts"]+="|нар"
	d["parts"]+="|"
	d["root"]=""
	if(d["parts"].count("сущ")+d["parts"].count("при")+d["parts"].count("гл")+d["parts"].count("деепр")+d["parts"].count("нар")>0 and len(d["forms"])>2):
		d["root"]=pymorphy2.utils.longest_common_substring(d['forms'])#Угадывание корня
	d["syns"]=[]
	try:
		j=getJSON("http://www.serelex.org/find/ru-skipgram-librusec/"+urllib.parse.urlencode([("",w)])[1:])['relations']
		d["syns"].append("____")#For good metric in future because Serelex is so vague
		for i in j:
			tt=getStartForm(i['word']).lower()
			if(tt in d["syns"]):continue
			if(len(d["syns"])>4):break
			d["syns"].append(tt)
	except Exception as e:
		logD("Warn: serelex through error: "+str(e))
	d['comm']="morph"#Комментарий. Сейчас тут указывается источник информации
	dictionw.append(oldw)
	dictioni.append(d)
	return d

def wordInfo(w):#Получить подробную информацию по слову
	w=w.lower()#TODO: Переписать на*** заново!
	global dictionw,dictioni
	if(w in dictionw):
		return dictioni[dictionw.index(w)]
	for i in dictioni:
		if(w in i['forms']):
			return i
	return wordInfo_wiki(w)

def makeDictionaryByFile(fname):#Создание словаря из слов в файле
	fl=open(fname,"r")
	lns=fl.readlines()
	fl.close()
	for s in lns:
		words=str2arr(s)
		for w in words:
			try:
				inf=wordInfo(w)
			except Exception as e:
				logD(w+": "+str(e))
				time.sleep(20)

def patchDictionary():
	global dictionw,dictioni
	for i in range(len(dictionw)):
		d=dictioni[i]
		formlen=max(3,len(d['root']))
		for j in range(len(d['forms'])):
			if(j>=len(d['forms'])):break
			if(len(d['forms'][j])<formlen):d['forms'].pop(j)
		if("|гл|" in d['parts'] and len(d['forms'])>13):
			d['forms']=d['forms'][:13]#Убираем причастия
		if(len(d['forms'])<2):
			p=morph.parse(d['word'])
			for j in p[0].lexeme:
				if(j.word in d["forms"]):continue
				d["forms"].append(j.word)
				if(len(d["forms"])==13):break
		try:bashExec("echo \""+d['word']+"\t"+str(d)+"\" >> utilsdata/dictionary.patched")
		except Exception as e:logD("Err: Cannot add word to dictionary, "+str(e))

def patchWord(d):
	formlen=max(3,len(d['root']))
	for j in range(len(d['forms'])):
		if(j>=len(d['forms'])):break
		if(len(d['forms'][j])<formlen):d['forms'].pop(j)
	if("|гл|" in d['parts'] and len(d['forms'])>13):
		d['forms']=d['forms'][:13]#Убираем причастия
	if(len(d['forms'])<2):
		p=morph.parse(d['word'])
		for j in p[0].lexeme:
			if(j.word in d["forms"]):continue
			d["forms"].append(j.word)
			if(len(d["forms"])==13):break
	return d


reg0=re.compile('\w*[\w\-\']\w*')#re.compile('\w\w*')
def str2arr(txt):
	arr=re.findall(reg0,txt)
	while(arr.count("-")>0):
		arr.pop(arr.index("-"))
	return arr

####################################################
###############  YANDEX TECNOLOGIES  ###############
####################################################
def checkText(s):
	url="https://speller.yandex.net/services/spellservice.json/checkText?options=4&text"+urllib.parse.urlencode([("",s)])
	try:
		errs=getJSON(url)
		for i in errs:
			if(len(i['s'])==0):
				logD("YaSpeller warn: no variants for "+i['word'])
				continue
			pos=i['pos']
			l=i['len']
			fr=i['word']
			if(fr in ['Курису','курису','Макисэ','макисэ']):continue#Это не ошибка
			to=i['s'][0]
			s=s[:pos]+s[pos:int(pos+l*1.5)].replace(fr,to)+s[int(pos+l*1.5):]#Test this place carefully
	except Exception as e:
		logD("YaSpeller error: "+str(e))
	return s

def entoru(q):
	url="https://translate.yandex.net/api/v1.5/tr.json/translate?key="+APIkeys.YandexTranslate+"&text"+urllib.parse.urlencode([("",q)])+"&lang=en-ru&format=plain"
	try:
		j=getJSON(url)
		return j['text'][0]
	except Exception as e:
		logD("Yatranslate error: "+str(e))
		return ""

def rutoen(q):
	url="https://translate.yandex.net/api/v1.5/tr.json/translate?key="+APIkeys.YandexTranslate+"&text"+urllib.parse.urlencode([("",q)])+"&lang=ru-en&format=plain"
	try:
		j=getJSON(url)
		return j['text'][0]
	except Exception as e:
		logD("Yatranslate error: "+str(e))
		return ""

#http://study.mokoron.com/ -- корпус текстов|UPD: Так и не юзал

#Информация о настроении слова
#TODO: Make it

######################################################
############### COPIED SEMANTIC MODULE ###############
######################################################
semwithoutends=[]#На самом деле тут лежат начальные формы слов, а не без окончаний, просто этот блок перекопирован из более ранней версии
semwordcount=[]
semprecalcans=[]#Кэш
sem_isCacheBuilt=False
semmaxcount=0#Не помню, зачем это нужно, но нужно
semmeancount=0

def SEMlearnByTXT(txt):
	global semwithoutends,semwordcount,semmaxcount,semmeancount
	tmpa=str2arr(txt.lower())
	tmpb=[]
	for w in tmpa:
		tmpb.append(getStartForm(w))
	for i in range(len(tmpb)):
		w=tmpb[i]
		if(w in semwithoutends):
			semwordcount[semwithoutends.index(w)]+=1
		else:
			semwithoutends.append(w)
			rw=tmpa[i]
			semwordcount.append(1)
			if(len(rw)>4):
				if(rw[:-4].count("ци")==1):
					semwordcount[-1]=1.5
	semmaxcount=max(semwordcount)
	semmeancount=sum(semwordcount)/len(semwordcount)

def SEMlearnByFile(fname):
	global semwithoutends,semwordcount,semmaxcount,semmeancount
	fl=open(fname,"r")
	arr=fl.readlines()
	fl.close()
	import sys
	for i in range(len(arr)):
		if(i%50==0):
			sys.stdout.write(str(int(10000*i/len(arr))/100)+"%   \r")
		SEMlearnByTXT(arr[i])
	logD("Complete!")

def SEMoptimize():#Ускоряет поиск и удаляет редкие слова(на практике около 18-33%)
	global semwithoutends,semwordcount,semmaxcount,semmeancount
	newsemwordcount=semwordcount.copy()
	newsemwordcount.sort()
	newsemwordcount.reverse()
	ind=len(newsemwordcount)
	try:
		ind=newsemwordcount.index(3)#Убираем редкие слова
	except:
		try:
			ind=newsemwordcount.index(3.5)
		except:
			pass
	newsemwordcount=newsemwordcount[:ind]
	newsemwithoutends=[]
	for i in newsemwordcount:
		tmp=semwordcount.index(i)
		newsemwithoutends.append(semwithoutends[tmp])
		semwordcount[tmp]=-1
	semwithoutends=newsemwithoutends
	semwordcount=newsemwordcount
	semmeancount=sum(semwordcount)/len(semwordcount)

SEMparam=5#Эмпирически подобранная константа, которая в принципе влияет только на мастабируемость и внешний вид ответа

def getSemanticLoad(txt):#Узнать, насколько значим текст. Около 550 слов в секунду
	if(len(txt)<2):
		return 0
	global semwithoutends,semwordcount,semmaxcount,semmeancount,semprecalcans,sem_isCacheBuilt
	tmpa=str2arr(txt.lower())
	if(len(tmpa)==0):
		return 0
	tmpb=[]
	for w in tmpa:
		tmpb.append(getStartForm(w))
	summ=0
	tmpc=0
	if(sem_isCacheBuilt):
		for w in tmpb:
			if(len(w)<2):continue
			if(w in semwithoutends):
				summ+=semprecalcans[semwithoutends.index(w)]
			else:
				summ+=math.tanh((len(w)+w.count("ци")+w.count("ф"))/5)
			tmpc+=1
		if(tmpc==0):return 0
		return summ/tmpc
	for i in range(len(tmpb)):
		w=tmpb[i]
		if(len(w)<2):
			continue
		if(w in semwithoutends):
			summ+=1-math.tanh(semwordcount[semwithoutends.index(w)]/(SEMparam*semmeancount))
		else:
			summ+=math.tanh((len(w)+w.count("ци")+w.count("ф"))/5)
		tmpc+=1
	if(tmpc==0):return 0
	return summ/tmpc

def SEMbuildCache():
	global semwithoutends,semwordcount,semmaxcount,semmeancount,semprecalcans,sem_isCacheBuilt
	semprecalcans=[]
	sem_isCacheBuilt=False
	for ic in semwordcount:
		semprecalcans.append(1-math.tanh(ic/(SEMparam*semmeancount)))
	sem_isCacheBuilt=True

def getSemanticLoad_low(w):
	if(len(w)<2):
		return 0
	global semwithoutends,semwordcount,semmaxcount,semmeancount,semprecalcans
	w=w.lower()
	if(w in semwithoutends):
		if(sem_isCacheBuilt):return semprecalcans[semwithoutends.index(w)]
		return 1-math.tanh(semwordcount[semwithoutends.index(w)]/(SEMparam*semmeancount))
	else:
		return math.tanh((len(w)+w.count("ци")+w.count("ф"))/5)

def comparePhrases(a,b):#TODO: Переделать под новые реалии
	if(a==b):
		return 1
	a_arr=str2arr(a)
	b_arr=str2arr(b)
	if(a_arr==b_arr):
		return 0.99
	if(len(a_arr)==0 or len(b_arr)==0):
		return 0
	for i in range(len(a_arr)):
		a_arr[i]=getStartForm(a_arr[i])
	for i in range(len(b_arr)):
		b_arr[i]=getStartForm(b_arr[i])
	f1=0
	for i in a_arr:
		tmp=getSemanticLoad_low(i)
		if(i in b_arr):
			f1+=1
		else:
			f1-=tmp
	f2=0
	for i in b_arr:
		tmp=getSemanticLoad_low(i)
		if(i in a_arr):
			f2+=1
		else:
			f2-=tmp
	return (f1+f2)/(len(a_arr)+len(b_arr))-0.001

def SEMsaveData(fname):
	global semwithoutends,semwordcount,semmaxcount,semmeancount
	fl=open(fname+".semwithoutends","w")
	tmp=fl.write(semwithoutends[0])
	for i in semwithoutends[1:]:
		fl.write("\n"+i)
	fl.close()
	fl=open(fname+".semwordcount","w")
	tmp=fl.write(str(semwordcount[0]))
	for i in semwordcount[1:]:
		fl.write("\n"+str(i))
	fl.close()
	logD("Saved!")

def SEMloadData(fname):
	global semwithoutends,semwordcount,semmaxcount,semmeancount
	fl=open(fname+".semwithoutends","r")
	semwithoutends=fl.readlines()
	for i in range(len(semwithoutends)):
		semwithoutends[i]=semwithoutends[i].replace("\n","")
	fl.close()
	fl=open(fname+".semwordcount","r")
	semwordcount=fl.readlines()
	for i in range(len(semwordcount)):
		semwordcount[i]=float(semwordcount[i])
	fl.close()
	semmaxcount=max(semwordcount)
	semmeancount=sum(semwordcount)/len(semwordcount)
	logD("Loaded!")

try:
	SEMloadData("utilsdata/semanticloadinfo")
	semwordcount[semwithoutends.index("не")]/=1000
	semwordcount[semwithoutends.index("нет")]/=1000
	semwordcount[semwithoutends.index("нельзя")]/=100#Учёт отрицаний, они важны
	semwordcount[semwithoutends.index("макисэ")]*=1000#Это скорее всего обращение, можно игнорить
	semwordcount[semwithoutends.index("курис")]*=1000#Это скорее всего обращение, можно игнорить
	SEMbuildCache()
except Exception as e:
	logD("Error at load semantic load model: "+str(e))

def getMainTheme(txt):#TODO:Переделать под новые реалии
	if(len(txt)<2):
		return []
	global semwithoutends,semwordcount,semmaxcount,semmeancount,semprecalcans
	tmpa=str2arr(txt)
	if(len(tmpa)==0):
		return []
	tmpb=[]
	for w in tmpa:
		tmpb.append(getStartForm(w))
	res=[]
	loads=[]
	for i in tmpb:
		loads.append(getSemanticLoad_low(i)*(1+wordInfo(i)['parts'].count("|сущ|")))
	level=max(0.18,max(loads)/2)
	for i in range(len(loads)):
		if(loads[i]>level):
			res.append(tmpb[i])
	return res

#######################################################
################  END SEMANTIC MODULE  ################
#######################################################

def compareWords(a,b):#Можно ли считать, что a это b, до 400 пар в секунду
	if(a==b):return 0#Точное совпадение
	aa=getStartForm(a)
	bb=getStartForm(b)
	if(aa==bb):return 0.1
	a=a.lower()
	b=b.lower()
	infa=wordInfo(a)
	infb=wordInfo(b)
	snsa=infa['syns']
	snsb=infb['syns']
	mans=1
	for s1 in range(len(snsa)):
		if(b==snsa[s1]):
			mans=0.15+0.1*s1
			break
	for s2 in range(len(snsb)):
		if(a==snsb[s2]):
			return min(mans,0.15+0.1*s2)
	if(mans<1):return mans
	if(infb['root']==infa['root']):return 0.96
	return 1#Связи не найдено

compPhrasesParam1=0.7#"На глазок"
def compPhrasesAddon(w1,w2,p1,p2,l1,l2):
	diff=compareWords(w1,w2)
	if(diff==1):return 0#Всё плохо
	diff=1-diff
	diff*=(1-compPhrasesParam1*abs(p1/l1-p2/l2))#1 для хорошего совпадения и 0.3 для плохого
	return diff

def compPhrasesAddon2(w1,p1,l1,arr2,l2):
	difs=[]
	for p2 in range(l2):
		difs.append(compPhrasesAddon(w1,arr2[p2],p1,p2,l1,l2))
	v=max(difs)
	w=getSemanticLoad_low(arr2[difs.index(v)])+getSemanticLoad_low(w1)
	return v,w

def comparePhrases2(a,b):#2-3 сравнения в секунду, очень медленно...TODO: Оптимизировать
	if(a==b):
		return 1
	a_arr=str2arr(a)
	b_arr=str2arr(b)
	if(a_arr==b_arr):
		return 0.99
	la=len(a_arr)
	lb=len(b_arr)
	if(la==0 or lb==0):
		return 0
	#We have: getSemanticLoad_low, compareWords
	sumsA=[]#Массив максимумов сравнений слов из А со словами из В
	sumsB=[]
	weightsA=[]
	weightsB=[]
	for i in range(la):
		v,w=compPhrasesAddon2(a_arr[i],i,la,b_arr,lb)
		sumsA.append(v*w)
		weightsA.append(w)
	for i in range(lb):
		v,w=compPhrasesAddon2(b_arr[i],i,lb,a_arr,la)
		sumsB.append(v*w)
		weightsB.append(w)
	return (sum(sumsA)+sum(sumsB))/(sum(weightsA)+sum(weightsB))

logD("Utils loaded")
