#!/usr/bin/env python3

from telegram.ext import (Updater, Filters)
from telegram.ext import (CommandHandler as CmdHndl, MessageHandler as MsgHndl, CallbackQueryHandler as CbQHndl)
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import constants

import logging
import configparser as CfgPsr

from datetime import datetime
from time import (localtime, strftime)

from BrixAIUtils import (VehicleCheck, FSM, NoteTake, DictLookup, Utils)

import re, operator
from argparse import ArgumentParser
from functools import reduce

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
			print ("Unauthorized") 
		except BadRequest:
			print ("Malformed requests")
		except TimedOut:
			print ("Slow connection")
		except NetworkError:
			print ("Network error")
		except ChatMigrate as e:
			print ("Chat ID of group has changed") 
		except TelegramError:
			print ("Internal Telegram error")

	def respond (self, texts, short = False, **kwargs):
		chunk_size = 1000 # 1000 chars
		short_chunk= 50
		if type(texts) is list:
			for idx, text in enumerate(texts):
				if short:
					text = text [:short_chunk]
				if len(text) > chunk_size:
					chunks = len(text)
					text_chunks = [text[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
					self.respond (text_chunks, short = short, **kwargs)
				else:
					#print (text)
					self.act_bot.send_message (self.act_chat_id, text = text, **kwargs)
		else:
			if short:
				texts = texts [:short_chunk]
			if len(texts) > chunk_size:
				chunks = len(text)
				text_chunks = [text[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
				self.respond (text_chunks, short = short, **kwargs)
			else:
				#print (texts)
				self.act_bot.send_message (self.act_chat_id, text = texts, **kwargs)

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

BotAction.initialize     = BotAction ("initialize")
BotAction.record         = BotAction ("record")
BotAction.tempswitchwork = BotAction ("tempswitchwork")
BotAction.end            = BotAction ("end")
BotAction.cancel         = BotAction ("cancel")

class Void (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Void")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.initialize:
			return ASys.init
		return self

class Init (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Init")
	def run(self, input, args):
		#print (self)
		BAI_bot.initialize (args["bot"], args["update"])
		BAI_bot.greeting ()
		BAI_bot.respond ("I'm here to serve you")
	def next(self, input, args):
		if input == BotAction.record:
			if args['type'] == 'note':
				BAI_bot.respond ("Recording note. You can save it by /end with tags separated by comma.")
				return ASys.worknote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.workdiary
		elif input == BotAction.tempswitchwork:
			if args['type'] == 'note':
				return ASys.worknote
			elif args['type'] == 'diary':
				return ASys.workdiary
		BAI_bot.respond ("Very sorry, I don't have this function right now")
		return self

class Idle (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "Idle")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.record:
			if args['type'] == 'note':
				BAI_bot.respond ("Recording note. You can save it by /end with tags separated by comma.")
				return ASys.worknote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.workdiary
		elif input == BotAction.tempswitchwork:
			if args['type'] == 'note':
				return ASys.worknote
			elif args['type'] == 'diary':
				return ASys.workdiary
		BAI_bot.respond ("Very sorry, I don't have this function right now")
		return self

class WorkNote (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WorkNote")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.record:
			BAI_bot.respond ("I'm recording.")
		if input == BotAction.end:
			if len(args['current_content']) != 0:
				record = NoteTake.Entry(NoteTake.Entry.shape_record (args['current_content'], args['current_tags']))
				Notebook.new_record (record)
				Notebook.store_notebook ()
				PA_sys.note_read_hndl[record.timestamp] = CmdHndl (str(record.timestamp), 
																															lambda bot, 
																															update, arg = record.timestamp,
																															book = Notebook: show_record (book, arg))
				BAI_bot.add_handler (PA_sys.note_read_hndl [record.timestamp])
				BAI_bot.respond ("Your note has been saved.")
			else:
				BAI_bot.respond ("Nothing to record.")
			return ASys.idle
		elif input == BotAction.cancel:
			BAI_bot.respond ("Canceled")
			return ASys.idle
		return self

class WorkDiary (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WorkDiary")
	def run(self, input, args):
		pass
	def next(self, input, args):
		if input == BotAction.record:
			BAI_bot.respond ("I'm recording.")
		if input == BotAction.end:
			if len(args['current_content']) != 0:
				record = NoteTake.Entry(NoteTake.Entry.shape_record (args['current_content'], args['current_tags']))
				Diary.new_record (record)
				Diary.store_notebook ()
				PA_sys.diary_read_hndl[record.timestamp] = CmdHndl (str(record.timestamp), 
																															 lambda bot,
																															 update, arg =
																															 record.timestamp,
																															 book = Diary: show_record (book, arg))
				BAI_bot.add_handler (PA_sys.diary_read_hndl [record.timestamp])
				BAI_bot.respond ("Your entry has been saved.")
			else:
				BAI_bot.respond ("Nothing to record.")
			return ASys.idle
		elif input == BotAction.cancel:
			BAI_bot.respond ("Canceled")
			return ASys.idle
		return self

def movement_violate_report_str (no, report):
	s1 = 'Loi %d' %(no + 1)
	s2 = 'Ngay vi pham: ' + report['date'].encode('latin-1').decode()
	s3 = 'Vi tri vi pham: ' + report['place'].encode('latin-1').decode()
	s4 = 'Loi vi pham: ' + report['description'].encode('latin-1').decode()
	s5 = 'Co quan xu ly: ' + report['dept'].encode('latin-1').decode()
	return '\n'.join([s1, s2, s3, s4, s5])

def check_plate (bot, update, args):
	if PA_sys.currentState is not ASys.void:
		send_str = [] 
		if len(args) == 0:
			list_of_vi = VehicleCheck.check_violation ("51f-81420")
			if len(list_of_vi) != 0:
				for idx, report in enumerate(list_of_vi):
					send_str.append(movement_violate_report_str(idx, report))
			else:
				send_str.append('No moving violation')
		else:
			for pidx, plate in enumerate(args):
				BAI_bot.respond ("Bien so %s" %(plate))
				list_of_vi = VehicleCheck.check_violation (plate)
				if len(list_of_vi) != 0:
					for idx, report in enumerate(list_of_vi):
						send_str.append(movement_violate_report_str(idx, report))
				else:
					send_str.append('No moving violation')
		BAI_bot.respond (send_str)

def lookup (args):
	if PA_sys.currentState is not ASys.void:
		send_str = []
		if len(args) == 0:
			send_str = ['Maybe next time.']
		else:
			for word in args:
				pron, desc, rela = DictLookup.lookup (word.strip().lower())
				send_str.append (word + '\n' + pron +  desc + ''.join(rela))
		return send_str

def short_lookup (bot, update, args):
	if PA_sys.currentState is not ASys.void:
		BAI_bot.respond( lookup (args), short = True)

def detail_lookup (bot, update, args):
	if PA_sys.currentState is not ASys.void:
		BAI_bot.respond( lookup (args), short = False)

def process_msg (bot, update):
	if PA_sys.currentState is not ASys.void:
		tag_re = re.compile(r"(\w+),,,")

		msg = update.message.text
		if (PA_sys.currentState == ASys.worknote) or (PA_sys.currentState == ASys.workdiary):
			PA_sys.current_tags.extend(map (lambda x: x.strip().lower(), tag_re.findall(msg)))
			PA_sys.current_tags = list(set(PA_sys.current_tags)) 
			if PA_sys.current_content == '':
				PA_sys.current_content = tag_re.sub(r'\1', msg)
			else:
				PA_sys.current_content += '\n' + tag_re.sub(r'\1', msg)
		else:
			BAI_bot.respond (["You said " + msg])
			BAI_bot.respond ("I'm here to serve you")

def show_tags    (book, All = True, timestr = 'Anytime'):
	if All:
		preview_tags (book.query_tags())

def show_records (book, tags = [], All = False, timestr = 'Anytime'):
	if not All:
		stamplist = book.query_records (map(lambda x: x.strip().lower(), tags))
	else:
		stamplist = book.records.keys()
	if len(stamplist) == 0:
		BAI_bot.respond("There is no record.")
	else:
		preview_records (book, stamplist)

options = Utils.InlineOptions ("Tags")

def preview_tags (tagscloud):
	#print (tagscloud)
	option_list = []
	callback_list = []
	for k, v in sorted(tagscloud.items(), key = lambda t: t[1], reverse = True):
		option_list.append('{0}({1})'.format(k,v))
		callback_list.append(k)
	options.set_options (option_list, callback_list, hasAll = True, hasDone = True, hasCancel = True)
	BAI_bot.respond ('Select tags:', reply_markup = options.get_InlineKeyboardMarkup()) 

def select (bot, update):
	if PA_sys.currentState is not ASys.void:
		query = update.callback_query
		options.select (query.data)
		select_str = ', '.join(options.selected_data_list)
		if options.SelectDone:
			bot.edit_message_text(text='Selected tags: ' + select_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id)
			if PA_sys.currentState == ASys.worknote:
				book = Notebook
			elif PA_sys.currentState == ASys.workdiary:
				book = Diary
			show_records (book, options.selected_data_list, All=options.AllOptionSelected)
			PA_sys.withdrawwork()
		elif options.SelectCancel:
			PA_sys.withdrawwork()
			bot.edit_message_text(text='Canceled.',
					chat_id=query.message.chat_id, message_id=query.message.message_id)
		else:
			bot.edit_message_text(text='Select tags: ' + select_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id,
					reply_markup = options.get_InlineKeyboardMarkup())

def preview_records (book, records_stamplist):
	for stamp in records_stamplist:
		record = book.records [stamp]
		BAI_bot.respond ('/' + str(stamp) + '\n' + record.to_str(Markdown = True, ftime = localtime, preview = 25), parse_mode = 'Markdown')
	BAI_bot.respond ("That's all.")
	
def record2str (book, timestamp):
	return book.records[timestamp].to_str(Markdown = True, ftime = localtime) 

def show_record (book, timestamp):
	BAI_bot.respond (record2str(book, timestamp), parse_mode = 'Markdown')


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
		cmd_slookup_hndl      = CmdHndl ('lookup', short_lookup, pass_args = True)
		cmd_llookup_hndl      = CmdHndl ('detail_lookup', detail_lookup, pass_args = True)
		query_select_hndl     = CbQHndl (select)
		msg_hndl              = MsgHndl (Filters.text, process_msg)
		
		BAI_bot.add_handler (cmd_start_hndl)
		BAI_bot.add_handler (cmd_note_hndl)
		BAI_bot.add_handler (cmd_diary_hndl)
		BAI_bot.add_handler (cmd_end_hndl)
		BAI_bot.add_handler (cmd_cancel_hndl)
		BAI_bot.add_handler (cmd_checkPlate_hndl)
		BAI_bot.add_handler (cmd_slookup_hndl)
		BAI_bot.add_handler (cmd_llookup_hndl)
		BAI_bot.add_handler (query_select_hndl)
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
		if self.currentState is not ASys.void:
			if len(args) == 0:
				self.on_event (BotAction.record, {"type": "note", "args": args})
			elif (len(args) == 1):
				if args[0].strip().lower() == 'all':
					show_records (Notebook, args, All=True)
				elif args[0].strip().lower() == 'tags':
					self.switchwork (ASys.worknote)
					show_tags    (Notebook)
				else:
					show_records (Notebook, args, All=False)
			else:
				show_records (Notebook, args, All=False)

	def diary (self, bot, update, args):
		if self.currentState is not ASys.void:
			if len(args) == 0:
				self.on_event (BotAction.record, {"type": "diary", "args": args})	
			elif (len(args) == 1):
				if args[0].strip().lower() == 'all':
					show_records (Diary, args, All=True)
				elif args[0].strip().lower() == 'tags':
					self.switchwork (ASys.workdiary)
					show_tags    (Diary)
				else:
					show_records (Diary, args, All=False)
			else:
				show_records (Diary, args, All=False)

	def end (self, bot, update, args):
		if self.currentState is not ASys.void:
			self.current_tags.extend(map(lambda x: x.strip().lower(), args))
			self.current_tags = list(set(self.current_tags))
			self.on_event (BotAction.end, {'current_content': self.current_content, 'current_tags': self.current_tags})	
			self.current_content = ''
			self.current_tags    = []

	def cancel (self, bot, update):
		if self.currentState is not ASys.void:
			self.on_event (BotAction.cancel, {})	
			self.current_content = ''
			self.current_tags    = []
	
	def transition_disable_info(self):
		BAI_bot.respond ('Please finish previous activity. All preemptive activities were abandoned.')

ASys.void           = Void ()
ASys.init           = Init ()
ASys.idle           = Idle ()
ASys.worknote    = WorkNote ()
ASys.workdiary   = WorkDiary ()

PA_sys                = ASys ()

if __name__ == '__main__':
	PA_sys.live ()
