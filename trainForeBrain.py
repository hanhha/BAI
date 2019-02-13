#!/usr/bin/env python3

import configparser as CfgPsr
from argparse import ArgumentParser
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

import logging

logger = logging.getLogger ()
logger.setLevel (logging.CRITICAL)

parser = ArgumentParser()
parser.add_argument ('-c', '--config', type=str, help = 'path to config file that stores api token of the bog')
args = parser.parse_args()

config = CfgPsr.ConfigParser ()
config.read (args.config)

print (config['chatterbot']['dbpath'])

BAI_forebrain         = ChatBot('BAI', 
		storage_adapter = 'chatterbot.storage.SQLStorageAdapter', 
		database_uri = config['chatterbot']['dbpath'],
	)

trainer = ChatterBotCorpusTrainer (BAI_forebrain)
trainer.train ("chatterbot.corpus.english")

BAI_forebrain         = ChatBot('BAI', 
		storage_adapter = 'chatterbot.storage.SQLStorageAdapter', 
		database_uri = config['chatterbot']['dbpath'],
		logic_adapters = ['chatterbot.logic.BestMatch',
				'chatterbot.logic.MathematicalEvaluation',
				],
		read_only = True
	)

print ("Done. Start conversation ...")

while True:
	try:
                bot_response = BAI_forebrain.get_response ( input("You: ") )
                print (bot_response)

	except (KeyboardInterrupt, EOFError, SystemExit):
		break
