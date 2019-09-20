#!/usr/bin/env python3

import sys, subprocess
import json
import time

class CommandExec (object):
  def __init__ (self, shortcuts):
    self.cmds_obj = dict ()
    self.supported_cmds = shortcuts

  def run (self, cmd_name):
  #TODO #Enhancement support cmd_name is a list
    self.clean ()

    if cmd_name in self.cmds_obj:
      return 3
    elif cmd_name not in self.supported_cmds:
      return 2
    else:
      cmdlist = self.supported_cmds[cmd_name]["cmd"].split()
      self.cmds_obj [cmd_name] = subprocess.Popen (cmdlist)
      return 0

  def clean (self):
    cleaned_dict = dict ()
    for k,v in self.cmds_obj.items () :
      v.poll ()
      if v.returncode is None:
        cleaned_dict [k] = v
    self.cmds_obj = cleaned_dict

  def kill (self, cmd_name):
  #TODO #Enhancement support cmd_name is a list
  #TODO #Enhancement support cmd_name is empty ( => remove all)
    if cmd_name in self.cmds_obj:
      self.cmds_obj [cmd_name].poll ()
      if self.cmds_obj [cmd_name].returncode is None:
        self.cmds_obj[cmd_name].terminate ()
        self.cmds_obj [cmd_name].poll () 
        count = 0
        while (self.cmds_obj [cmd_name].returncode is None) and (count < 4):
          self.cmds_obj [cmd_name].poll ()
          time.sleep (1)
          count += 1
      if self.cmds_obj [cmd_name].returncode is not None:
        del self.cmds_obj [cmd_name]
        return 10
      else:
        return 11
    else:
      return 12

  def support (self):
    return {k:v["desc"] for k,v in self.supported_cmds.items()}

  def list (self):
    self.clean ()
    return [*self.cmds_obj]

  def intepret (self, code):
    if code == 0:
      return "Task has been started."
    if code == 2:
      return "Unknown task."
    if code == 3:
      return "Task has been running already."
    if code == 10:
      return "Task should stop now."
    if code == 11:
      return "This task is being performed heavily. Please try again later."
    if code == 12:
      return "This task is not running."
