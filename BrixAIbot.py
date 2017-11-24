#!/usr/bin/env python3

from telegram.ext import Updater
from telegram.ext import CommandHandler as CmdHndl
from telegram.ext import MessageHandler as MsgHndl
from telegram.ext import Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut,
		ChatMigrated, NetworkError)
import logging
import configparser as CfgPsr

from datetime import datetime
from time import localtime, strftime

from BrixAIUtils import VehicleCheck 
from BrixAIUtils import FSM
from BrixAIUtils import NoteTake

import re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument ('-p', '--path', type=str, help = 'path of root dir of notebook')
parser.add_argument ('-n', '--notebook', type=str, help = 'name of using notebook')
parser.add_argument ('-d', '--diary', type=str, help = 'name of using diary')
parser.add_argument ('-b', '--botname', type=str, help = 'name of bot')
parser.add_argument ('-c', '--config', type=str, help = 'path to config file that stores api token of the bog')
args = parser.parse_args()

Notebook = NoteTake.NoteBook (args.notebook, args.path)
Diary    = NoteTake.NoteBook (args.diary, args.path)

class ABot:
	#config_filename = '/etc/telegram-send.conf'
	config_filename = args.config
	
	act_name    = ""
	act_chat_id = ""
	act_bot     = None

	updater     = None 
	dispatcher  = None

	def error_cb (self, bot, update, error):
		try:
			raise error
		except Unauthorized:
			print ("Unautorized") 
		except BadRequest:
			print ("Malformed requests")
			print ("Unautorized") 
		except TimedOut:
			print ("Slow connection")
		except NetworkError:
			print ("Network error")
		except ChatMigrate as e:
			print ("Chat ID of group has changed") 
		except TelegramError:
			print ("Internal Telegram error")

	def respond (self, texts):
		if type(texts) is list:
			for idx, text in enumerate(texts):
				self.act_bot.send_message (self.act_chat_id, text = text)
		else:
			self.act_bot.send_message (self.act_chat_id, text = texts)

	def initialize (self, bot, update):
		self.act_chat_id = update.message.chat_id
		self.act_bot     = bot
	
	def greeting (self):
		h = datetime.now().time().hour
		if h >= 5 and h <= 12:
			greeting = "Good morning."
		elif h > 12 and h <= 17:
			greeting = "Good afternoon."
		elif h > 17 and h <= 21:
			greeting = "Good evening."
		else:
			greeting = "Greetings night owl."
	
		self.respond (greeting + " " + "My name is " + self.act_name)

	def live (self):
		self.updater.start_polling()
		self.updater.idle()
		self.respond ("I'm offline right now. Good bye.")

	def add_handler (self, hndl):
		self.dispatcher.add_handler (hndl)

	def __init__ (self, name = "BAI"):
		self.act_name = name 
		config = CfgPsr.ConfigParser ()
		config.read (self.config_filename)
		self.updater    = Updater(token=config['telegram']['token'])
		self.dispatcher = self.updater.dispatcher

		self.dispatcher.add_error_handler (self.error_cb)
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BAI_bot               = ABot (args.botname)


class BotAction (FSM.Action):
	def __init__ (self, action):
		FSM.Action.__init__ (self, action, "Bot")

BotAction.initialize = BotAction ("initialize")
BotAction.record     = BotAction ("record")
BotAction.end        = BotAction ("end")
BotAction.cancel     = BotAction ("cancel")

