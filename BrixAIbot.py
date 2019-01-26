#!/usr/bin/env python3

from telegram.ext import (Updater, Filters, BaseFilter)
from telegram.ext import (CommandHandler as CmdHndl, MessageHandler as MsgHndl, CallbackQueryHandler as CbQHndl)
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import constants

import logging
import configparser as CfgPsr

from datetime import datetime
from time import (localtime, strftime)

from BrixAIUtils import (VehicleCheck, FSM, NoteTake, DictLookup, InlineOptions, InlineCalendar)

import re, operator
from argparse import ArgumentParser
from functools import reduce
import random, string

parser = ArgumentParser()
parser.add_argument ('-p', '--path', type=str, help = 'path of root dir of notebook')
parser.add_argument ('-n', '--notebook', type=str, help = 'name of using notebook')
parser.add_argument ('-d', '--diary', type=str, help = 'name of using diary')
parser.add_argument ('-b', '--botname', type=str, help = 'name of bot')
parser.add_argument ('-c', '--config', type=str, help = 'path to config file that stores api token of the bog')
args = parser.parse_args()

Notebook = NoteTake.NoteBook (args.notebook, args.path, editable = True)
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

	def is_allowed (bot, update):
		if update.message.chat_id != self.act_chat_id:
			bot.send_message (update.message.chat_id, text = "I don't know you. You're harrasing.")
			return False
		else:
			return True

	def respond (self, texts, **kwargs):
		"""
		In case of Markdown or HTML, the split feature would cause error due to no matching parentheses.
		So that feature is abandoned if Markdown or HTML exists
		"""
		if type(texts) is list:
			for idx, text in enumerate(texts):
					self.act_bot.send_message (self.act_chat_id, text = text, **kwargs)
		else:
			self.act_bot.send_message (self.act_chat_id, text = texts, **kwargs)

	def initialize (self, bot, update):
		#self.act_chat_id = update.message.chat_id
		self.act_bot     = bot
		#print (self.act_chat_id)
		#print (update.message)
	
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

	def remove_handler (self, hndl):
		self.dispatcher.remove_handler (hndl)

	def __init__ (self, name = "BAI"):
		self.act_name = name 
		config = CfgPsr.ConfigParser ()
		config.read (self.config_filename)
		self.updater    = Updater(token=config['telegram']['token'])
		self.act_chat_id    = int(config['telegram']['chat_id'])
		self.dispatcher = self.updater.dispatcher

		self.dispatcher.add_error_handler (self.error_cb)
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BAI_bot               = ABot (args.botname)

class FilterMe (BaseFilter):
	def filter (self, message):
		#print (message)
		if message.chat_id != BAI_bot.act_chat_id:
			return False
		else:
			return True

filterme = FilterMe()

class BotAction (FSM.Action):
	def __init__ (self, action):
		FSM.Action.__init__ (self, action, "Bot")

BotAction.initialize     = BotAction ("initialize")
BotAction.record         = BotAction ("record")
BotAction.tempfastswitch = BotAction ("tempfastswitch")
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
				if 'timestamp' in args:
					return ASys.workeditnote
				else:
					return ASys.worknewnote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.workdiary
		elif input == BotAction.tempfastswitch:
			if args['type'] == 'note':
				return ASys.worknewnote
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
				if 'timestamp' in args:
					return ASys.workeditnote
				else:
					return ASys.worknewnote
			elif args['type'] == 'diary':
				BAI_bot.respond ("Recording diary. You can save it by /end with tags separated by comma.")
				return ASys.workdiary
		elif input == BotAction.tempfastswitch:
			if args['type'] == 'note':
				return ASys.worknewnote
			elif args['type'] == 'diary':
				return ASys.workdiary
		BAI_bot.respond ("Very sorry, I don't have this function right now")
		return self

class WorkNewNote (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WorkNewNote")
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
																															book = Notebook: show_record (book, arg), filters = filterme)
				BAI_bot.add_handler (PA_sys.note_read_hndl [record.timestamp])
				BAI_bot.respond ("Your note has been saved.")
			else:
				BAI_bot.respond ("Nothing to record.")
			return ASys.idle
		elif input == BotAction.cancel:
			BAI_bot.respond ("Canceled")
			return ASys.idle
		return self

class WorkEditNote (FSM.State):
	def __init__ (self):
		FSM.State.__init__ (self, "WorkEditNote")
	def run(self, input, args):
		if 'timestamp' in args:
			self.timestamp_note = args ['timestamp']
	def next(self, input, args):
		if input == BotAction.record:
			BAI_bot.respond ("I'm recording.")
		if input == BotAction.end:
			if len(args['current_content']) != 0:
				Notebook.append_record ({'content':args['current_content'], 'tags':args['current_tags']}, self.timestamp_note)
				Notebook.store_notebook ()
				record = Notebook.records [self.timestamp_note]
				PA_sys.note_read_hndl[record.timestamp] = CmdHndl (str(record.timestamp), 
																															lambda bot, 
																															update, arg = record.timestamp,
																															book = Notebook: show_record (book, arg), filters = filterme)
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
																															 book = Diary: show_record (book, arg), filters = filterme)
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

