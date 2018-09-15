import os

def parseFile(fname):
	flr=open(fname,"r")
	lns=flr.readlines()
	flr.close()
	res=[]
	for i in lns:
		if("Dialogue" in i[:9]):
			try:
				arr=i[i.index("0000,0000,0000,,")+len("0000,0000,0000,,"):]
				if('{' in arr):arr=arr[arr.index("}")+1:]
				res.append(arr)
			except:
				pass
	return res

filelist=os.listdir()

fl=open("resultphrases","w")
for i in filelist:
	if(i[-4:]==".ass"):
		print(i)
		lns=parseFile(i)
		ttt=fl.write('\n\n')
		for l in lns:
			ttt=fl.write(l)

fl.close()
