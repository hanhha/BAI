#!/usr/bin/env python3

import configparser as CfgPsr
from argparse import ArgumentParser
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

parser = ArgumentParser()
parser.add_argument ('-c', '--config', type=str, help = 'path to config file that stores api token of the bog')
args = parser.parse_args()

config = CfgPsr.ConfigParser ()
config.read (args.config)

print (config['chatterbot']['dbpath'])

BAI_forebrain         = ChatBot('BAI', 
		storage_adaptor = 'chatterbot.storage.SQLStorageAdapter', 
		database = config['chatterbot']['dbpath'],
	)

BAI_forebrain.set_trainer (ChatterBotCorpusTrainer)
BAI_forebrain.train ("chatterbot.corpus.english")

BAI_forebrain         = ChatBot('BAI', 
		storage_adaptor = 'chatterbot.storage.SQLStorageAdapter', 
		database = config['chatterbot']['dbpath'],
		logic_adapters = ['chatterbot.logic.BestMatch',
											'chatterbot.logic.MathematicalEvaluation',
											],
		input_adapter = "chatterbot.input.TerminalAdapter",
		output_adapter = "chatterbot.output.TerminalAdapter",
		read_only = True
	)

print ("Done. Start conversation ...")

while True:
	try:
		bot_input = BAI_forebrain.get_response (None)

	except (KeyboardInterrupt, EOFError, SystemExit):
		break
