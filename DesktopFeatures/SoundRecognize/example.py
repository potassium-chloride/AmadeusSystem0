#!/usr/bin/env python3
import subprocess,parser

def bashExec(q):
	return subprocess.check_output(q,shell=True).decode("UTF-8")

def onSpeechRec(s):
	print("Text: "+s)
	s=s.lower()
	if("тиша" in s):bashExec("xdotool key XF86AudioLowerVolume")
	if("тише" in s):bashExec("xdotool key XF86AudioLowerVolume")
	if("тихо" in s):bashExec("xdotool key XF86AudioLowerVolume")
	if("громко" in s):bashExec("xdotool key XF86AudioRaiseVolume")
	if("громче" in s):bashExec("xdotool key XF86AudioRaiseVolume")
	if("стоп" in s):bashExec("xdotool key XF86AudioPause")


parser.onSpeech=onSpeechRec

parser.mainloop()
