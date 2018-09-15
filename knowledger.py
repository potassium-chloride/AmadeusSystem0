#!/usr/bin/env python3
import sys,time,json,urllib.request,subprocess,random,utils,APIkeys

from logStub import logD

debug=True
ua="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
WF_APPID=APIkeys.WF_APPID

#https://tproger.ru/wp-content/plugins/citation-widget/get-quote.php -- прогерские цитаты, но Курису не очень в компах

fl=open("data/quotes.txt","r")
quotes=fl.readlines()#Цитаты
fl.close()

def getRandquote():#Случайная цитата из цитатника
	return random.choice(quotes)

###################################

from urllib.request import FancyURLopener

def getBashorg():#Получить цитату с баша
	FancyURLopener.version='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'
	myopener=FancyURLopener()
	page = myopener.open('https://bash.im/forweb/')
	s=page.read().decode("cp1251").replace("<\' + \'br>","\\n").replace("&quot;","\"").replace("&lt;","<").replace("&gt;",">")
	page.close()
	strt=s.index('id="b_q_t" style="padding: 1em 0;">')+len('id="b_q_t" style="padding: 1em 0;">')
	s=s[strt:]
	return s[:s.index("<\'")]

###################################

def getVibor(txt):#Выбрать один вариант из нескольких, TODO: доработать
	txt=txt.replace("Тру, ","").replace("Амадей","").replace("Кристина","").replace("Курису","").replace("Тру,","")#Если вопрос к Тру, то тоже отвечаем
	txt=txt.replace("как думаешь","").replace("что лучше","").replace("Как думаешь","").replace("Что лучше","")
	if(len(txt)<3 or txt.lower().count(" или ")==0):
		return 0.1,""
	txtarr=utils.str2arr(txt[:2]+txt[2:].replace(", "," или ").replace(","," или "))
	if(txtarr.count("или")==0):
		return 0.1,""
	txtarrarr=[""]
	for i in txtarr:
		if(i=="или"):
			txtarrarr.append("")
		else:
			txtarrarr[-1]+=i+" "
	semloads=[]
	for i in txtarrarr:
		semloads.append(utils.getSemanticLoad(i))
	minn=min(semloads)
	mini=semloads.index(minn)
	semloads[mini]=10
	minn2=min(semloads)
	ans=txtarrarr[mini][:-1]
	cov=abs(minn-minn2)/(minn+minn2+1e-6)
	if(cov>0.9):
		ans=random.choice(["Очень сложно, но думаю, что ","Очень сложно, но мне кажется, что ","Сложно/pauseМне кажется, что "])+ans
	elif(cov>0.6):
		ans=random.choice(["Сложно, но думаю, что ","Сложно, но мне кажется, что "])+ans
	elif(cov>0.3):
		ans=random.choice(["Мне кажется, что ","Думаю, что "])+ans
	elif(cov>0.2):
		ans=random.choice(["Я считаю, что ","Моё мнение: ",""])+ans
	else:
		ans=random.choice(["Очевидно, что ","Очевидно же, что ","Ясно, что ","Это же очевидно!/pause","А что думать?/pause"])+ans
	return 1-cov/9,ans

###################################

def getRandAnime():#Случайное аниме с findanime
	try:
		bashExec("wget -O /tmp/randanime.html -U -q \"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0\" -p \"http://findanime.me/internal/random\" 2>/dev/null")
	except:
		pass
	fl=open("/tmp/randanime.html")
	s=""
	for i in range(1000):
		try:
			s=s+fl.readline()
		except:
			break
	fl.close()
	res=""
	try:
		tmp=s.index("<span class='name'>")
		aniname=s[tmp:tmp+200]
		aniname=aniname[aniname.index(">")+1:aniname.index("</span>")]
		res+=aniname
	except Exception as e:
		logD(e)
	try:
		tmp=s.index("<meta itemprop=\"description\" content=\"")
		descript=s[tmp+33:tmp+500]
		descript=descript[descript.index("\"")+1:descript.index("/>")-1]
		res+="\n\n"+descript
	except Exception as e:
		logD(e)
	try:
		tmp=s.index("<meta itemprop=\"url\" content=\"")
		url=s[tmp+25:tmp+200]
		url=url[url.index("\"")+1:url.index("/>")-1]
		res+="\n\nСмотреть онлайн: "+url
	except Exception as e:
		logD(e)
	return res.replace("&quot;","\"")

###################################

