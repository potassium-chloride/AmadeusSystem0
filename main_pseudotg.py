#!/usr/bin/env python3
import os,sys,time,json,urllib.request,subprocess,random
import DialogManager as dm

def ttt():
	return time.strftime("[%H:%M:%S]: ")

#Получить JSON из адреса
def getJSON(url):
	bts = urllib.request.urlopen(url,timeout=50)
	s=bts.read().decode('UTF-8')
	bts.close()
	try:
		return json.loads(s)
	except:
		print(ttt()+"Ошибка запроса! url="+url+";\n\t\tans="+s)
	return json.loads("{}")

#Адрес VK API
api_url="http://volna2017msu.000webhostapp.com/tgapi"
import APIkeys
token=APIkeys.tgToken
offset=-2

def hotplugKurisu():
	dm.kurisu=dm.GetAnswerFromFile("data/kurisuphrases")
	sendMsg(205176061,"Выполнено")

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

def sendMsg(peer,text,ttl=10):
	if(len(text)<1):
		print(ttt()+"Длина сообщения менее 1, не отправляется")
		return
	if(ttl<0):
		print(ttt()+"Превышено число попыток отправки сообщения, не отправляется")
		return		
	time.sleep(0.2)
	try:
		getJSON(api_url+"/sendMessage.php?token="+token+"&peer="+str(peer)+"&text"+urllib.parse.urlencode([("",text.replace("\n","\r\n"))]))
	except Exception as e:
		sendMsg(peer,text,ttl=ttl-1)
		print(e)

def sendPhoto(peer,url,ttl=10):
	if(len(url)<5):
		print(ttt()+"Длина url менее 2, не отправляется")
		return
	if(ttl<0):
		print(ttt()+"Превышено число попыток отправки сообщения, не отправляется")
		return		
	time.sleep(0.2)
	try:
		getJSON(api_url+"/sendPhoto.php?token="+token+"&peer="+str(peer)+"&photo="+url)
	except Exception as e:
		sendPhoto(peer,url,ttl=ttl-1)
		print(e)

def sendSticker(peer,ttl=10):
	try:
		if(ttl<0):
			print("Too many calls")
			return
		getJSON(api_url+"/sendSticker.php?token="+token+"&peer="+str(peer)+"&disable_notification=1&sticker="+random.choice(['CAADAgAD-wADxx0jA2H_bs8eWmg2Ag','CAADAgAD5wADxx0jAz4NLs1Vl8AjAg','CAADAgAD-QADxx0jA3Ys-h31PxSVAg','CAADAgAD7QADxx0jA19EaPUogWpwAg']))
	except Exception as e:
		print(e)
		sendSticker(peer,ttl=ttl-1)

sendSticker(205176061)

def sendTypingStatus(peer):
	try:
		getJSON(api_url+"/sendChatAction.php?token="+token+"&peer="+str(peer)+"&action=typing")
	except Exception as e:
		print(e)

def getUpdates(offset=-2):
	return getJSON(api_url+"/getUpdates.php?token="+token+"&limit=2&offset="+str(offset)+"&timeout=25")['result']

seen=[]

def recognizeVoice(fid):
	j=getJSON(api_url+"/getFile.php?token="+token+"&file_id="+file_id)
	url="https://api.telegram.org/file/bot"+token+"/"+j['result']['file_path']
	time.sleep(1)
	try:
		#https://t.me/socks?server=sreju5h4.spry.fail&port=1080&user=telegram&pass=telegram
		#bot.avinfo17.info:38157
		bashExec("curl --socks5 sreju5h4.spry.fail:1080 -U telegram:telegram \""+url+"\" > /tmp/voicemsg.ogg")
	except Exception as e:
		print(e)
		time.sleep(2)
		bashExec("curl --socks5 sreju5h4.spry.fail:1080 -U telegram:telegram \""+url+"\" > /tmp/voicemsg.ogg")
	bashExec("ffmpeg -y -i /tmp/voicemsg.ogg /tmp/voicemsg.wav 2>/dev/null")
	return bashExec("python ogg2text.py 2>/dev/null")

def recognizePicture(fid):
	j=getJSON(api_url+"/getFile.php?token="+token+"&file_id="+file_id)
	url="https://api.telegram.org/file/bot"+token+"/"+j['result']['file_path']
	time.sleep(1)
	try:
		#https://t.me/socks?server=sreju5h4.spry.fail&port=1080&user=telegram&pass=telegram
		#bot.avinfo17.info:38157
		bashExec("curl --socks5 sreju5h4.spry.fail:1080 -U telegram:telegram \""+url+"\" > /tmp/tgpic.jpg")
	except Exception as e:
		print(e)
		time.sleep(2)
		bashExec("curl --socks5 sreju5h4.spry.fail:1080 -U telegram:telegram \""+url+"\" > /tmp/tgpic.jpg")
	return bashExec("recognizefrompic.py /tmp/tgpic.jpg 2>/dev/null")

