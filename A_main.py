from copy import copy
from string_to_cmd import str_to_cmd
from traceback import format_exc
import threading
from pickle import load
from time import sleep
from datetime import datetime, timedelta
import os
from random import randint
from dotenv import load_dotenv
from amiinrepl import REPL
from json import loads as json_loads
ONLANIZE=False
load_dotenv()
if REPL :
	os.system("pip install --upgrade --force-reinstall git+https://github.com/Merubokkusu/Discord-S.C.U.M.git#egg=discum")
import discum
from discum.utils.button import Buttoner
import commands
class empty_instance :
	def __init__(self) : pass
DATE_STR_FORMAT="%d/%m/%Y, %H:%M:%S"
LOG_STATES=("GREEN", "YELLOW", "RED", "WHITE")
def read_json(file_name) :
	with open(f"{file_name}.json", "r") as f : return json_loads(f.read())
def fwrite(log, state=LOG_STATES[0], print_statement=None) :
	if print_statement is None and state in ("YELLOW", "RED") : print_statement=True
	log_statement=" : ".join([datetime.now().strftime(DATE_STR_FORMAT), state, log])
	if print_statement : print(log_statement)
	if REPL : db["log"]+="\n"+log_statement
	else :
		with open("FWRITE LOG.txt", "r", encoding="utf-8") as f :
			t=f.read()
		with open("FWRITE LOG.txt", "w", encoding="utf-8") as f :
			f.write(t+"\n"+log_statement)
	return True
#commands.ready()
commands.fwrite, commands.REPL=fwrite, REPL
def load_defualt_db() : return read_json("settings")
def fix_db(dbb) :
	defaultdb=load_defualt_db()
	try : commands.dump_dict_into_dict(defaultdb, dbb)
	except : fwrite(format_exc(), LOG_STATES[2])
def get_db_file(fix_with_default_one=True) :
	with open("db backup.ass", "br") as f :
		lastdb=load(f)
		if fix_with_default_one :
			fix_db(lastdb)
		return lastdb
def upload_dbfile_to_repl(repldb) :
	rr=get_db_file()
	repldb.set_bulk(rr)
if REPL :
	from replit import db
	from keep_alive import keep_alive
	keep_alive()
	if "state" not in db :
		db.clear()
		upload_dbfile_to_repl(db)
	else : fix_db(db)

else :
	try :
		db=get_db_file()
		fwrite("loaded pickle db file")
	except :
		db=load_defualt_db()
		fwrite("loaded default db file", LOG_STATES[1])
#db loaded
commands.db=db
LOG_CHANNEL=db["log channel"]
commands.LOG_CHANNEL=LOG_CHANNEL
if ONLANIZE : db["online"]=True
if not db["online"] : exit()
if REPL :
	db["open logger"] +=datetime.now().strftime(DATE_STR_FORMAT)
else :
	with open("open logger.txt", "r") as f : asdasd=f.read()
	with open("open logger.txt", "w") as f : f.write(asdasd+datetime.now().strftime(DATE_STR_FORMAT))
	
commands.db=db
if REPL : tokenlist=eval(os.environ["token"])
else : tokenlist=os.getenv("token")
repl_gateway={"reactions on messages" : []}
commands.repl_gateway=repl_gateway
def import_discum_from_github() :
	import os
	os.system("pip install --upgrade --force-reinstall git+https://github.com/Merubokkusu/Discord-S.C.U.M.git#egg=discum")
	import discum
class sb : #not put into use yet
	def __init__(self, bot : discum.Client, index) -> None:
		self.bot=bot
		self.INDEX=index
		self.message_checks={}
		self.listened_channels={}
		self.messages_to_edit_refresh={}
		self.karuta_execution_channel=db["settings"]["karuta execution channel"]
		self.PREFIX=db["self call"]
		if self.PREFIX not in db : db[self.PREFIX]={}
		self.OFFICE=None#db[self.PREFIX].get("OFFICEID", None)
		self.public_usage=False
		try :
			self.USERNAME=db[self.PREFIX]["username"]
			self.SBID=db[self.PREFIX]["sbid"]
		except :
			self.SBID=None
			self.USERNAME=None
		self.loop_count=0
def initialize_bot_info(bot_data, index) :
	bot_data.INDEX=index
	bot_data.message_checks={}
	bot_data.listened_channels={}
	bot_data.messages_to_edit_refresh={}
	bot_data.PREFIX=db["self call"]
	db[bot_data.PREFIX]={}
	bot_data.OFFICE=None#db[bot_data.PREFIX].get("OFFICEID", None)
	bot_data.public_usage=False
	try :
		bot_data.USERNAME=db[bot_data.PREFIX]["username"]
		bot_data.SBID=db[bot_data.PREFIX]["sbid"]
	except :
		bot_data.SBID=None
		bot_data.USERNAME=None
	bot_data.loop_count=0




