#!/usr/bin/env python3
import datetime, calendar
import re

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
import copy

class InlineCalendar:
	def __init__ (self, name):
		self.name = name
		self.selected_dates = {}

	def reset (self):
		self.selected_dates.clear()

	@property
	def currentYear (self):
		return self._currentYear

	@property
	def currentMonth (self):
		return self._currentMonth

	@currentMonth.setter
	def currentMonth (self, value):
		self._currentMonth = value

	@currentYear.setter
	def currentYear (self, value):
		self._currentYear = value

	def set_calendar_tree (self, datetree):
		"""
		datetree should like this ['year']['month']['date'] = quoted value
		quoted value will show by the date
		"""
		self.datetree = datetree.copy()

	def set_view (self, hasAll = True, hasDone = True, hasCancel = True):
		self.hasAllOption      = hasAll
		self.hasDoneOption     = hasDone
		self.hasCancelOption   = hasCancel
		self.AllOptionSelected = False
		self.SelectDone        = False
		self.SelectCancel      = False

		self.month_table       = []

		if self.hasAllOption:
			self.month_table.append([InlineKeyboardButton('Select All',
				callback_data=self.name + '__All')])

		self.month_table.append([InlineKeyboardButton(str(self.currentYear), callback_data = self.name + '__' + str(self.currentYear))])
		curMonthbtn = InlineKeyboardButton(str(self.currentMonth), callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth))
		nxtMonthbtn = InlineKeyboardButton(">", callback_data = self.name + '__nxtMonth')
		prvMonthbtn = InlineKeyboardButton("<", callback_data = self.name + '__prvMonth')
		nxtYearbtn = InlineKeyboardButton(">>", callback_data = self.name + '__nxtYear')
		prvYearbtn = InlineKeyboardButton("<<", callback_data = self.name + '__prvYear')
		self.month_table.append([prvYearbtn, prvMonthbtn, curMonthbtn, nxtMonthbtn, nxtYearbtn])

		MonBtn = InlineKeyboardButton("M", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Mon')
		TueBtn = InlineKeyboardButton("T", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Tue')
		WedBtn = InlineKeyboardButton("W", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Wed')
		ThuBtn = InlineKeyboardButton("R", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Thu')
		FriBtn = InlineKeyboardButton("F", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Fri')
		SatBtn = InlineKeyboardButton("S", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Sat')
		SunBtn = InlineKeyboardButton("U", callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + 'Sun')
		self.month_table.append([MonBtn, TueBtn, WedBtn, ThuBtn, FriBtn, SatBtn, SunBtn])

		wday = 0
		num_days = calendar.monthrange(self.currentYear, self.currentMonth)[1]
		wday = datetime.date (self.currentYear, self.currentMonth, 1).weekday()
		# prepare blank button
		BlnkBtn = InlineKeyboardButton(" ", callback_data = self.name + "__blnk")
		# fill blank button to unused day in week
		week = []
		for day in range (0, wday):
			week.append (BlnkBtn)
		for day in range (1, num_days + 1):
			week.append (InlineKeyboardButton(str(day), callback_data = self.name + '__' + str(self.currentYear) + '__' + str(self.currentMonth) + '__' + str(day)))
			wday += 1
			if wday > 6:
				wday = 0
				self.month_table.append(week)
				week = []

		if wday > 0:
			wday -= 1
			if wday < 0:
				wday = 6
			for day in range (wday, 6):
				week.append (BlnkBtn)
		self.month_table.append(week)

		text_line = []
		if self.hasDoneOption:
			text_line.append(InlineKeyboardButton('Done', callback_data = self.name + '__Done'))
		if self.hasCancelOption:
			text_line.append(InlineKeyboardButton('Cancel', callback_data = self.name + '__Cancel'))
		if len(text_line) != 0:
			self.month_table.append(text_line.copy())
	
	def refresh_view (self):
		self.set_view (self.hasAllOption, self.hasDoneOption, self.hasCancelOption)
	
	def parse_cb_data (self, cb_data):
		if cb_data.find (self.name + '__') == 0:
			cb_data = cb_data.replace (self.name + '__','')
			if cb_data == 'nxtMonth':
				return ['nxtM']
			elif cb_data == 'nxtYear':
				return ['nxtY']
			elif cb_data == 'prvMonth':
				return ['prvM']
			elif cb_data == 'prvYear':
				return ['prvY']
			else:
				select_date_re  = re.compile(r"^(\d+)__(\d+)__(\d+)$")
				select_month_re = re.compile(r"^(\d+)__(\d+)$")
				select_year_re  = re.compile(r"^(\d+)$")
				select_wday_re  = re.compile(r"(\d+)__(\d+)__([A-Z][a-z][a-z])$")
				if select_wday_re.match(cb_data):
					return ['wday', select_wday_re.match(cb_data).group(1), select_wday_re.match(cb_data).group(2), select_wday_re.match(cb_data).group(3)]
				elif select_date_re.match(cb_data):
					return ['date', select_date_re.match(cb_data).group(1), select_date_re.match(cb_data).group(2), select_date_re.match(cb_data).group(3)]
				if select_month_re.match(cb_data):
					return ['month', select_month_re.match(cb_data).group(1), select_month_re.match(cb_data).group(2)]
				if select_year_re.match(cb_data):
					return ['year', select_year_re.match(cb_data).group(1)]
		else:
			return ['None']

	def select (self, selected_cb):
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
			command = self.parse_cb_data (selected_cb)
			if command [0] == 'None':
				return
			else:
				if command [0] == 'prvY':
					self.currentYear -= 1
					self.refresh_view()
				elif command [0] == 'nxtY':
					self.currentYear += 1
					self.refresh_view()
				elif command [0] == 'prvM':
					self.currentMonth -= 1
					self.refresh_view()
				elif command [0] == 'nxtM':
					self.currentMonth += 1
					self.refresh_view()
				elif command [0] == 'year':
					print ("year")
					print (command)
				elif command [0] == 'month':
					print ("month")
					print (command)
				elif command [0] == 'wday':
					print ("wday")
					print (command)
				elif command [0] == 'date':
					print ("date")
					print (command)
				else:
					print ('Unsupported command.')
					return

	def get_InlineKeyboardMarkup (self):
		return InlineKeyboardMarkup (copy.deepcopy(self.month_table))
