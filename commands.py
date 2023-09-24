from dis import dis
from time import sleep, perf_counter
import re
import alive_code
from importlib import reload as module_reload
from random import choice, randint, shuffle
from traceback import format_exc
from pickle import load, dump
WAIT_CHECKER_ASSING_AGAIN=False
import discum
from discum.utils.button import Buttoner
class Timeout(Exception) : pass
LOG_CHANNEL=None
def ready() :
	global fwrite, db, REPL
	from __main__ import fwrite, db, REPL, log_states
def dump_dict_into_dict(d1 : dict, d2 : dict, fix_values=False) :
	for i in d1 :
		if i not in d2 :
			d2[i]=d1[i]
			continue
		elif type(d1[i])==dict :
			if str(type(d2[i])) not in ("<class 'dict'>", "<class 'replit.database.database.ObservedDict'>") : d2[i]=dict()
			dump_dict_into_dict(d1[i], d2[i])
		elif fix_values :
			d2[i]=d1[i]
def getMessage(bot, channelid, messageid) :
	return list(bot.getMessage(channelid, messageid).json())[0]
def getButtons(message, exclude_disabled=False) :
	for component in message["components"] :
		if component["type"]==1 :
			buttons=[]
			for button in component["components"] :
				if button["type"]==2 and ("disabled" not in button or not exclude_disabled) :
					if "label" in button : buttons.append(button["label"])
					elif "emoji" in button : buttons.append(button["emoji"]["name"])
			return buttons
			return [button["label"] for button in component["components"] if button["type"]==2 and ("disabled" not in button or not exclude_disabled)]
	return []
def refreshMessage(bot : discum.Client, message) :
	message=list(bot.getMessage(message["channel_id"], message["id"]).json())[0]
	if message is None : fwrite("Refreshed message then it turned out to be blank", "YELLOW")
	return message
def pressButton(bot : discum.Client, message, target, using_emoji=False, refresh_afterwards=False) :
	buts = Buttoner(message["components"])
	if type(target)==str : buttons_name=target
	elif type(target)==int : 
		target=getButtons(message)[target]
	else : raise Exception("Invalid button type")
	if using_emoji : data=buts.getButton(emojiName=target)
	else : data=buts.getButton(target)
	if "guild_id" in message : guild_id=message["guild_id"]
	else :
		try : guild_id=message["message_reference"]["guild_id"] # if there is a referenced message then the guild id will only exist there
		except : guild_id = None
	pressresponce=bot.click(
		message["author"]["id"],
		channelID=message["channel_id"],
		guildID=guild_id,
		messageID=message["id"],
		messageFlags=message["flags"],
		data=data,
	)
	if refresh_afterwards :
		sleep(2)
		return refreshMessage(bot, message)
	return pressresponce
def send_as_file(bot, channel, text) : #sends str as a txt file
	with open("tmp.txt", "w") as f :
		f.write(text)
	return bot.sendFile(channel, "tmp.txt")
def wait_checker(m, bot) :
	bot_data=bot.userData[69]
	for check_id in bot_data.message_checks :
		#print("going to try on one")
		if bot_data.message_checks[check_id]["function"](bot, m) :
			bot_data.message_checks[check_id]["result"] = m
		else :
			if WAIT_CHECKER_ASSING_AGAIN :
				print("message with content : {} didn't meet requirements".format(m["content"]))
def wait_for_message(check, bot, timeout=10, channel=None, raise_on_timeout=False) :
	bot_data=bot.userData[69]
	check_id=randint(1, 1000000)//1
	while check_id in bot_data.message_checks :
		check_id=randint(1, 1000000)//1
	bot_data.message_checks[check_id]={"function" : check, "result" : None}
	a=perf_counter()
	while perf_counter()-a<timeout :
		if bot_data.message_checks[check_id]["result"] is not None :
			c=bot_data.message_checks[check_id]["result"]
			del bot_data.message_checks[check_id]
			return c
	del bot_data.message_checks[check_id]
	if raise_on_timeout : raise Timeout
	return "timeout"
def send_then_wait(check, bot, send_channel, send_text, timeout=10, channel=None, raise_on_timeout=False) :
	bot_data=bot.userData[69]
	check_id=randint(1, 1000000)//1
	while check_id in bot_data.message_checks :
		check_id=randint(1, 1000000)//1
	bot_data.message_checks[check_id]={"function" : check, "result" : None}
	a=perf_counter()
	bot.sendMessage(send_channel, send_text)
	while perf_counter()-a<timeout :
		if bot_data.message_checks[check_id]["result"] is not None :
			c=bot_data.message_checks[check_id]["result"]
			del bot_data.message_checks[check_id]
			return c
	del bot_data.message_checks[check_id]
	if raise_on_timeout : raise Timeout
	return "timeout"
