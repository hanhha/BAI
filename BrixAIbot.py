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

def send_me (text):
	act_bot.send_message (chat_id = chat_id, text = text)

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

	send_me (greeting + " " + "My name is BAI - Brix A.I.")

def process_msg (bot, update):
	msg = update.message.text
	send_me ("You said " + msg)

def main ():
	config = CfgPsr.ConfigParser ()
	config.read (config_filename)
	updater = Updater(token=config['telegram']['token'])
	dispatcher = updater.dispatcher
	
	dispatcher.add_error_handler (error_cb)
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	
	# Adding handlers
	start_hndl = CmdHndl ('start', start)
	msg_hndl   = MsgHndl (Filters.text, process_msg)

	dispatcher.add_handler (start_hndl)
	dispatcher.add_handler (msg_hndl)
	
	updater.start_polling()
	updater.idle()
	send_me ("I'm offline right now. Good bye.")

if __name__ == '__main__':
	main()