ev_dict = DictLookup.EV_dict_cache ()
wordlist = {}

def lookup (bot, update, args):
	if PA_sys.currentState is not ASys.void:
		send_str = []
		if len(args) == 0:
			send_str = ['Maybe next time.']
		else:
			for k,v in wordlist.items():
				BAI_bot.remove_handler (v)
			wordlist.clear()
			for word in args:
				if len(ev_dict.read(word)) > 0:
					send_str.append ('/' + word + '\n' + ev_dict.read (word) [0] [:99])
					wordlist [word] = CmdHndl (word, lambda bot, update, arg = word: BAI_bot.respond (ev_dict.read (arg)), filters = filterme)
					BAI_bot.add_handler (wordlist [word])
				else:
					send_str.append ('No result found.')

	BAI_bot.respond (send_str)

def process_msg (bot, update):
	if PA_sys.currentState is not ASys.void:
		tag_re = re.compile(r"(\w+),,,")

		msg = update.message.text
		if (PA_sys.currentState == ASys.worknewnote) or (PA_sys.currentState == ASys.workeditnote) or (PA_sys.currentState == ASys.workdiary):
			PA_sys.current_tags.extend(map (lambda x: x.strip().lower(), tag_re.findall(msg)))
			PA_sys.current_tags = list(set(PA_sys.current_tags)) 

			pattern = re.compile ('[\W]+')
			wcount = len ([x for x in tag_re.sub(r'\1', msg).split() if pattern.sub('',x).isalnum()])
			PA_sys.current_wcount += wcount
			BAI_bot.respond ("Word count: %d" %(PA_sys.current_wcount))

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

def show_dates   (book):
	preview_dates (book.query_dates())

def show_records (book, tags = [], All = False, timestr = 'Anytime'):
	if not All:
		stamplist = book.query_records (map(lambda x: x.strip().lower(), tags))
	else:
		stamplist = book.records.keys()
	if len(stamplist) == 0:
		BAI_bot.respond("There is no record.")
	else:
		preview_records (book, stamplist)

options = InlineOptions.InlineOptions ("Tags307")
calendar = InlineCalendar.InlineCalendar ("Dates307")

def preview_dates (datetree):
	calendar.reset()
	today = datetime.now()
	calendar.currentYear = today.year
	calendar.currentMonth = today.month
	calendar.set_calendar_tree (datetree)
	calendar.set_view (hasAll = True, hasDone = True, hasCancel = True)
	BAI_bot.respond ('Select dates:', reply_markup = calendar.get_InlineKeyboardMarkup())

def preview_tags (tagscloud):
	#print (tagscloud)
	option_list = []
	callback_list = []
	for k, v in sorted(tagscloud.items(), key = lambda t: t[1], reverse = True):
		option_list.append('{0}({1})'.format(k,v))
		callback_list.append(k)
	options.set_options (option_list, callback_list, hasAll = True, hasDone = True, hasCancel = True)
	BAI_bot.respond ('Select tags:', reply_markup = options.get_InlineKeyboardMarkup()) 

def date_select (bot, update):
	if PA_sys.currentState is not ASys.void:
		query = update.callback_query
		calendar.select (query.data)
		select_dates_str = ', '.join(calendar.selectedDatesSum)
		if calendar.SelectDone:
			bot.edit_message_text(text='Select dates: ' + select_dates_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id)
			#TODO
			PA_sys.withdrawwork()
		elif calendar.SelectCancel:
			PA_sys.withdrawwork()
			bot.edit_message_text(text='Canceled.',
					chat_id=query.message.chat_id, message_id=query.message.message_id)
		else:
			bot.edit_message_text(text='Select dates: ' + select_dates_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id,
					reply_markup = calendar.get_InlineKeyboardMarkup())

def tag_select (bot, update):
	if PA_sys.currentState is not ASys.void:
		query = update.callback_query
		options.select (query.data)
		select_str = ', '.join(options.selectedOptions)
		if options.SelectDone:
			bot.edit_message_text(text='Selected tags: ' + select_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id)
			if PA_sys.currentState == ASys.worknewnote or PA_sys.currentState == ASys.workeditnote:
				book = Notebook
			elif PA_sys.currentState == ASys.workdiary:
				book = Diary
			show_records (book, options.selectedOptions, All=options.AllOptionSelected)
			PA_sys.withdrawwork()
		elif options.SelectCancel:
			PA_sys.withdrawwork()
			bot.edit_message_text(text='Canceled.',
					chat_id=query.message.chat_id, message_id=query.message.message_id)
		else:
			bot.edit_message_text(text='Select tags: ' + select_str,
					chat_id=query.message.chat_id, message_id=query.message.message_id,
					reply_markup = options.get_InlineKeyboardMarkup())

