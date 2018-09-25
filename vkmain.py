#!/usr/bin/env python3
import os,sys,time,json,urllib.request,DialogManager,subprocess,APIkeys

def ttt():
	return time.strftime("[%H:%M:%S]: ")

#Получить JSON из адреса
def getJSON(url):
	time.sleep(0.34)
	bts = urllib.request.urlopen(url,timeout=40)
	s=bts.read().decode('UTF-8')
	bts.close()
	try:
		return json.loads(s)['response']
	except:
		print(ttt()+"Ошибка запроса! url="+url+";\n\t\tans="+s)
	return json.loads("{}")

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

def sendMsg(peer,text):
	if(len(text)<2):
		print(ttt()+"Длина сообщения менее 2, не отправляется")
		return
	getJSON(api_url+"messages.send?v=5.52&peer_id="+peer+"&message"+urllib.parse.urlencode([("",text)])+"&access_token="+token)

#Адрес VK API
api_url="https://api.vk.com/method/"
#LongPoll конфигурация
key="";
ts="";
server="";
isDoing=True
#access_token
#https://oauth.vk.com/authorize?client_id=5540662&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=864414&response_type=token&v=5.52&revoke=1
#Сергей Ломоносовский
my_id=373637602
token=APIkeys.vkToken

def getserv():
	bts = urllib.request.urlopen(api_url+"messages.getLongPollServer?v=5.52&access_token="+token)
	s=bts.read().decode('UTF-8')
	j=json.loads(s)['response']
	global key,ts,server
	key=j["key"]
	server=j["server"]
	ts=j['ts']
	bts.close()

def runlongpoll():
	try:
		global key,ts,server,isDoing
		bts = urllib.request.urlopen("https://"+server+"?act=a_check&key="+key+"&ts="+str(ts)+"&wait=25&mode=2&version=1")
		s=bts.read().decode('UTF-8')
		bts.close()
		if(s.find("failed")>-1):
			if(json.loads(s)["failed"]==1):
				print(ttt()+"\033[31mОшибка LongPoll сервера: утерена история\033[0m",file=sys.stderr)
				answerAll()#=========================================
				ts=json.loads(s)["ts"]
				return runlongpoll()
			print(ttt()+"\033[31mОшибка LongPoll сервера\033[0m",file=sys.stderr)
			time.sleep(0.2)
			getserv()
			return runlongpoll()
		return json.loads(s)
	except KeyboardInterrupt:
		print(ttt()+"Остановлено пользователем",file=sys.stderr)
		DialogManager.updateLocalDials()
		isDoing=False
		return json.loads('{"ts": 0, "updates": [[0]]}')
	except:
		print(ttt()+"\033[31mОшибка HTTP\033[0m",file=sys.stderr)
		time.sleep(0.2)
		DialogManager.updateLocalDials()
		return runlongpoll()

def serviceRec(j):
	txt=j[6]
	if(txt.count("рими код управления:")>0):
		peer=str(j[3])
		who=str(peer)
		try:who=j[7]['from']
		except:pass
		if(who!='169221285'):
			sendMsg(peer,"Код управления не принят. Ошибка: Вы не являетесь администратором Amadeus")
			return True
		cmd=txt[txt.index("рими код управления:")+len("рими код управления:"):]
		try:
			res=eval(cmd)
			if(res==None):sendMsg(peer,"Код управления принят. Команда выполнена.")
			elif(type(res)==str):sendMsg(peer,"Код управления принят. Результат: "+res)
			else:sendMsg(peer,"Код управления принят. Результат: "+str(res))
		except Exception as e:
			sendMsg(peer,"Код управления не принят. Ошибка: "+str(e))
		return True
	return False

def start_serv(onMsg):
	global isDoing,ts
	isDoing=True
	try:
		getserv()
		print(ttt()+"Запущено",file=sys.stderr)
		while isDoing:
			j=runlongpoll()
#			print(ttt()+str(j))
			ts=j['ts']
			arr=j['updates']
			for i in arr:
				ev=i[0]
				if(ev==4):
					print(ttt()+str(i))
					if( (i[2]//2)%2==0 ):
						markAsRead(str(i[1]))
						servtmp=False
						try:servtmp=serviceRec(i)
						except Exception as e:print(ttt(),e)
						if(not servtmp):
							try:onMessageRec(i[3],i[6])
							except Exception as e:print(ttt(),e)
		print(ttt()+"Завершено")
	except KeyboardInterrupt:
		print(time.strftime("[%H:%M:%S]: ")+"Остановлено пользователем",file=sys.stderr)
	except Exception as e:
		print(e)
		time.sleep(20)
		start_serv(onMsg)

def sendf(t,i):
	print(str(i)+"<-"+t)
	sendMsg(i.replace("_vk",""),t)
	return True

def sendTypingStatus(i):
	getJSON(api_url+"messages.setActivity?v=5.52&peer_id="+i.replace("_vk","")+"&access_token="+token)

def markAsRead(mid):
	getJSON(api_url+"messages.markAsRead?v=5.67&message_ids="+mid+"&access_token="+token)

def onMessageRec(uid,txt):
	d=DialogManager.getDialogById("_vk"+str(uid),sendfunction=sendf,typefunction=sendTypingStatus)
	d.pubScore=0.84
	isPriv=not (str(uid).count("2000000")>0)
	if(not isPriv):
		isPriv=(txt.count("Курису")+txt.count("Макис")+txt.lower().count("ассистент")+txt.count("Амадей")+txt.count("Амадеус")+txt.count("Куристина")>0)
	print(isPriv)
	d.getAnswer(txt.replace("<br>",""),"",isPrivate=isPriv)

start_serv(onMessageRec)
