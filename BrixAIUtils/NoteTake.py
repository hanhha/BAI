#!/usr/bin/env python3
from time import time, gmtime, strftime
from functools import reduce
import re
import copy
import os
from itertools import chain
from time import sleep

def listdir_nohidden (path):
    return list(filter(lambda f: not f.startswith('.'), os.listdir(path)))

class Entry:
  def __init__ (self, record = {'timestamp':0 , 'tags':['untagged'], 'content':{}}):
    """
        record: {"timestamp": added time, "tags": tags, "content": note content}
    timestamp is epoch time
    """
    self.record = copy.deepcopy (record)

  def add (self, content, tags = [], replace_tag = False):
    if replace_tag:
      self.set_tags (tags)
    else:
      self.add_tags (tags)
    inttime = int(time())
    if self.record ['timestamp'] == 0 :
      self.record ['timestamp'] = inttime
    self.record ['content'] [inttime] = content

  def add_tags (self, tags):
    if type(tags) is list:
      if len(tags) == 0: 
        pass
      else:
        if self.record ['tags'][0] == 'untagged':
          self.record['tags'].clear()
        self.record['tags'].extend(tags.copy)
    else:
      self.record['tags'].append(tags)

  def del_tags (self, tags):
    if type(tags) == 'list' and len(tags) == 0: 
      pass
    else:
      if type(tags) == 'list':
        for tag in tags:
          if tag in self.record ['tags']:
            self.record ['tags'].remove (tag)
      else:
        if tags in self.record ['tags']:
          self.record ['tags'].remove (tags)

  def set_tags (self, tags):
    if type(tags) == 'list' and len(tags) == 0: 
      pass
    else:
      if type(tags) == 'list':
        self.record ['tags'] = tags.copy()
      else:
        self.record ['tags'] = [tags]

  @property
  def timestamp (self):
    return self.record ['timestamp']

  @property
  def tags (self):
    return self.record ['tags']

  @property
  def content (self):
    return self.record ['content']

  @staticmethod
  def date_str (timestamp, prefix, Markdown, ftime):
    ret_str = prefix + strftime ('%Y-%m-%d %H:%M:%S', ftime (timestamp))
    if Markdown:
      ret_str = '_' + ret_str + '_'
    return ret_str

  @staticmethod
  def tags_str (tagslist, Markdown):
    if tagslist [0] == 'untagged':
      return ''
    else:
      ret_str = ', '.join(tagslist)
      if Markdown:
        ret_str = '*' + ret_str + '*'
      return ret_str

  def to_str (self, Markdown = False, ftime = gmtime, preview = 0):
    ret_str = "" 
    ret_str += self.tags_str (self.record ['tags'], Markdown)
    char_quota = preview
    for timestamp, content in sorted (self.record['content'].items(), key = lambda t: t[0], reverse = False):
      if (preview == 0) or (preview > 0 and char_quota > 0):
        ret_str += '\n'
        if timestamp == self.record ['timestamp']:
          ret_str += self.date_str (timestamp, "Created in ", Markdown, ftime) + '\n'
        else:
          ret_str += self.date_str (timestamp, "Edited in ", Markdown, ftime) + '\n'
        if (preview > 0) and (len(content) > char_quota):
          ret_str += content [0:char_quota]
        else:
          ret_str += content 
        char_quota = char_quota - len(content)
      else:
        break
    if preview > 0:
      end_str = 'click to timestamp to see more'
      if Markdown:
        end_str = '_' + end_str + '_'
      ret_str += '\n' + end_str
    #print (ret_str)
    return ret_str

  @staticmethod
  def shape_record (content, tags):
    if type(tags) is list:
      if len(tags) == 0:
        ttags = ['untagged']
      else:
        ttags = tags
    else:
      ttags = [tags]
    inttime = int(time())
    return {'timestamp': inttime,
            'tags': list(set(ttags.copy())),
            'content': {inttime : content},
           }

  @staticmethod
  def unshape_record (record):
    if record['tags'][0] == 'untagged':
      return record['timestamp'], [''], record['content']
    else:
      return record['timestamp'], record['tags'], record['content']