class Void (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Void")
	def run(self, input, args):
		print ("Void")
	def next(self, input, args):
		if input == BotAction.initialize:
			return ASys.init
		return self

class Init (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Init")
	def run(self, input, args):
		BAI_bot.initialize (args["bot"], args["update"])
		BAI_bot.greeting ()
		BAI_bot.respond ("I'm here to serve you")
	def next(self, input, args):
		if input == BotAction.record:
			if args['type'] == 'note':
				BAI_bot.respond ("Recording note. You can save it by /end with tags separated by comma.")
				return ASys.writingnote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.writingdiary
		BAI_bot.respond ("Very sorry, I don't have this function right now")
		return self

class Idle (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Idle")
	def run(self, input, args):
		BAI_bot.respond ("I'm here to serve you")
	def next(self, input, args):
		if input == BotAction.record:
			if args['type'] == 'note':
				BAI_bot.respond ("Recording note. You can save it by /end with tags separated by comma.")
				return ASys.writingnote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.writingdiary
		BAI_bot.respond ("Very sorry, I don't have this function right now")
		return self

class WritingNote (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WritingNote")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.end:
			record = NoteTake.NoteBook.shape_record (args['current_content'], args['current_tags'])
			Notebook.new_record (record)
			Notebook.store_notebook ()
			PA_sys.note_read_hndl[record['timestamp']] = CmdHndl (str(record['timestamp']), 
																														lambda bot, 
																														update, arg = record['timestamp'],
																														book = Notebook: show_record (book, arg))
			BAI_bot.add_handler (PA_sys.note_read_hndl [record['timestamp']])
			BAI_bot.respond ("Your note has been saved.")
			return ASys.idle
		elif input == BotAction.cancel:
			BAI_bot.respond ("Canceled")
			return ASys.idle
		BAI_bot.respond ("What do you want to do with current recording?")
		return self

class WritingDiary (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WritingDiary")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.end:
			record = NoteTake.NoteBook.shape_record (args['current_content'], args['current_tags'])
			Diary.new_record (record)
			Diary.store_notebook ()
			PA_sys.diary_read_hndl[record['timestamp']] = CmdHndl (str(record['timestamp']), 
																														 lambda bot,
																														 update, arg =
																														 record['timestamp'],
																														 book = Diary: show_record (book, arg))
			BAI_bot.add_handler (PA_sys.diary_read_hndl [record['timestamp']])
			BAI_bot.respond ("Your entry has been saved.")
			return ASys.idle
		elif input == BotAction.cancel:
			BAI_bot.respond ("Canceled")
			return ASys.idle
		BAI_bot.respond ("What do you want to do with current writing?")
		return self

def check_plate (bot, update, args):
	send_str = [] 
	if len(args) == 0:
		list_of_vi = VehicleCheck.check_violation ("51f-81420")
		if len(list_of_vi) != 0:
			for idx, report in enumerate(list_of_vi):
				s1 = 'Loi %d' %(idx + 1)
				s2 = 'Ngay vi pham: ' + report['date'].encode('latin-1').decode()
				s3 = 'Vi tri vi pham: ' + report['place'].encode('latin-1').decode()
				s4 = 'Loi vi pham: ' + report['description'].encode('latin-1').decode()
				s5 = 'Co quan xu ly: ' + report['dept'].encode('latin-1').decode()
				send_str.append('\n'.join([s1, s2, s3, s4, s5]))
		else:
			send_str.append('No moving violation')
	else:
		for pidx, plate in enumerate(args):
			BAI_bot.respond ("Bien so %s" %(plate))
			list_of_vi = VehicleCheck.check_violation (plate)
			if len(list_of_vi) != 0:
				for idx, report in enumerate(list_of_vi):
					s1 = 'Loi %d' %(idx + 1)
					s2 = 'Ngay vi pham: ' + report['date'].encode('latin-1').decode()
					s3 = 'Vi tri vi pham: ' + report['place'].encode('latin-1').decode()
					s4 = 'Loi vi pham: ' + report['description'].encode('latin-1').decode()
					s5 = 'Co quan xu ly: ' + report['dept'].encode('latin-1').decode()
					send_str.append('\n'.join([s1, s2, s3, s4, s5]))
			else:
				send_str.append('No moving violation')
	BAI_bot.respond (send_str)

def process_msg (bot, update):
	tag_re = re.compile(r"(\w+),,,")

	msg = update.message.text
	if (PA_sys.currentState == ASys.writingnote) or (PA_sys.currentState == ASys.writingdiary):
		PA_sys.current_tags.extend(map (lambda x: x.strip().lower(), tag_re.findall(msg)))
		PA_sys.current_tags = list(set(PA_sys.current_tags))
		PA_sys.current_content += tag_re.sub (r'\1', msg)
	else:
		BAI_bot.respond (["You said " + msg])

def show_records (book, args, All = False):
	if not All:
		preview_records (book, book.query_records (map(lambda x: x.strip().lower(), args)))

def preview_records (book, records_stamplist):
	for stamp in records_stamplist:
		record = book.records [stamp]
		msg = '/' + str(record['timestamp']) + '\n'
		msg += ','.join(record['tags']) + '\n'
		if len(record['content']) < 50:
			msg += record['content']
		else:
			msg += record['content'][0:50]
		BAI_bot.respond (msg)
	
def record2str (book, timestamp):
	record_time, tags, content = NoteTake.NoteBook.unshape_record (book.records[timestamp])
	msg = ''
	msg += strftime('%Y-%m-%d %H:%M:%S', localtime(record_time)) + '\n'
	msg += ', '.join(tags) + '\n'
	msg += content
	return msg

def show_record (book, timestamp):
	BAI_bot.respond (record2str(book, timestamp))


class ASys (FSM.StateMachine):
	def __init__(self):
		self.current_content = ''
		self.current_tags    = []
		FSM.StateMachine.__init__(self, ASys.void)
		
		# Adding handlers
		cmd_start_hndl        = CmdHndl ('start', self.initialize_bot)
		cmd_note_hndl         = CmdHndl ('note', self.note, pass_args = True)
		cmd_diary_hndl        = CmdHndl ('diary', self.diary, pass_args = True)
		cmd_end_hndl          = CmdHndl ('end', self.end, pass_args = True)
		cmd_cancel_hndl       = CmdHndl ('cancel', self.cancel)
		cmd_checkPlate_hndl   = CmdHndl ('check_plate', check_plate, pass_args = True)
		msg_hndl              = MsgHndl (Filters.text, process_msg)
		
		BAI_bot.add_handler (cmd_start_hndl)
		BAI_bot.add_handler (cmd_note_hndl)
		BAI_bot.add_handler (cmd_diary_hndl)
		BAI_bot.add_handler (cmd_end_hndl)
		BAI_bot.add_handler (cmd_cancel_hndl)
		BAI_bot.add_handler (cmd_checkPlate_hndl)
		BAI_bot.add_handler (msg_hndl)

		self.note_read_hndl = {}
		for timestamp, record in Notebook.records.items():
			self.note_read_hndl [timestamp] = CmdHndl (str(timestamp), lambda bot, update,
					arg = timestamp, book = Notebook: show_record (book, arg))
			BAI_bot.add_handler (self.note_read_hndl [timestamp])

		self.diary_read_hndl = {}
		for timestamp, record in Diary.records.items():
			self.diary_read_hndl [timestamp] = CmdHndl (str(timestamp), lambda bot, update,
					arg = timestamp, book = Diary: show_record (book, arg))
			BAI_bot.add_handler (self.diary_read_hndl [timestamp])
	
	def live (self):
		BAI_bot.live ()

	def initialize_bot (self, bot, update):
		self.on_event (BotAction.initialize, {"bot": bot,
																					"update": update
																				})
	
	def note (self, bot, update, args):
		if len(args) == 0:
			self.on_event (BotAction.record, {"type": "note", "args": args})
		elif args[0].strip().lower() == 'all':
			show_records (Notebook, args, All=True)
		else:
			show_records (Notebook, args, All=False)

	def diary (self, bot, update, args):
		if len(args) == 0:
			self.on_event (BotAction.record, {"type": "diary", "args": args})	
		elif args[0].strip().lower() == 'all':
			show_records (Diary, args, All=True)
		else:
			show_records (Diary, args, All=False)

	def end (self, bot, update, args):
		self.current_tags.extend(map(lambda x: x.strip().lower(), args))
		self.current_tags = list(set(self.current_tags))
		self.on_event (BotAction.end, {'current_content': self.current_content, 'current_tags': self.current_tags})	
		self.current_content = ''
		self.current_tags    = []

	def cancel (self, bot, update):
		self.on_event (BotAction.cancel, {})	
		self.current_content = ''
		self.current_tags    = []

ASys.void           = Void ()
ASys.init           = Init ()
ASys.idle           = Idle ()
ASys.writingnote    = WritingNote ()
ASys.writingdiary   = WritingDiary ()

PA_sys                = ASys ()

if __name__ == '__main__':
	PA_sys.live ()