def inline_select (bot, update):
	query = update.callback_query
	if options.name in query.data:
		tag_select (bot, update)
		return
	if calendar.name in query.data:
		date_select (bot, update)
		return
	return


def preview_records (book, records_stamplist):
	for stamp in records_stamplist:
		record = book.records [stamp]
		preview_str = record.to_str(Markdown = False, ftime = localtime, joined = True) [0:99]	
		preview_str += '\n...click to /' + str(stamp) + ' for full note...'
		BAI_bot.respond ('/' + str(stamp) + '\n' + preview_str)
	BAI_bot.respond ("That's all.")
	
def record2str (book, timestamp):
	return book.records[timestamp].to_str(Markdown = True, ftime = localtime) 

def show_record (book, timestamp):
	record_content = book.records[timestamp].to_str(Markdown = True, ftime = localtime)
	BAI_bot.respond (record_content, parse_mode = 'Markdown')

class ASys (FSM.StateMachine):
	def __init__(self):
		self.current_wcount  = 0
		self.current_content = ''
		self.current_tags    = []
		FSM.StateMachine.__init__(self, ASys.void)
		
		# Adding handlers
		cmd_start_hndl        = CmdHndl ('start', self.initialize_bot, filters = filterme)
		cmd_note_hndl         = CmdHndl ('note', self.note, pass_args = True, filters = filterme)
		cmd_diary_hndl        = CmdHndl ('diary', self.diary, pass_args = True, filters = filterme)
		cmd_end_hndl          = CmdHndl ('end', self.end, pass_args = True, filters = filterme)
		cmd_cancel_hndl       = CmdHndl ('cancel', self.cancel, filters = filterme)
		cmd_checkPlate_hndl   = CmdHndl ('check_plate', check_plate, pass_args = True, filters = filterme)
		cmd_lookup_hndl       = CmdHndl ('lookup', lookup, pass_args = True, filters = filterme)
		query_select_hndl   	= CbQHndl (inline_select)
		msg_hndl              = MsgHndl (Filters.text & filterme, process_msg)
		
		BAI_bot.add_handler (cmd_start_hndl)
		BAI_bot.add_handler (cmd_note_hndl)
		BAI_bot.add_handler (cmd_diary_hndl)
		BAI_bot.add_handler (cmd_end_hndl)
		BAI_bot.add_handler (cmd_cancel_hndl)
		BAI_bot.add_handler (cmd_checkPlate_hndl)
		BAI_bot.add_handler (cmd_lookup_hndl)
		BAI_bot.add_handler (query_select_hndl)
		BAI_bot.add_handler (msg_hndl)

		self.note_read_hndl = {}
		for timestamp, record in Notebook.records.items():
			self.note_read_hndl [timestamp] = CmdHndl (str(timestamp), lambda bot, update,
					arg = timestamp, book = Notebook: show_record (book, arg), filters = filterme)
			BAI_bot.add_handler (self.note_read_hndl [timestamp])

		self.diary_read_hndl = {}
		for timestamp, record in Diary.records.items():
			self.diary_read_hndl [timestamp] = CmdHndl (str(timestamp), lambda bot, update,
					arg = timestamp, book = Diary: show_record (book, arg), filters = filterme)
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
					self.fastswitch (ASys.worknewnote)
					show_tags    (Notebook)
				elif args[0].strip().lower() == 'dates':
					self.fastswitch (ASys.worknewnote)
					show_dates   (Notebook)
				elif int(args[0]) in Notebook.records:
					self.on_event (BotAction.record, {"type": "note", "timestamp" : int(args[0]), "args": args})
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
					self.fastswitch (ASys.workdiary)
					show_tags    (Diary)
				elif args[0].strip().lower() == 'dates':
					self.fastswitch (ASys.workdiary)
					show_dates    (Diary)
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
			self.current_wcount  = 0
			self.current_tags    = []

	def cancel (self, bot, update):
		if self.currentState is not ASys.void:
			self.on_event (BotAction.cancel, {})	
			self.current_content = ''
			self.current_wcount  = 0
			self.current_tags    = []
	
	def transition_disable_info(self):
		BAI_bot.respond ('Please finish previous activity. All preemptive activities were abandoned.')

ASys.void           = Void ()
ASys.init           = Init ()
ASys.idle           = Idle ()
ASys.worknewnote    = WorkNewNote ()
ASys.workeditnote   = WorkEditNote ()
ASys.workdiary      = WorkDiary ()

PA_sys                = ASys ()

if __name__ == '__main__':
	PA_sys.live ()
