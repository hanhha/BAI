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
    self.plain_textlist = [] 
    self.md_textlist = []

  def add (self, content, tags = [], replace_tag = False):
    if replace_tag:
      self.set_tags (tags)
    else:
      self.add_tags (tags)
    inttime = int(time())
    if self.record ['timestamp'] == 0 :
      self.record ['timestamp'] = inttime
    self.record ['content'] [inttime] = content
    # Flush cached representation strings
    self.plain_textlist = [] 
    self.md_textlist = []

  def add_tags (self, tags):
    if type(tags) is list:
      if len(tags) == 0: 
        pass
      else:
        if self.record ['tags'][0] == 'untagged':
          self.record['tags'].clear()
        self.record['tags'].extend(tags.copy())
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
  def date_str (timestamp, prefix, ftime):
    ret_str = []
    ret_str.append(prefix + strftime ('%Y-%m-%d %H:%M:%S', ftime (timestamp)))
    ret_str.append('_' + ret_str [0] + '_')
    return ret_str

  @staticmethod
  def tags_str (tagslist):
    if tagslist [0] == 'untagged':
      return ['','']
    else:
      ret_str = ', '.join(tagslist)
      return [ret_str, '*' + ret_str + '*']
  
  @staticmethod
  def split_content (timestamp, content, prefix, framesize, ftime = gmtime):
    ret_list = []
    md_ret_list = []
    ret_str = ''
    md_ret_str = ''
    [ret_str, md_ret_str] = Entry.date_str (timestamp, prefix, ftime)
    text = content
    quota = framesize - len(ret_str)
    if quota <= 0:
      ret_list.append (ret_str)
      md_ret_list.append (md_ret_str)
      (ret_str, md_ret_str) = ('','')
    else:
      if quota >= len(text):
        ret_str += '\n' + text
        md_ret_str += '\n' + '```\n' + text + '\n```'
        #print (ret_str)
        #print (md_ret_str)
        return [[ret_str], [md_ret_str]]
      else:
        tmp_str = text [0:quota-1]
        text = text [quota:]
        ret_str += '\n' + tmp_str
        md_ret_str += '\n' + '```\n' + tmp_str + '\n```'
        ret_list.append (ret_str)
        md_ret_list.append (md_ret_str)
        (ret_str, md_ret_str) = ('','')
    
    #print ("split")
    #print (text)
    chunks = len(text)
    for i in range (0, chunks, framesize):
      text_list = text[i:i+framesize] 
      md_text_list = '```\n' + text[i:i+framesize] + '\n```' 

    ret_list.extend (text_list)
    md_ret_list.extend (md_text_list)
    #print ("Split")
    #print (ret_list)
    #print (md_ret_list)
    return [ret_list, md_ret_list]
    
  def to_str (self, Markdown = False, ftime = gmtime, joined = False):
    tlist = []
    if not Markdown and len(self.plain_textlist) > 0:
      tlist = self.plain_textlist
    if Markdown and len(self.md_textlist) > 0:
      tlist = self.md_textlist
    if len(tlist) > 0:
      if joined:
        return '\n'.join(tlist)
      else:
        return tlist
    else:
      ret_list = []
      md_ret_list = []
      ret_str = ''
      md_ret_str = ''
      [ret_str, md_ret_str] = self.tags_str (self.record ['tags'])

      for timestamp, content in sorted (self.record['content'].items(), key = lambda t: t[0], reverse = False):
        if timestamp == self.record ['timestamp']:
          [tmp_list, md_tmp_list] = self.split_content (timestamp, content, "Created in ", 3000, ftime) 
        else:
          [tmp_list, md_tmp_list] = self.split_content (timestamp, content, "Edited in ", 3000, ftime) 
        ret_list.extend(tmp_list.copy())
        md_ret_list.extend(md_tmp_list.copy())
      ret_list [0] = ret_str + '\n' + ret_list [0]
      md_ret_list [0] = md_ret_str + '\n' + md_ret_list [0]

      self.plain_textlist = ret_list.copy()
      self.md_textlist = md_ret_list.copy()

      tlist = []
      if not Markdown:
        tlist = self.plain_textlist
      else:
        tlist = self.md_textlist
      #print  ("to_str")
      #print(tlist)
      if joined:
        return '\n'.join(tlist)
      else:
        return tlist

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

  def append_record (self, extra_record_dict, inttime):
    """
    in this case, timestamp is existed in timetree
    The existed one will be removed from timetree and all linked structures, and new one will be added to changed_timetree
    """
    if self.editable:
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

      #print (self.changed_timetree)
      #print (self.timetree)

      # Add new tags
      tags = extra_record_dict['tags']
      for tag in tags:
          if tag in self.tags:
              self.tags[tag].append (inttime)
          else:
              self.tags[tag] = [inttime]
      
      # Change in records
      self.records[inttime].add(extra_record_dict['content'], extra_record_dict['tags'])

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

  def pop_record (self, timestamp):
    """
    in this case, timestamp is existed in timetree
    The existed one will be removed from timetree and all linked structures
    """
    if self.editable:
      inttime    = timestamp

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
      # Delete record in changed_timetree
      del self.changed_timetree [year][month][day][inttime]

      # Delete in records
      ret_record = self.records.pop(inttime)

      # Delete from tags list
      for tag in ret_record.tags:
        self.tags['tag'].remove(inttime)
      
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
      return ret_record
    else:
      return None

  def query_tags (self):
      tagscloud = {}
      for k, v in self.tags.items():
          tagscloud [k] = len(v)
      return tagscloud

  def query_dates (self):
    ret_timetree = {}
    for year, months in self.changed_timetree.items():
      ret_timetree [year] = {}
      for month, mdays in months.items():
        ret_timetree [year] [month] = {}
        for mday, recordstamplist in mdays.items():
          ret_timetree [year] [month] [mday] = len(recordstamplist)
    for year, months in self.timetree.items():
      if year not in ret_timetree:
        ret_timetree [year] = {}
      for month, mdays in months.items():
        if month not in ret_timetree [year]:
          ret_timetree [year] [month] = {}
        for mday, recordstamplist in mdays.items():
          if mday not in ret_timetree [year][month]:
            ret_timetree [year] [month] [mday] = len(recordstamplist)
          else:
            ret_timetree [year] [month] [mday] += len(recordstamplist)
    return ret_timetree

  def query_date_records (self, datetree):
      return []

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
                os.mkdir (path)
          else:
            self.timetree[year] = {month : {mday : self.changed_timetree[year][month][mday].copy()}} 
            os.makedirs (path)
            
          f = open (filename, 'a')
          for stamp in recordstamplist:
            f.write ('\n'.join(['@[' + str(self.records[stamp].timestamp) + ']',
                                                   ','.join(self.records[stamp].tags)]))
            for edited_timestamp, content in sorted (self.records[stamp].content.items(), key = lambda t: t[0], reverse = False):
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

