class State:
	def __init__ (self, name):
		self.name = name
	def __str__ (self): return self.name
	def __cmp__ (self, other):
		return cmp (self.name, other.name)
	def __hash__ (self):
		return hash(self.name)

	def run(self, input, args):
		assert 0, "run not implemented"

	def next(self, input, args):
		assert 0, "next not implemented"

class StateMachine:
	def __init__(self, initialState):
		self._currentState = initialState

	# Template method
	def switchwork (self, tempState):
		self._prvState = self._currentState
		self._currentState = tempState
		print (self._currentState)
	
	def withdrawwork (self):
		self._currentState = self._prvState
		print (self._currentState)

	def on_event (self, input, args):
			self._currentState = self.currentState.next(input, args)
			self._currentState.run (input, args)
	
	@property
	def currentState(self):
		return self._currentState

class Action:
	def __init__ (self, action, prefix):
		self.action = prefix + "_" + action
	def __str__ (self): return self.action
	def __cmp__ (self, other):
		return cmp (self.action, other.action)
	def __hash__ (self):
		return hash(self.action)