class NoteBook:
  def __init__(self, name, rootdir, editable=False):
    self.records  = {} 
    self.tags     = {}
    self.changed_timetree = {} #gmt time 
    self.timetree         = {} #gmt time 
    self.name     = name
    self.rootdir  = rootdir
    self.editable = editable
    self.notebookpath = os.path.join(self.rootdir, self.name)
    if not os.path.exists (self.notebookpath):
        os.makedirs (self.notebookpath)
    else:
        self.fetch_notebook()
    
  def new_record (self, record):
      inttime = record.timestamp
      self.records [inttime] = copy.deepcopy(record)
      tags = record.tags
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

  def replace_record (self, old_record, new_record):
    """
    in this case, timestamp is existed in timetree
    The existed one will be removed from timetree and all linked structures, and new one will be added to changed_timetree
    """
    if self.editable:
      assert old_record.timestamp == new_record.timestamp
      inttime    = old_record.timestamp

      # Move from timetree to changed_timetree
      year  = str(gmtime(inttime).tm_year)
      month = str(gmtime(inttime).tm_mon)
      mday  = str(gmtime(inttime).tm_mday)
      self.changed_timetree [year] = {month : {mday : copy.deepcopy(self.timetree [year][month][mday])}}
      del self.timetree[year][month][mday]
      if len(self.timetree[year][month]) == 0:
        del self.timetree[year][month]
      if len(self.timetree[year]) == 0:
        del self.timetree[year]

      # Delete old tags and add new tags
      for tag in old_record.tags:
        self.tags['tag'].remove(inttime)
      tags = new_record.tags
      for tag in tags:
          if tag in self.tags:
              self.tags[tag].append (inttime)
          else:
              self.tags[tag] = [inttime]
      
      # Change in records
      self.records [inttime] = copy.deepcopy (new_record)

      # Delete file for that day
      os.remove (os.path.join(self.notebookpath, year, month, mday + ".txt"))
      try:
        os.rmdir  (os.path.join(self.notebookpath, year, month))
      except OSError:
        pass
      try:
        os.rmdir  (os.path.join(self.notebookpath, year))
      except OSError:
        pass
    else:
      pass

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
          #return list(reduce((lambda l1, l2 : filter (lambda l: l in l2, l1)), queried_records.values()))
          queried_records = list(chain.from_iterable(queried_records.values()))
          ret_list = list(set(queried_records))
          return ret_list

  def store_notebook (self):
    """
    only records in changed_timetree are written back to storage
    """
    for year, months in self.changed_timetree.items():
      for month, mdays in months.items():
        path     = os.path.join(self.notebookpath, year, month)
        for mday, recordstamplist in mdays.items():
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
          for stamp in recordstamplist:
            f.write ('\n'.join(['@[' + str(self.records[stamp].timestamp) + ']',
                                                   ','.join(self.records[stamp].tags)]))
            for edited_timestamp, content in self.records[stamp].content.items():
              f.write('\n' + '@[' + str(edited_timestamp) + ']')
              for contentline in content.split('\n'):
                f.write('\n' + '\t' + contentline)
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
  def parse_file (path):
    records = {}
    timestamp = 0
    content = {} 
    tags = []
    tag_idx = {}
    sep_mark = re.compile(r"^---oOo---$")
    timestamp_mark = re.compile(r"^@\[\d+\]$")
    contentline_pattern = re.compile(r"^\t.*$")
    
    f = open (path, 'r')

    parse_state = 0 # 0 - none 1 - stamp read 2 - tags read 3 - content read
    for line in f:
      if parse_state == 0:
        if timestamp_mark.match(line):
          timestamp = int(line.strip()[2:-1])
          parse_state = 1
        else:
          continue
      elif parse_state == 1:
        tags = [tag.strip().lower() for tag in line.split(',')]
        if len(tags) == 0:
          tags = ['untagged']
        parse_state = 2 
      elif parse_state == 2:
        if sep_mark.match(line):
          parse_state = 3
          records [timestamp] = Entry({'timestamp': timestamp,
                                                 'tags': list(set(tags.copy())),
                                                 'content': copy.deepcopy(content)})
          #print (tags)
          for t in list(set(tags)):
            if t in tag_idx:
              tag_idx [t].append (timestamp)
            else:
              tag_idx [t] = [timestamp]
          parse_state = 0
          content.clear()
        else:
          if timestamp_mark.match(line):
            temp_timestamp = int(line.strip()[2:-1])
            content [temp_timestamp] = ''
          elif contentline_pattern.match(line):
            content [temp_timestamp] = content [temp_timestamp] + line [1:]
          else:
            pass
      else:
          print ("Error: malfunction")
    
    f.close()
    return records, tag_idx
            
#Test code
#record1 = Entry(Entry.shape_record ("Test hahaha", ["123","test"]))
#sleep(2)
#record2 = Entry(Entry.shape_record ("Test hahahaha", ["123","test2"]))
#notebook = NoteBook ("Test", "/home/hha/Scratches/BAI")
#notebook.fetch_notebook()
#notebook.new_record(record1)
#notebook.new_record(record2)
#notebook.store_notebook()

