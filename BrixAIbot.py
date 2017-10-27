#!/usr/bin/env python3

from telegram.ext import Updater
from telegram.ext import CommandHandler as CmdHndl
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut,
		ChatMigrated, NetworkError)
import logging
import configparser as CfgPsr

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
	send_me ("I'm BAI - Brix A.I")

def main ():
	config = CfgPsr.ConfigParser ()
	config.read (config_filename)
	updater = Updater(token=config['telegram']['token'])
	dispatcher = updater.dispatcher
	
	dispatcher.add_error_handler (error_cb)
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	
	start_hndl = CmdHndl ('start', start)
	dispatcher.add_handler (start_hndl)
	
	updater.start_polling()
	updater.idle()
	send_me ("I'm offline right now. Good bye.")

if __name__ == '__main__':
	main()
