#!/usr/bin/env python3
import sys,subprocess,re

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

fl=open(sys.argv[1],"r")
lns=fl.readlines()
fl.close()

reg0=re.compile('\w\w*')
def str2arr(txt):
	arr=re.findall(reg0,txt)
	return arr

allwords=[]

for i in lns:
	if(len(i)==0):continue
	words=str2arr(i)
	for w in words:
		w=w.lower()
		if(w in allwords):continue
		allwords.append(w)
		try:
			tmp=bashExec("cat ru-full.dic | grep \""+w+" \"").split("\n")
			for k in tmp:
				if(len(k)>0 and k[:k.index(" ")].replace("(2)","")==w):
					bashExec("echo \""+k+"\" >> "+sys.argv[1]+".dic")
					break
		except KeyboardInterrupt:sys.exit(0)
		except Exception as e:print("Bad word:",w,e)
	if(len(words)>0):
		tmp=str(words)[1:-1].replace("\n","").replace("\"","").replace("\'","").replace(","," ").replace("  "," ")
		bashExec("echo \"<s> "+tmp+" </s>\" >> .tmp.txt")

bashExec("text2wfreq < .tmp.txt | wfreq2vocab > .tmp.vocab")
bashExec("text2idngram -vocab .tmp.vocab -idngram .tmp.idngram < .tmp.txt")
bashExec("idngram2lm -vocab_type 0 -idngram .tmp.idngram -vocab .tmp.vocab -arpa "+sys.argv[1]+".lm")
bashExec("rm .tmp.txt")
bashExec("rm .tmp.vocab")
bashExec("rm .tmp.idngram")

