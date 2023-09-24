import discum
from time import sleep
from commands import *
def ass_function(bot : discum.Client, message, args_and_data, db) :
	bot_data=bot.userData[69]
	t=[]
	t.append(getMessage(bot, "988688067797872651", "1128742816261079120"))
	sleep(2)
	t.append(getMessage(bot, "988688067797872651", "1128743331028025364"))
	sleep(2)
	t.append(getMessage(bot, "988688067797872651", "1128743446958571550"))
	sleep(2)
	t.append(getMessage(bot, "988688067797872651", "1128743710755131392"))
	sleep(2)
	t.append(getMessage(bot, "988688067797872651", "1128743877571002509"))
	sleep(2)
	tt=["idle", "question", "q answered right", "actions", "tell joke prompt"]
	ttt="\n\n".join([tt[i]+" : \n"+str(t[i]) for i in range(len(t))])
	with open("tmp.txt", "w") as f : f.write(ttt)
	return True