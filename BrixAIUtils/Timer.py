#!/usr/bin/env python3
from datetime import datetime

class Timer (object):
  def __init__ (self, telegram_job_queue, exec_func):
    """
    """
    self.exec_func  = exec_func
    self.job_queue  = telegram_job_queue
    self.job_record = dict ()

  def exec_wrap (self, when, cmd):
    self.exec_func (cmd)
    self.job_record [when][cmd]["executed"] = True

  def remove (self, cmd, timestamp):
  #TODO #Enhancement support cmd is a list
  #TODO #Enhancement support cmd is empty ( => remove all)
    try:
      desired_time = datetime.strptime(timestamp, "%H:%M:%S").time ().strftime("%H:%M:%S")
    except:
      return 1

    self.clean ()

    if desired_time in self.job_record:
      if cmd in self.job_record [desired_time]:
        self.job_record [desired_time][cmd]["ptr"].schedule_removal ()
        del self.job_record [desired_time][cmd]
        if len(self.job_record[desired_time]) == 0:
          del self.job_record [desired_time]
        return 10
      else:
        return 12
    else:
       return 12

  def add (self, cmd, timestamp):
  #TODO #Enhancement support cmd is a list
    try:
      desired_time = datetime.strptime(timestamp, "%H:%M:%S").time ()
      desired_time_str = desired_time.strftime("%H:%M:%S") 
    except:
      return 1

    self.clean ()

    if desired_time_str not in self.job_record:
      self.job_record [desired_time_str] = dict ()
    if cmd in self.job_record [desired_time_str]:
      return 3

    self.job_record [desired_time_str][cmd] = {"executed":False,"ptr":self.job_queue.run_once (lambda bot,_job: self.exec_wrap (desired_time_str, cmd), when = desired_time)}
    return 0

  def clean (self):
    cleaned_dict = dict ()
    for k,v in self.job_record.items ():
      for jname, jinfo in v.items ():
        if (not jinfo["executed"]) and (not jinfo["ptr"].removed):
          if k not in cleaned_dict:
            cleaned_dict [k] = dict ()
          cleaned_dict [k][jname] = jinfo
    self.job_record = cleaned_dict

  def list (self):
    self.clean ()
    return {k:v.keys() for k,v in self.job_record.items()}

  def intepret (self, code):
    if code == 0:
      return "Scheduled."
    if code == 1:
      return "Invalid time info."
    if code == 3:
      return "There is same action at that time."
    if code == 10:
      return "Removed."
    if code == 12:
      return "This action is no longer scheduled."
