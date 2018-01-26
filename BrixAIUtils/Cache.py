# Read-only LRU cache
class Cache:
	def __init__ (self, name, capacity):
		self.name = name
		self.capacity = capacity
		self.cache = {}
		self.lru = [] 
	
	def flush (self):
		self.cache.clear()
		self.lru.clear()

	@staticmethod
	def split_text (text, framesize):
		chunks = len(text)
		ret_list = [text[i:i+framesize] for i in range(0, chunks, framesize)]
		return ret_list

	def read (self, tag):
		if tag in self.cache:
			#cache hit
			self.lru.remove(tag)
			self.lru.insert(0,tag)
		else:
			#cache miss
			value = self.fetch (tag)
			if len(self.lru) == self.capacity:
				# find LRU unit
				lru_tag = self.lru.pop()
				removed_value = self.cache.pop (lru_tag)
			self.lru.insert(0,tag)
			self.cache[tag] = value
		return self.split_text(self.cache[tag], 3000)

		def fetch (self, tag):
			assert 0, "fetch not implemented" 
