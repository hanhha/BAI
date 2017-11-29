#!/usr/bin/env python3
from time import time, gmtime #, sleep
from functools import reduce
import re
import copy
import os
from itertools import chain

def listdir_nohidden (path):
	return list(filter(lambda f: not f.startswith('.'), os.listdir(path)))

class NoteBook:
	def __init__(self, name, rootdir):
		self.records  = {} 
		self.tags     = {}
		self.changed_timetree = {} #gmt time 
		self.timetree         = {} #gmt time 
		self.name     = name
		self.rootdir  = rootdir

		self.notebookpath = os.path.join(self.rootdir, self.name)
		if not os.path.exists (self.notebookpath):
			os.makedirs (self.notebookpath)
		else:
			self.fetch_notebook()
	
	def store_notebook (self):
		"""
		only records in changed_timetree are written back to storage
		"""
		for year, months in self.changed_timetree.items():
			for month, mdays in months.items():
				path     = os.path.join(self.notebookpath, year, month)
				for mday, recordlist in mdays.items():
					filename = os.path.join(path, mday + ".txt")
					if year in self.timetree:
						if month in self.timetree[year]:
							if mday in self.timetree[year][month]:
								self.timetree[year][month][mday].extend (self.changed_timetree[year][month][mday].copy())
							else:
								self.timetree[year][month][mday] = self.changed_timetree[year][month][mday].copy() 
						else:
							self.timetree[year][month] = {mday : self.changed_timetree[year][month][mday].copy()} 
							#os.makedir (path)
					else:
						self.timetree[year] = {month : {mday : self.changed_timetree[year][month][mday].copy()}} 
						#os.makedirs (path)

					f = open (filename, 'w')
					for stamp in recordlist:
						f.write('\n'.join(['@[' + str(self.records[stamp]['timestamp']) + ']',
															 ','.join(self.records[stamp]['tags']),
															 '@[' + str(self.records[stamp]['timestamp']) + ']']))
						texts = self.records[stamp]['content'].split('\n')
						if texts[-1] == '':
							del texts[-1]
						for text in texts:
							#print (text)
							f.write('\n\t' + text)
						f.write('\n---oOo---\n')
					f.close()
		self.changed_timetree.clear()

	def fetch_notebook (self):
		self.records.clear()
		self.timetree.clear()
		self.tags.clear()
		self.changed_timetree.clear()

		for year in listdir_nohidden (self.notebookpath):
			self.changed_timetree [year] = {}
			for month in listdir_nohidden (os.path.join(self.notebookpath, year)):
				self.changed_timetree [year][month] = {}
				for mday in listdir_nohidden (os.path.join(self.notebookpath, year, month)):
					records, tagidx = self.parse_file (os.path.join(self.notebookpath, year, month, mday))
					self.changed_timetree [year][month][mday[:-4]] = list(records.keys()) 
					self.records.update(records)
					for k,v in tagidx.items():
						if k in self.tags:
							self.tags[k].extend(v)
						else:
							self.tags[k] = v

	@staticmethod
	def parse_file (path):
		records = {}
		timestamp = 0
		content = ''
		tags = []
		tag_idx = {}
		sep_mark = re.compile(r"^---oOo---$")
		timestamp_mark = re.compile(r"^@\d+$")

		f = open (path, 'r')
		is_content_read = False 
		is_tags_read    = False 
		is_stamp_read   = False
		for line in f:
			if not is_stamp_read:
				if timestamp_mark.match(line):
					timestamp = int(line.strip()[1:])
					is_stamp_read = True
					continue
			if not is_tags_read:
				tags = [tag.strip().lower() for tag in line.split(',')]
				if len(tags) == 0:
					tags = ['untagged']
				is_tags_read = True
				continue
			if sep_mark.match(line):
				is_content_read = True
			else:
				content += line
			if is_content_read and is_tags_read and is_stamp_read:
				records [timestamp] = {'timestamp': timestamp,
															 'tags': list(set(tags.copy())),
															 'content': content,}
				for t in list(set(tags)):
					if t in tag_idx:
						tag_idx [t].append (timestamp)
					else:
						tag_idx [t] = [timestamp]

				is_content_read = False
				is_stamp_read   = False
				is_tags_read    = False
				content = ''

		f.close()
		return records, tag_idx
			
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument ('-p', '--path', type=str, help = 'path of root dir of notebook')
parser.add_argument ('-n', '--notebook', type=str, help = 'name of using notebook')
parser.add_argument ('-d', '--diary', type=str, help = 'name of using diary')
args = parser.parse_args()

Notebook = NoteBook (args.notebook, args.path)
Diary    = NoteBook (args.diary, args.path)

Notebook.store_notebook()
Diary.store_notebook()

#Test code
#record1 = NoteBook.shape_record ("Test hahaha", ["123","test"])
#sleep(2)
#record2 = NoteBook.shape_record ("Test hahahaha", ["123","test2"])
#notebook = NoteBook ("Test", "/home/hha/Scratches/BAI")
#notebook.fetch_notebook()
#notebook.new_record(record1)
#notebook.new_record(record2)
#notebook.store_notebook()

