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

from BrixAIUtils import VehicleCheck 

config_filename = '/etc/telegram-send.conf'
chat_id = ""
act_bot = None

def error_cb (bot, update, error):
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

def send_me (texts):
	if (act_bot is not None) and (chat_id is not ""):
		for idx, text in enumerate(texts):
			act_bot.send_message (chat_id = chat_id, text = text)
	else:
		print ("Bot is not initialized - Please call /start first")

def start (bot, update):
	global chat_id, act_bot
	chat_id = update.message.chat_id
	act_bot     = bot
	h = datetime.now().time().hour
	if h >= 5 and h <= 12:
		greeting = "Good morning."
	elif h > 12 and h <= 17:
		greeting = "Good afternoon."
	elif h > 17 and h <= 21:
		greeting = "Good evening."
	else:
		greeting = "Greetings night owl."

	send_me ([greeting + " " + "My name is BAI - Brix A.I."])

def check_plate (bot, update):
	list_of_vi = VehicleCheck.check_violation ("51f-81420")
	send_str = [] 
	for idx, report in enumerate(list_of_vi):
		s1 = 'Loi %d' %(idx + 1)
		s2 = 'Ngay vi pham: ' + report['date'].encode('latin-1').decode()
		s3 = 'Vi tri vi pham: ' + report['place'].encode('latin-1').decode()
		s4 = 'Loi vi pham: ' + report['description'].encode('latin-1').decode()
		s5 = 'Co quan xu ly: ' + report['dept'].encode('latin-1').decode()
		#send_str.extend([s1, s2, s3, s4, s5])
		send_str.append('\n'.join([s1, s2, s3, s4, s5]))

	if len(send_str) == 0:
		send_me (["No moving violation"])
	else:
		send_me (send_str)

def process_msg (bot, update):
	msg = update.message.text
	send_me (["You said " + msg])

def main ():
	config = CfgPsr.ConfigParser ()
	config.read (config_filename)
	updater = Updater(token=config['telegram']['token'])
	dispatcher = updater.dispatcher
	
	dispatcher.add_error_handler (error_cb)
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	
	# Adding handlers
	start_hndl = CmdHndl ('start', start)
	check_plate_hndl = CmdHndl ('check_plate', check_plate)
	msg_hndl   = MsgHndl (Filters.text, process_msg)

	dispatcher.add_handler (start_hndl)
	dispatcher.add_handler (check_plate_hndl)
	dispatcher.add_handler (msg_hndl)
	
	updater.start_polling()
	updater.idle()
	send_me (["I'm offline right now. Good bye."])

if __name__ == '__main__':
	main()
