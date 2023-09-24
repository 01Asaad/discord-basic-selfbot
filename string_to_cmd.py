from re import finditer, sub
def str_to_cmd(text) :
	r=list(finditer("<.+?>", text))
	ttt=sub("<.+?>","##",text)
	ttt=ttt.split(" ")
	newt=ttt
	hasshtags=0
	for word in range(len(newt)) :
		if newt[word] =="##" :
			newt[word]=r[hasshtags].group()[1:-1]
			hasshtags+=1
		#newt=re.sub("##",str(i.group())[1:-1],newt,count=1)
	return newt
if __name__=="__main__" :
	tt="dio <qw> erty blind pp potato <tomato cucmber >"
	print(str_to_cmd(tt))