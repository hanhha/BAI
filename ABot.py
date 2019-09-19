#!/usr/bin/env python3

from telegram.ext import (Updater, Filters, BaseFilter)
from telegram.ext import (CommandHandler as CmdHndl, MessageHandler as MsgHndl, CallbackQueryHandler as CbQHndl)
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import constants

from datetime import datetime

class ABot (object):
  def __init__ (self, name = "BAI", token = "", chat_id = 0):
    self.act_chat_id = ""
    self.act_bot     = None

    self.act_name    = name
    self.updater     = Updater(token=token)
    self.job_queue   = self.updater.job_queue
    self.act_chat_id = chat_id

    self.dispatcher  = self.updater.dispatcher

    self.dispatcher.add_error_handler (self.error_cb)

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

  def respond_conversation (self, text, **kwargs):
    """
    Get reponse from chatterbot to serve conversation
    """
    self.act_bot.send_message (self.act_chat_id, text = "Sorry, I've been removed conversation ability.", **kwargs)

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
    self.updater.start_polling ()
    self.updater.idle ()
    if self.act_bot is not None:
       self.respond ("I'm offline right now. Good bye.")

  def add_handler (self, hndl):
    self.dispatcher.add_handler (hndl)

  def remove_handler (self, hndl):
    self.dispatcher.remove_handler (hndl)

class FilterMe (BaseFilter):
  def __init__ (self, bot):
    self.bot = bot

  def filter (self, message):
    #print (message)
    if message.chat_id != self.bot.act_chat_id:
      return False
    else:
      return True