def getArxiv0(q):#Arxiv.org low
	if(utils.isEnglish(q)<0.8):
		q=utils.rutoen(q)
	q=q.replace("\n","")#В отличии от Баша, у Архива есть документированный API:
	url="http://export.arxiv.org/api/query?search_query"+urllib.parse.urlencode([("",q)])+"&start=0&max_results=1"
	logD("Original query: "+q)
	bts = urllib.request.urlopen(url,timeout=40)
	s=bts.read().decode('UTF-8')
	bts.close()
	try:
		s=s[s.index("<entry>"):s.index("</summary>")]
		link=s[s.index("<id>")+4:s.index("</id>")].replace("/abs/","/pdf/")
		desc=utils.entoru(s[s.index("<title>")+7:s.index("</title>")])
		return link+" - "+desc
	except Exception as e:
		logD(e)
		return "Ошибка запроса ("

def getArxivArticle(txt):#Статья с arxiv.org по поисковому запросу
	txtarr=utils.str2arr(txt)
	q=""
	for i in txtarr:
		if(i.count("arxiv")+i.count("кинь")+i.count("най")+i.count("пожалуйста")+i.count("плиз")+i.count("мне")+i.count("го")+i.count("стат")+i.count("архив")+i.count("ишли")+i.count("отправь")==0):
			q+=i+" "
	return getArxiv0(q[:-1])#TODO: fix it

###################################

import wolframalpha
cl=wolframalpha.Client(WF_APPID)
def getWolfram(q):#Выполнить запрос к Wolfram|Alpha (англ.)
	res=cl.query(q)['pod']#TODO:Отдебажить, иногда неправильно парсит
	ans=""
	for i in res:
		try:
			if(not i['subpod']['plaintext']==None):
				ans+=i['subpod']['plaintext']+"\n"
		except:
			pass
	ans=ans.replace("\n\n","\n").replace("|","\n\n")
	return ans

def getWolframRU(q):#Выполнить запрос к Wolfram|Alpha (сам переведёт, если надо)
	if(utils.isEnglish(q)<0.5):
		q=rutoen(q)[:-1]
	return entoru(getWolfram(q))

###################################

#Получить JSON из адреса
def getJSON(url):#TODO: Delete this stub
	return utils.getJSON(url)

def bashExec(q):
	return subprocess.check_output(q,shell=True)

def getPogoda():#TODO: Заюзать это, погода в Москве#TODO: сделать разные города
	bashExec("wget -O /tmp/pogoda.html -U \""+ua+"\" \"https://p.ya.ru/moscow\" 2>/dev/null")
	tmp=bashExec("html2text -utf8 /tmp/pogoda.html").decode("utf-8").replace("=============================================================================","=")
	return tmp

###################################

def weakWiki(url):#HTML Wiki
	if(debug):logD("Обращение к html Википедии")
	bashExec("wget -O /tmp/wikitest.html -U \""+ua+"\" \""+url+"\" 2>/dev/null")
	tmp=bashExec("html2text -utf8 /tmp/wikitest.html").decode("utf-8")+"поискsearch"
	tmp=tmp[min(tmp.index("поиск")+tmp.index("search"))+5:]
	tmp=tmp[:tmp.index("*****")]
	tmp=tmp.replace("\n"," ")

def strongWiki(q):#Запрос к Википедии (русской)
	if(debug):logD("Обращение к русской Википедии")
	if(q.count("что такое")>0):q=q.replace("что такое ","").replace("что такое","")
	if(q.count(" ")>3):return ""
	url="https://ru.wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&search"+urllib.parse.urlencode([("",q)])+"&namespace=0&limit=10&suggest=true"
	ans=getJSON(url)
	try:
		tmp=ans[2][0]
		if(len(tmp)<25 or tmp.count("— ")<1):tmp=weakWiki(ans[3][0])
		return tmp
	except:
		return ""

def strongWikiEN(q):#Запрос к Википедии (англ.)
	if(debug):logD("Обращение к англоязычной Википедии")
	if(q.count(" ")>3):return ""
	url="https://en.wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&search"+urllib.parse.urlencode([("",q)])+"&namespace=0&limit=10&suggest=true"
	ans=getJSON(url)
	try:
		tmp=ans[2][0]
		if(len(tmp)<25 or tmp.count("— ")<1):tmp=weakWiki(ans[3][0])
		return tmp
	except:
		return ""

def rutoen(q):#TODO: Delete this stub
	if(debug):logD("Обращение к переводу на английский")
	return utils.rutoen(q)