def fetch_command(bot, message, splitted_content) :
	try :
		command=getattr(commands.user_commands, splitted_content[0][1].lower())
	except AttributeError : return False
	try :
		status=command(bot, message, splitted_content)
		stat=status
		fwrite("executed command {} from message ({}, {}) with success".format(splitted_content[0][1].lower(), message["channel_id"], message["id"]), print_statement=True)
	except :
		status=format_exc()
		stat=False
		status2=status+" // command text : "+message["author"]["username"]+ " : "+message["content"]
		fwrite(status2, LOG_STATES[2], True)
	if ("--feedback" in splitted_content[0]) or ("--show-exception" in splitted_content[0]) :
		bot.sendMessage(message["channel_id"], str(status))
	return stat
def message_saver(resp, bot) :
	if resp.event.message_deleted :
		message=resp.parsed.auto()
		print(message)
		t=f"Deleted message :\n\tAuthor : {message['author']['username']}\n\tAuthor id : {message['author']['id']}\n\tcontent :\n\t{message['content']}\n"
		if message["channel_id"] in db["channels to track"] :
			bot.sendMessage(LOG_CHANNEL, t)
		print(t)
def message_update_tracker(resp, bot) :
	bot_data=bot.userData[69]
	if resp.event.message_updated :
		message=resp.parsed.auto()
		if message["id"] in bot_data.messages_to_edit_refresh :
			bot_data.messages_to_edit_refresh[message["id"]]=message
def command_handling(resp, bot, delayed=False) :
	bot_data=bot.userData[69]
	if resp.event.message :
		message=resp.parsed.auto()
		if len(message["content"])==0 : return
		if message["author"]["id"] not in db["myself"] and not bot_data.public_usage : return
		splitted_content=message["content"].splitlines()
		splitted_content[0]=str_to_cmd(splitted_content[0])
		if len(splitted_content[0])>1 :
			if splitted_content[0][0] in (bot_data.PREFIX, db["multiple call"], db["all call"]) :
				for i in splitted_content[0] :
					if i.startswith("--inds:") :
						list_of_accs=eval(i[7:])
						break
					else :
						list_of_accs=[]
				if (bot_data.INDEX not in list_of_accs) and (bot_data.PREFIX not in list_of_accs) and (splitted_content[0][0] not in (bot_data.PREFIX, db["all call"])): return
				if not delayed :
					for i in splitted_content[0] :
						if i.startswith("--after:") :
							commands.functions_to_do.append({"arguments" : (resp, bot, True), "datetime" : datetime.now()+timedelta(i[8:])})
							return
				
				
				
				if splitted_content[0][1].lower()=="exec" :
					print("exec message recieved")
					if "--no-feedback" in splitted_content[0] or "-nf" in splitted_content[0]:
						done_responce=False
						fail_responce=False
					elif "--no-done" in splitted_content[0] or "-nd" in splitted_content[0]:
						done_responce=False
						fail_responce=True
					else :
						done_responce=True
						fail_responce=True
					d=message["content"].splitlines()
					lines_to_exec=""
					if d[-1]=="```" :
						for line in d[2:-1] : lines_to_exec+=line+"\n"
					else :
						for line in d[1:] : lines_to_exec+=line+"\n"
					try :
						exec(lines_to_exec)
						sleep(2)
						if done_responce : bot.sendMessage(message["channel_id"], "》done")
					except :
						print(format_exc())
						sleep(2)
						if fail_responce :
							if len(str(format_exc())) <2000 :
								bot.sendMessage(message["channel_id"], str(format_exc()))
							else :
								with open("tmp.txt", "w") as f : f.write(str(format_exc()))
								bot.sendFile(message["channel_id"], "tmp.txt")
				elif splitted_content[0][1].lower()=="multicommand" :
					for command in splitted_content[1:] :
						subpp=[str_to_cmd(command)]
						fetch_command(bot, message, subpp)
				else :
					fetch_command(bot, message, splitted_content)
#@bot.gateway.command
def hw2(resp, bot) :
	if resp.event.message:
		m = resp.parsed.auto()
		commands.wait_checker(m, bot)
#gateway commands appending :
client=discum.Client(token=tokenlist, log={"console":False, "file":False, "encoding":"utf-8"})
build_num = client._Client__super_properties['client_build_number']
client.userData[69]=empty_instance()
initialize_bot_info(client.userData[69], 0)
client.gateway.command({"function":command_handling, "params":{"bot":client}})
client.gateway.command({"function":hw2, "params":{"bot":client}})
client.gateway.command({"function":message_update_tracker, "params":{"bot":client}})
client.gateway.command({"function":message_saver, "params":{"bot":client}})



pressButton=commands.pressButton
getMessage=commands.getMessage
getButtons=commands.getButtons
refreshMessage=commands.refreshMessage

def gatewayRunner(bot, result, index):
	fwrite(f"Running a gatewawy {result} , {index}")
	#bot.gateway.run()
	bot.gateway.run(auto_reconnect=True)
	#commands.bots_data[bot.gateway.session.user] = bot
	try : result[index] = bot.gateway.session.user
	except :
		fwrite("user keyerror gateway", LOG_STATES[1], False)
result=[None]*1
thread = threading.Thread(target=gatewayRunner, args=(client , result, 0))
thread.start()
print("end of code")