#!/usr/bin/env python3
import datetime, calendar

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
import copy

class InlineOptions:
	def __init__ (self, name):
		self.name              = name
	
	def set_options (self, options, callback_data_list,  hasAll = True, hasDone = True, hasCancel = True):
		self.option_data_list            = options.copy()
		self.selected_data_list          = [] 
		self.callback_data_list          = [(self.name + "_" + cb_item) for cb_item in callback_data_list]
		self.hasAllOption      = hasAll
		self.hasDoneOption     = hasDone
		self.hasCancelOption   = hasCancel
		self.AllOptionSelected = False
		self.SelectDone        = False
		self.SelectCancel      = False

		self.text_select = []
		self.cb_pos = {}

		char_quota = 50 

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

	@property
	def selectedOptions (self):
		trunc_len = len(self.name) + 1
		return [selected_item[trunc_len:] for selected_item in self.selected_data_list]

	def select (self, selected_cb):
		if selected_cb == self.name + '__All':
			self.AllOptionSelected = True
			self.SelectDone = True
		elif selected_cb == self.name + '__Done':
			self.SelectDone = True
		elif selected_cb == self.name + '__Cancel':
			self.selected_data_list.clear()
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