def get_refreshed(bot, id : str) :
	if type(id)==dict : id=id["id"]
	return bot.userData[69].messages_to_edit_refresh[id]
def start_refreshing(bot, message : str | dict) :
	bot_data=bot.userData[69]
	if type(message)==dict : id=message["id"]
	elif type(message)==str : id=message
	bot_data.messages_to_edit_refresh[id]=message

class user_commands :
	def execute_alive_code(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		module_reload(alive_code)
		alive_code.ass_function(bot, message, args_and_data, db)
	def evaluated_send(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		try :
			t=str(eval(args_and_data[1]))
		except :
			t=str(format_exc())
		bot.sendMessage(LOG_CHANNEL, t)
	def backup_db(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		u=dict(db)
		with open("db backup.ass", "bw") as f :
			dump(u, f)
		if "-send-too" in args_and_data[0] :
			bot.sendFile(LOG_CHANNEL, "db backup.ass")
		else :
			bot.addReaction(message["channel_id"], message["id"], "✅")
		return True
	def send_logs(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		#with open("FWRITE LOG.txt", "r") as f :
		#	all_log=f.read()
		if REPL :
			with open("FWRITE LOG.txt", "w") as f :
				f.write(str(db["log"]))
		bot.sendFile(message["channel_id"], "FWRITE LOG.txt")
	def clear_logs(bot, message, args) :
		if REPL : db["log"]=""
		else :
			with open("FWRITE LOG.txt", "w") as f : f.write("")
	def send_open_logs(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		#with open("FWRITE LOG.txt", "r") as f :
		#	all_log=f.read()
		if REPL :
			with open("open logger.txt", "w") as f :
				f.write(str(db["open logger"]))
		bot.sendFile(LOG_CHANNEL, "open logger.txt")
	def all_terminate(bot : discum.Client, message, args_and_data) :
		db["online"]=False
		import os, signal
		os.kill(os.getpid(), signal.SIGTERM)
	def test(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		bot.sendMessage(message["channel_id"], "hello world")
	def send(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		if len(args_and_data[0])<3 and len(args_and_data)>1 :
			channel_id=message["channel_id"]
		elif args_and_data[0][2]=="here" : channel_id=message["channel_id"]
		else :
			try : channel_id=str(int(args_and_data[0][2]))
			except :
				try :channel_id=db["saved channels"][args_and_data[0][2]]
				except : channel_id=LOG_CHANNEL
		if len(args_and_data)==1 : message_content=" ".join(args_and_data[0][3:])
		else : message_content="\n".join(args_and_data[1:])
		m=bot.sendMessage(channel_id, message_content)
		if "-nfb" not in args_and_data[0] :
			sleep(1.5)
			try : message["content"]
			except :
				bot.addReaction(message["channel_id"], message["id"], "❌")
				return format_exc()
			bot.addReaction(message["channel_id"], message["id"], "✅")
			return True
	def reply(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		if len(args_and_data[0])<4 and len(args_and_data)>1 :
			channel_id=message["channel_id"]
		else :
			try : channel_id=str(int(args_and_data[0][2]))
			except :
				try :channel_id=db["saved channels"][args_and_data[0][2]]
				except : raise Exception("Couldn't find that channel")
		replied_message=str(int(args_and_data[0][3]))
		if len(args_and_data)==1 : cc=" ".join(args_and_data[0][4:])
		else : cc="\n".join(args_and_data[1:])
		m=bot.reply(channel_id, replied_message, cc)
		if "-nfb" not in args_and_data[0] :
			try : message["content"]
			except :
				bot.addReaction(message["channel_id"], message["id"], "❌")
				return format_exc()
			bot.addReaction(message["channel_id"], message["id"], "✅")
	def change_my_prefix(bot : discum.Client, message, args_and_data) :
		pass
	def add_saved_channel(bot : discum.Client, message, args_and_data) :
		db["saved channels"][args_and_data[0][2]]=args_and_data[0][3]
		bot.addReaction(message["channel_id"], message["id"], "✅")
	def count(bot : discum.Client, message, args_and_data) :
		bot_data=bot.userData[69]
		if args_and_data[0][2]=="off" :
			db["count"]=0
			return
		target_channel, startt, endd = args_and_data[0][2:5]
		startt, endd=int(startt), int(endd)
		db["count"]=1
		for i in range(startt, endd) :
			sleep(5)
			if db["count"] : p=bot.sendMessage(target_channel, str(i))
			else : break
			p=dict(p.json())
			try : p["id"]
			except : raise Exception(f"Couldn't send the count message #{str(i)}")