def entoru(q):#TODO: Delete this stub
	if(debug):logD("Обращение к переводу на русский")
	return utils.entoru(q)

def getWikipediaAnswer(inp):#Запрос к Вики в любом виде
	if(utils.isEnglish(inp)>0.8):
		res=strongWikiEN(inp)
	else:
		res=strongWiki(inp)
	if(len(res)<1):
		res=strongWikiEN(utils.rutoen(inp))
		if(len(res)>5):res=utils.entoru(res)
	return res

###################################

def thequest(q):#Запрос к thequestion
	if(debug):logD("Обращение к html thequestion.ru")
	url="https://thequestion.ru/search/questions?limit=2&offset=0&q"+urllib.parse.urlencode([("",q)])+"&sort=date"
	ans=utils.getJSON(url)
	try:
		nurl=ans['items'][0]['absoluteUrl']
		time.sleep(0.84+random.random()*1)
		bts = urllib.request.urlopen(nurl)
		s=bts.read().decode('UTF-8')
		bts.close()
		startq="class=\"answer__text\"><p>"
		endq="</p></qml>"
		s=s[s.index(startq)+len(startq):]
		s=s[:s.index(endq)]
		s=s.replace("&#34;","\"").replace("<p>","\n").replace("</p>","").replace("<br>","\n")
		return s
	except Exception as e:
		logD(e)
		return ""

def otvetMailRu(q):#Запрос к mail.ru
	if(debug):logD("Обращение к ответам mail.ru")
	url="https://go.mail.ru/answer_json?ajax_id=21&q"+urllib.parse.urlencode([("",q)])+"&num=2&sf=0&dwh_pagetype=search&dwh_platform=web"
	try:
		ans=utils.getJSON(url)
		res=(ans['results'][0]['banswer']+"\n\n"+ans['results'][0]['answer']).replace("<b>","").replace("</b>","")
		if(res.count("!")+res.count(")")-res.count("(")+res.count("))")+res.count("!!")+res.count("!!!")>4):return ""
		return res
	except:
		return ""

def getLurkAnswer(inp):#Как с Вики, только с Лурком (рус.)
	if(debug):logD("Обращение к html Лурка")
	try:
#		url="https://lurkmore.co/"+inp
		url="https://lurkmore.co/index.php?title=Служебная:Search&search="+inp+"&go=Перейти"
		try:
			bashExec("wget -O /tmp/wikitest.html -U -q \""+ua+"\" -p \""+url+"\" 2>/dev/null")
		except:
			return " "
		fl=open("/tmp/wikitest.html")
		tmp=utils.wordInfo(inp)['root'].lower()
		if(len(tmp)==0):
			tmp=utils.getStartForm(inp).lower()
		lns=""
		for i in range(0,5000):
			try:
				lns=fl.readline()
				lnsl=lns.lower()
				if(lnsl.count('<meta name="description" content="')>0):
					lns=lns[len('<meta name="description" content="'):lns.rindex(".")+1]
					return lns
				elif(lnsl.count(tmp+" ")+lnsl.count(tmp+"\xa0")+lnsl.count(tmp+"</b>")>0 and lnsl.count("—")>0 and lnsl.count("title")<1 and lnsl.count("quote")<1):
					if(lns.index("—")-lns.index(tmp)>0):
						tmp2=lns.replace("<p>","").replace("<b>","").replace("</b>","").replace("\" />","").replace("&amp;#160;"," ")
						tmp2=tmp2[tmp2.index(tmp[1:])-1:tmp2.rindex(".")+1]
						if(len(tmp2)>4*len(tmp)):
							return tmp2
			except:
				if(debug):logD("Error after line "+lns)
		fl.close()
	except Exception as e:
		logD(str(e))
		return ""
	return ""

###################################

