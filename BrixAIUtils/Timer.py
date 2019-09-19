#!/usr/bin/env python3
from datetime import datetime

class Timer (object):
  def __init__ (self, telegram_job_queue, exec_func):
    """
    """
    self.exec_func  = exec_func
    self.job_queue  = telegram_job_queue
    self.job_record = dict ()

  def remove (self, cmd, timestamp):
    if timestamp in self.job_record:
      if cmd in self.job_record [timestamp]:
        self.job_record [timestamp][cmd].schedule_removal ()
        self.job_record [timestamp].remove (cmd)
        if size(self.job_record[timestamp]) == 0:
          del self.job_record [seconds]
        return 10
      else:
        return 12
    else:
       return 12

  def add (self, cmd, timestamp):
    if timestamp not in self.job_record:
      self.job_record [timestamp] = dict ()
    if cmd in self.job_record [timestamp]:
      return 3

    try:
      desired_time = datetime.strptime(timestamp, "%H:%M:%S").time ()
    except:
      return 1

    self.job_record [timestamp][cmd] = self.job_queue.run_once (lambda x,y: self.exec_func (cmd), when = desired_time)
    return 0

  def list (self):
    #TODO
    pass

  def intepret (self, code):
    if code == 0:
      return "Scheduled."
    if code == 1:
      return "Wakaranai."
    if code == 3:
      return "There is same action at that time."
    if code == 10:
      return "Removed."
    if code == 12:
      return "This action is no longer scheduled."
