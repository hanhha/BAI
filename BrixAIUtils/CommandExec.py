#!/usr/bin/env python3
import sys, subprocess
import json

class CommandExec (object):
  def __init__ (self, shortcuts, extra_stop_func = None):
    """
    """
    self.cmds_name = ()
    self.cmds_obj = dict ()
    self.supported_cmds = shortcuts
    self.stop_in_schdule = extra_stop_func

  def run (self, cmd_name):
    if cmd_name in self.cmds_obj:
      return 3
    elif cmd_name not in self.supported_cmds:
      return 2
    else:
      cmdlist = self.supported_cmds[cmd_name].split()
      self.cmds_obj [cmd_name] = subprocess.Popen (cmdlist)
      return 0

  def kill (self, cmd_name, extra_kill = None):
    if cmd_name in self.cmds_obj:
      self.cmds_obj[cmd_name].kill ()
      return 10 
    else:
      if extra_kill is not None and self.stop_in_schdule is not None:  
        self.stop_in_schdule (cmd_name)
      return 12

  def list (self):
    return [*self.cmds_obj]

  def intepret (self, code):
    if code == 0:
      return "Command has been started."
    if code == 2:
      return "Unknown command."
    if code == 3:
      return "Command has been running already."
    if code == 10:
      return "Command should stop now."
    if code == 12:
      return "If this command was started in schedule, it should stop now."
