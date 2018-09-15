#!/usr/bin/env python3
import os,sys,time,json,urllib.request,subprocess

def ttt():
	return time.strftime("[%H:%M:%S]: ")

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

#Получить JSON из адреса
def getJSON(url):
	time.sleep(0.4)
	bts = urllib.request.urlopen(url)
	s=bts.read().decode('UTF-8')
	bts.close()
	try:
		return json.loads(s)
	except:
		print(ttt()+"Ошибка запроса! url="+url+";\n\t\tans="+s)
	return json.loads("{}")

api_url="https://api.vk.com/method/"
token=bashExec("cat ~/bin/.token").replace("\n","")#У меня тут токен для вк лежит

def getConversations():
	j=getJSON(api_url+"messages.getConversations?v=5.80&offset=0&count=50&filter=all&extended=0&access_token="+token)
	ans=[]
	for i in j['response']['items']:
		ans.append(i['conversation']['peer']['id'])
	return ans

#dialids=getConversations()
#dialids=[2000000083,2000000037,2000000065,2000000059]
dialids=[2000000065]

def getHistory(peer):
	j=getJSON(api_url+"messages.getHistory?offset=0&count=200&peer_id="+str(peer)+"&rev=1&extended=0&v=5.80&access_token="+token)
	arr=j['response']['items']
	offset=200
	while(True):#Выгружаем всю переписку
		try:
			j=getJSON(api_url+"messages.getHistory?offset="+str(offset)+"&count=200&peer_id="+str(peer)+"&rev=1&extended=0&v=5.80&access_token="+token)
			for i in j['response']['items']:
				arr.append(i)
			offset+=200
			print(offset)
			if(len(j['response']['items'])<200):return arr
		except:return arr
	return arr

def getConversationNames(peer):
	j=getJSON(api_url+"messages.getConversationMembers?peer_id="+str(peer)+"&v=5.80&access_token="+token)
	mems=j['response']['profiles']
	res=[]
	for i in mems:
		res.append(i['first_name'].lower())
		res.append(i['last_name'].lower())
	return res

import re,pymorphy2
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
		print("Morph error:",e)
	return w

reg0=re.compile('\w*[\w\-\']\w*')#re.compile('\w\w*')
def str2arr(txt):
	arr=re.findall(reg0,txt)
	while(arr.count("-")>0):
		arr.pop(arr.index("-"))
	return arr

def isExistnames(txt,nms):
	sym="ЙЦУКЕНГШЩЗХФЫВАПРОЛДЖЭЯЧСМИТЬQWERTYUIOPASDFGHJKLZXCVBNM"
	for i in range(2,len(txt)):
		if(txt[i] in sym):
			if( not '.' in txt[i-2:i]): return True
	arr=str2arr(txt)
	for i in arr:
		if(getStartForm(i) in nms):
			return True
	return False

def histToDialsits(hist,nms):
	dialsit=['']
	lastsender=-1
	lastdate=0
	for m in hist:
		snder=m['from_id']
		txt=m['text']
		dt=m['date']
		if(dt-lastdate>1900):
			if(dialsit[-1]!=''):dialsit.append('')
		lastdate=dt
		if(len(m['fwd_messages'])>0 or len(m['attachments'])>0 or isExistnames(txt,nms)):
			if(dialsit[-1]!=''):dialsit.append('')
			lastsender=-1
			lastdate=0
			continue
		if(snder==lastsender):dialsit[-1]+="/pause "+txt.replace("\n","\\n")
		else:dialsit.append(txt.replace("\n","\\n"))
		lastsender=snder
	dialsit.append('')
	for i in range(1,len(dialsit)-1):
		if(len(dialsit[i-1])==0 and len(dialsit[i+1])==0):dialsit[i]=''
	newdialsit=[dialsit[0]]
	for i in range(1,len(dialsit)):
		if(len(dialsit[i-1])==0 and len(dialsit[i])==0):continue
		newdialsit.append(dialsit[i])
	return newdialsit

fl=open("saveddialogs.txt","w")
for p in dialids:
	nms=getConversationNames(p)
	hist=getHistory(p)
	dial=histToDialsits(hist,nms)
	print(p)
	for i in dial:
		fl.write(i+"\n")
	fl.flush()

fl.close()

