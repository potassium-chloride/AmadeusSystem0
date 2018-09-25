import subprocess,re,threading
import speech_recognition as sr
import time
def ttt():
	return time.strftime("[%H:%M:%S]: ")

reg0=re.compile('\w*[\w\-\']\w*')#re.compile('\w\w*')
def str2arr(txt):
	arr=re.findall(reg0,txt)
	while(arr.count("-")>0):
		arr.pop(arr.index("-"))
	return arr

#Google Speech Recognition
recognizer = sr.Recognizer()
#recognizer.non_speaking_duration=0.6
#recognizer.energy_threshold=500
microphone = sr.Microphone()
def checkNoise():
	global microphone,recognizer
	print("Замер уровня шума...")
	with microphone as source:
		recognizer.adjust_for_ambient_noise(source)

checkNoise()

audiodata=None
isGetSpeech=False
maxduration=10#Максимальная длина аудиозаписи в секундах, большое значение вызывает лаги распознавателя гугла

def bgListener():
	global microphone,audiodata,isGetSpeech
	while(True):
		with microphone as source:
			audiodata = recognizer.listen(source)
		dur=len(audiodata.frame_data)/audiodata.sample_rate/audiodata.sample_width
		if(dur>maxduration):
			audiodata.frame_data=audiodata.frame_data[-maxduration*audiodata.sample_rate*audiodata.sample_width:]
#			print("Patch big audio")
#		print("Knock")
		if(isGetSpeech):
			print("Stop")
			isGetSpeech=False
			txt,score=getSpeech()
			print("Recognized")
			if(score>0.5):onSpeech(txt)
			isGetSpeech=False

def getSpeech():#Возвращает распознанную строку. Произвольный текст лучше распознавать гуглом
	global recognizer,microphone,audiodata
	result=None
	try:
		print("Send request to Google...")
		result=recognizer.recognize_google(audiodata,language="ru_RU", show_all=True)
		print("Request to Google was sent success")
		conf=0.7
		try:conf=result['alternative'][0]['confidence']#Фиг знает, почему это поле не всегда существует
		except:pass
		tmpres=result['alternative'][0]['transcript']
		tmparr=tmpres.split(" ")
		tmpres=""
		for i in range(min(len(tmparr),2)):
			if(tmparr[i].count("уриц")==1):tmparr[i]="Курису"
		if(tmparr[0]=="Курису"):tmparr.pop(0)
		for i in tmparr:
			tmpres+=i+" "
		return tmpres[:-1],conf
	except Exception as e:
		pass
#		print(e)
#		print(result)
	return "",0

reg0=re.compile('\w\w*')
def str2arr(txt):
	arr=re.findall(reg0,txt)
	return arr

def onspeechstub(s):
	print(s)

onSpeech=onspeechstub#Функция, которой передаётся распознанная речь

#Sphinx Speech Recognition, пути к файлам надо патчить
#sphinxcmd='pocketsphinx_continuous -inmic yes -hmm zero_ru.cd_cont_4000 -dict lm_train.txt.dic -lm lm_train.txt.lm -samprate 16000 2>/dev/null'
sphinxcmd='pocketsphinx_continuous -inmic yes -hmm zero_ru.cd_cont_4000 -dict ru-kurisu.dic -lm ru-kurisu-min.lm -samprate 16000'# 2>/dev/null'
def mainloop():
	global isGetSpeech
	t = threading.Thread(target=bgListener)
	t.daemon = True
	t.start()#Теперь он будет слушать в фоне
	proc=subprocess.Popen(sphinxcmd,shell=True,stdout=subprocess.PIPE)
	isStart=False
	while proc.poll() is None:
		s = proc.stdout.readline().decode("utf-8")
		if(not isStart):
			print("Готов к работе")
			isStart=True
		if(len(s)<2):continue
		s=s.replace("\n","")
		arr=str2arr(s)
		if(len(arr)<1):continue
		if(len(arr)>=2 and arr[0] in ['привет','здравствуй','здравствуйте','окей'] and arr[1] in ['кристина','курису','ассистентка','ассистент','амадей','амадеус']):
			print("Listen...")
			isGetSpeech=True
		elif(len(arr)>=1 and arr[0] in ['кристина','курису','ассистентка','ассистент','амадей','амадеус']):
			print("Listen...")
			isGetSpeech=True

def mainloopAgressive():
	global microphone,audiodata,isGetSpeech
	while(True):
		with microphone as source:
			audiodata = recognizer.listen(source)
		dur=len(audiodata.frame_data)/audiodata.sample_rate/audiodata.sample_width
		if(dur>maxduration):
			audiodata.frame_data=audiodata.frame_data[-maxduration*audiodata.sample_rate*audiodata.sample_width:]
		txt,score=getSpeech()
		print(ttt()+"Recognized")
		if(score>0.5):onSpeech(txt)

