#!/usr/bin/env python3
from time import time, gmtime #, sleep
from functools import reduce
import re
import copy
import os

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
	
	def new_record (self, record):
		"""
		record: {"timestamp": added time, "tags": tags, "content": note content}
		timestamp is epoch time
		"""
		inttime = record['timestamp']
		self.records [inttime] = copy.deepcopy(record)
		tags = record['tags']
		for tag in tags:
			if tag in self.tags:
				self.tags[tag].append (inttime)
			else:
				self.tags[tag] = [inttime]
		year  = str(gmtime(inttime).tm_year)
		month = str(gmtime(inttime).tm_mon)
		mday  = str(gmtime(inttime).tm_mday)
		if year in self.changed_timetree:
			if month in self.changed_timetree[year]:
				if mday in self.changed_timetree[year][month]:
					self.changed_timetree[year][month][mday].append(inttime)
				else:
					self.changed_timetree[year][month][mday] = [inttime]
			else:
				self.changed_timetree[year][month] = {mday : [inttime]}
		else:
			self.changed_timetree[year] = {month : {mday : [inttime]}}

	def query_tags (self):
		tagscloud = {}
		for k, v in self.tags.items():
			tagscloud [k] = len(v)
		return tagscloud

	def query_records (self, tags):
		queried_records = {}
		for tag in tags:
			if tag in self.tags:
				queried_records [tag] = self.tags[tag]
			else:
				queried_records [tag] = []
		if len(queried_records) == 0:
			return []
		else:
			return list(reduce((lambda l1, l2 : filter (lambda l: l in l2, l1)),
				queried_records.values()))

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
							os.makedir (path)
					else:
						self.timetree[year] = {month : {mday : self.changed_timetree[year][month][mday].copy()}} 
						os.makedirs (path)

					f = open (filename, 'a')
					for stamp in recordlist:
						f.write('\n'.join(['@' + str(self.records[stamp]['timestamp']),
															 ','.join(self.records[stamp]['tags']),
															 self.records[stamp]['content']]))
						f.write('\n' + '---oOo---' + '\n')
					f.close()
		self.changed_timetree.clear()

	def fetch_notebook (self):
		self.records.clear()
		self.timetree.clear()
		self.tags.clear()
		self.changed_timetree.clear()

		for year in listdir_nohidden (self.notebookpath):
			self.timetree [year] = {}
			for month in listdir_nohidden (os.path.join(self.notebookpath, year)):
				self.timetree [year][month] = {}
				for mday in listdir_nohidden (os.path.join(self.notebookpath, year, month)):
					records, tagidx = self.parse_file (os.path.join(self.notebookpath, year, month, mday))
					self.timetree [year][month][mday[:-4]] = list(records.keys()) 
					self.records.update(records)
					for k,v in tagidx.items():
						if k in self.tags:
							self.tags[k].extend(v)
						else:
							self.tags[k] = v

	@staticmethod
	def shape_record (content, tags):
		return {
						'timestamp': int(time()),
						'tags': list(set(tags.copy())),
						'content': content,
						}
					
	@staticmethod
	def unshape_record (record):
		return record['timestamp'], record['tags'], record['content']

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
			
#Test code
#record1 = NoteBook.shape_record ("Test hahaha", ["123","test"])
#sleep(2)
#record2 = NoteBook.shape_record ("Test hahahaha", ["123","test2"])
#notebook = NoteBook ("Test", "/home/hha/Scratches/BAI")
#notebook.fetch_notebook()
#notebook.new_record(record1)
#notebook.new_record(record2)
#notebook.store_notebook()