print(ttt()+"Start!")

def sendf(t,i):
	print(str(i)+"<-"+t)
	if(random.random()>0.5 and t in ["А как же я?","А про меня забыли?","Мне скучно(","Хэй!/pauseМеня не существует что ли?!"]):
		sendSticker(i)
	sendMsg(i,t)
	return True

lastrec=""

while True:
	j=[]
	try:
		j=getUpdates(offset)
	except KeyboardInterrupt:
		sys.exit(0)
	except Exception as e:
		print(e)
	sys.stdout.write(ttt()+"Get!\r")
	for i in j:
		try:
			msg_id=i['update_id']
			if(seen.count(msg_id)>0):continue
			else:seen.append(msg_id)
			offset=msg_id+1
			print(ttt()+"len(j)="+str(len(j)))
			txt=""
			isPrivate=True
			try:
				isPrivate=(i['message']['chat']['type']=='private')
			except Exception as e:
				print(e)
				print(i)
			peer=i['message']['chat']['id']
			if(peer>0):
				sendTypingStatus(peer)
			try:
				txt=i['message']['text']
			except:
				try:
					txt=i['message']['caption']
				except:
					pass
				print(i)
				try:
					ne=i['message']['new_chat_participant']
					sendMsg(peer,"Я Макисэ Курису. Рада познакомиться ^-^")
				except:
					pass
			isVoice=False
			try:
				if(len(txt)<1):
					file_id=i['message']['voice']['file_id']
					txt=recognizeVoice(file_id)
					isVoice=True
			except:
				pass
			try:
				file_id=i['message']['photo'][-1]['file_id']
				tmp="|||"+recognizePicture(file_id)
				if(len(tmp)>10):
					if(txt.lower().count("прочти")+txt.lower().count("текст")+txt.lower().count(" с ")+txt.lower().count("картин")+txt.lower().count("фот")+txt.lower().count("что")+txt.lower().count("здесь")+txt.lower().count("написано")>2):
						sendMsg(peer,tmp[3:])
					txt+=tmp
			except:
				pass
			print(ttt()+"Received: "+txt)
			if(txt.count("/")>0):
				print(i)
			if(txt.count("/help")>0):
				sendMsg(peer,"Бот для развлечения, практического смысла не имеет или почти не имеет. Возможно, когда-нибудь научится имитировать Курису Макисэ")
				continue
			if(peer==205176061 and txt.lower().count("перезапуск модуля курису")>0):
				hotplugKurisu()
			if(peer==205176061 and txt.count("Выполнить: ")>0):
				try:
					exec("res="+txt.replace("Выполнить: ","").replace("\n",""))
					if(type(res)==type(None)):
						sendMsg(205176061,"Выполнено")
					elif(type(res)==str):
						sendMsg(205176061,res)
					else:
						sendMsg(205176061,str(res))
				except Exception as exc:
					sendMsg(205176061,"Error: "+exc)
				continue
			if(txt.count("Курису")+txt.count("Макисэ")+txt.count("Макисе")+txt.count("Ассистент")+txt.count("Асистент")+txt.count("Амадеус")>0):
				isPrivate=True
				txt=txt.replace("Курису","").replace("Макисэ","").replace("Макисе","").replace("Ассистент","").replace("Асистент","").replace("Амадеус","")
			if(txt.count("Kurisu")+txt.count("Makise")+txt.count("Assistent")+txt.count("Amadeus")>0):
				isPrivate=True
				txt=txt.replace("Kurisu","").replace("Makise","").replace("Assistent","").replace("Amadeus","")
			if(txt.replace(" ","").replace("ё","е").replace("\n","").lower().count("еще")==1 and len(txt)<6):
				txt=lastrec
			else:
				lastrec=txt
			dm.getDialogById(peer,sendfunction=sendf,typefunction=sendTypingStatus).getAnswer(txt,"",isPrivate=isPrivate)
		except Exception as e:
			print(e)
	if(random.random()<0.000545):
		try:
			if(random.random()>0.6):
				random.choice(dm.dialogs).getAnswer("го цитату",isVoice=False,isPrivate=True)
			else:
				sendSticker(random.choice(dm.dialogids))
		except Exception as e:
			print(e)
	time.sleep(2)

