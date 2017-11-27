#!/usr/bin/env python3

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
import copy

class InlineOptions:
	def __init__ (self, name):
		self.name              = name
	
	def set_options (self, options, callback_data_list,  hasAll = True, hasDone = True, hasCancel = True):
		self.option_data_list            = options.copy()
		self.selected_data_list          = [] 
		self.callback_data_list          = callback_data_list.copy()
		self.hasAllOption      = hasAll
		self.hasDoneOption     = hasDone
		self.hasCancelOption   = hasCancel
		self.AllOptionSelected = False
		self.SelectDone        = False
		self.SelectCancel      = False

		self.text_select = []
		self.cb_pos = {}

		char_quota = 25

		if self.hasAllOption:
			self.text_select.append([InlineKeyboardButton('Select All',
				callback_data=self.name + '__All')])
	
		text_line = []
		quota = char_quota
		for i in range (len(self.option_data_list)):
			if quota - len(self.option_data_list[i]) < 0:
				self.text_select.append (text_line.copy())
				text_line = []
				quota = char_quota
			text_line.append (InlineKeyboardButton(self.option_data_list[i], callback_data=self.callback_data_list[i]))
			quota -= len(self.option_data_list[i])
			self.cb_pos [self.callback_data_list[i]] = (len(self.text_select),len(text_line)-1)
		self.text_select.append (text_line.copy())

		text_line = []
		if self.hasDoneOption:
			text_line.append(InlineKeyboardButton('Done', callback_data = self.name + '__Done'))
		if self.hasCancelOption:
			text_line.append(InlineKeyboardButton('Cancel', callback_data = self.name + '__Cancel'))
		if len(text_line) != 0:
			self.text_select.append(text_line.copy())

	def select (self, selected_cb):
		if type(selected_cb) == 'set':
			for i, t in enumerate(self.callback_data_list):
				if t in selected_cb:
					pos = self.cb_pos[t]
					self.text_select [pos[0]][pos[1]] = InlineKeyboardButton('(+)' + self.option_data_list [i], callback_data = self.callback_data_list[i])
				else: 
					pos = self.cb_pos[self.callback_data_list[i]]
					self.text_select [pos[0]][pos[1]] = InlineKeyboardButton(self.option_data_list [i], callback_data = self.callback_data_list[i])
					
			self.selected_data_list = dict(selected_cb.copy())
		else:
			if selected_cb == self.name + '__All':
				self.AllOptionSelected = True
				self.SelectDone = True
				#self.selected_data_list = []
			elif selected_cb == self.name + '__Done':
				self.SelectDone = True
			elif selected_cb == self.name + '__Cancel':
				self.selected_data_list = []
				self.SelectCancel = True
			else: # toggle select status
					i = self.callback_data_list.index(selected_cb)
					pos = self.cb_pos[selected_cb]
					if selected_cb in self.selected_data_list:
						select_sts_str = ''
						self.selected_data_list.remove(selected_cb)
					else:
						select_sts_str = '(+)'
						self.selected_data_list.append(selected_cb)
					self.text_select [pos[0]][pos[1]] = InlineKeyboardButton(select_sts_str + self.option_data_list [i], callback_data = self.callback_data_list[i])

	def get_InlineKeyboardMarkup (self):
		return InlineKeyboardMarkup (copy.deepcopy(self.text_select))