def getAnswerFromKnowledger(txt,context,lastmsg):#Получить ответ из Интернета (Лурк и Вики вместе)
	ismat=False######## АХТУНГ! МНОГО МАТА И ИНДУССКОГО КОДА! ПЕРЕД ИЗУЧЕНИЕМ СЕСТЬ И ВЫПИТЬ УСПОКОИТЕЛЬНОГО
	txt=txt.replace("Тру, ","").replace("Тру,","")#Вот сейчас серьёзно. Не стоит вскрывать эту функцию, вы молодые, шутливые...
	if(len(txt)<3):
		return 0.1,""
	txtarr=utils.str2arr(txt)
	lastmsgarr=[]
	try:
		lastmsgarr=utils.str2arr(lastmsg)
	except:
		pass
	for i in ['хуй', 'залупа', 'пенис', 'пепка', 'пеп', 'пизда', 'пиздец', 'бля', 'блять', 'блядь', 'заебись', 'ебу', 'хуя', 'кек']:
		if(i in lastmsgarr or i in txtarr or i in context):
			ismat=True
			break
	res=""
	if("что" in txtarr and "это" in txtarr and len(txtarr)==2):
		try:
			inp=context[-1]
			if(len(inp)<5):
				inp=context[-2]
			if(utils.getSemanticLoad(inp)<0.2):
				lastmsgsems=[]
				for i in lastmsgarr:
					lastmsgsems.append(utils.getSemanticLoad(i))
				inp=lastmsgarr[lastmsgsems.index(max(lastmsgsems))]
			if(ismat):
				res=getLurkAnswer(inp)
				if(len(res)<3):
					res=getWikipediaAnswer(inp)
			else:
				res=getWikipediaAnswer(inp)
				if(len(res)<3):
					res=getLurkAnswer(inp)
		except Exception as e:
			logD(e)
	if(len(res)>3):
		return 0.9,res
	if("что" in txtarr and "такое" in txtarr):
		inp=""
		for i in txtarr:
			if(i!="что" and i!="такое"):
				inp+=i+" "
		if(ismat):
			res=getLurkAnswer(inp)
			if(len(res)<3):
				res=getWikipediaAnswer(inp)
		else:
			res=getWikipediaAnswer(inp)
			if(len(res)<3):
				res=getLurkAnswer(inp)
	if(len(res)>3):
		return 0.9,res
	if("что" in txtarr and "значит" in txtarr):
		inp=""
		for i in txtarr:
			if(i!="что" and i!="значит"):
				inp+=i+" "
		if(ismat):
			res=getLurkAnswer(inp)
			if(len(res)<3):
				res=getWikipediaAnswer(inp)
		else:
			res=getWikipediaAnswer(inp)
			if(len(res)<3):
				res=getLurkAnswer(inp)
	if(len(res)>3):
		return 0.9,res
	if("что" in txtarr and "есть" in txtarr):
		inp=""
		for i in txtarr:
			if(i!="что" and i!="есть"):
				inp+=i+" "
		if(ismat):
			res=getLurkAnswer(inp)
			if(len(res)<3):
				res=getWikipediaAnswer(inp)
		else:
			res=getWikipediaAnswer(inp)
			if(len(res)<3):
				res=getLurkAnswer(inp)
	if(len(res)>3):
		return 0.9,res
	if("поясни" in txtarr and "за" in txtarr):
		inp=""
		for i in txtarr:
			if(i!="поясни" and i!="за"):
				inp+=i+" "
		if(ismat):
			res=getLurkAnswer(inp)
			if(len(res)<3):
				res=getWikipediaAnswer(inp)
		else:
			res=getWikipediaAnswer(inp)
			if(len(res)<3):
				res=getLurkAnswer(inp)
	if(len(res)>3):
		return 0.9,res
	if("кто" in txtarr and "такой" in txtarr):
		inp=""
		for i in txtarr:
			if(i!="кто" and i!="такой"):
				inp+=i+" "
		if(ismat):
			res=getLurkAnswer(inp)
			if(len(res)<3):
				res=getWikipediaAnswer(inp)
		else:
			res=getWikipediaAnswer(inp)
			if(len(res)<3):
				res=getLurkAnswer(inp)
	if(len(res)>3):
		return 0.9,res
	if("что" in txtarr and "будет" in txtarr and "если" in txtarr):
		res=thequest(txt)
		if(res.count("<theq-answer")>0):
			res=res[:res.index("<theq-answer")]
		if(len(res)<3):
			res=otvetMailRu(inp)
		res=res.replace("<strong>","").replace("</strong>","").replace("<i>","").replace("</i>","").replace("</span>","").replace("<a href=\"","").replace("target=\"_blank\"","").replace("</a>","")
	if(len(res)>3):
		return 0.9,res
	if(int("кто" in txtarr)+int("что" in txtarr)+2*(txt.count("проинтегрир")+txt.count("продифференц"))+txt.count("зна")+txt[-2:].count("?")>1):
		try:
			res=getWolframRU(txt)
		except Exception as e:
			logD(e)
	if(len(res)>3):
		return 0.9,res
	return 0.1,"Я не знаю"

#TODO: Протестировать и реализовать функцию getAnsswerByDialsit(cont,dialsit), возвращающую (sc,ans,debuginfo)
