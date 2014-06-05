
class Syntax:
	def __init__ (self):
		0
		self.type_basics = ['int', 'float', 'char']
		self.keywords = ['if', 'else', 'eslif', 'for', 'while']
		
		self.begins = ['keyword', 'typedec', 'function_def']
		
		self.delimeters = ['\n', '\t', ' ', ':', '#', '+', '-']
		
	
	# Token definitions
		
	def name(self, char):
		if char.isalnum() or char == '_':
			return True

	def comment_single(self, char):
		if char == '#':
			return True
		
	def comment_single_delim(self, char):
		if char == '\n':
			return True
			
	def number(self, char):
		if char.isdigit():
			return True
			
	def type_name_get(self, string):
		if string in self.keywords:
			return 'keyword'
		elif string in self.type_basics:
			return 'typedec'
		else:
			return 'reference'
			
	def type_reference_get(self, string):
		return 'err'
		
	def string(self, char):
		if char.isalnum() or char == '.':
			return True
		return False
		
	def begins_statement(self, string):
		if string in self.begins:
			return True
		return False
	
	
	# errors
	
	def err(self, string):
		print("err: " + string)
		exit(0)

class Tokenizer:
	class Token:
		def __init__ (self, src, syn, prev, start, end, type):
			self.src = src
			self.start = start
			self.end = end
			self.prev = prev
			self.next = None
			self.type = type
			self.syn = syn
			self.tkfirst = 0
			
			self.name = ["keyword", "typedec", "reference"]
			self.keywords = ["if", "else", "elsif", "for", "while"]
			self.typedec = "typedec"
			self.reference = ["function", "variable"]
			
		# Helper
			
		def string(self):
			return self.src[self.start:self.end]
			
		def print(self):
			if self.string() == '\n':
				out = '\\n'
			elif self.string() == '\t':
				out = '\\t'
			else:
				out = self.string()
			print(out + " (" + self.type + ")")
			
		def pri(self):
			if self.string() == '\n':
				return '\\n'
			elif self.string() == '\t':
				return '\\t'
			else:
				return self.string()
		
		# Type Check
			
		def is_name(self):
			if self.type == 'name':
				return True
			return False
			
		def is_keyword(self):
			if self.string() in self.syn.keywords:
				return True
			return False
			
		def is_type(self):
			if self.string() in self.syn.type_basics:
				return True
			return False

	def __init__ (self, src, syn):
		self.syn = syn
		self.src = src
		self.pos = 0
		self.start = 0
		self.end = 0
		
		self.tk = None
		self.tk_type = 'none'
		
		self.scope = 0
		
	# Helper
	
	def char(self):
		return self.src[self.pos]
		
	def more(self):
		return self.pos < len(self.src)
		
	def string(self):
		return self.src[self.start:self.end]
	
	# Word Grammar
	
	def name(self):													# Name
		self.start = self.pos
		while self.more() and self.syn.name(self.char()):
			self.pos += 1
		self.end = self.pos
		
		# look ahead
		#if self.next():
		#	0
		
		#	if self.tk.next.type == 'function_def':
		#		self.tk.type = 'function_def'
		
		self.tk_type = 'name'
	
	def single(self):
		self.start = self.pos
		self.pos += 1
		self.end = self.pos
	
	def space(self):												# Space
		while self.more() and self.char() == ' ':
			self.pos += 1
			
	def pound(self):
		while self.more() and self.char() != '\n':
			self.pos += 1
				
	def number(self):												# Number
		self.start = self.pos
		while self.more() and self.syn.number(self.char()):
			self.pos += 1
		self.end = self.pos
		
		self.tk_type = 'number'
	
	def newline(self):												# \n
		self.pos += 1
		while self.more() and self.src[self.pos] == '\n':
			self.pos += 1
		
		self.start = self.pos - 1
		self.end = self.pos
		
		self.tk_type = 'newline'
		self.scope = 0
		
	def plussign(self):												# +
		self.single()
		self.tk_type = 'plus'
		
	def colon(self):												# :
		self.start = self.pos
		self.pos += 1
		
		if self.more() and self.char() == ':':
			self.pos += 1
			self.tk_type = 'function_def'
		else:
			self.tk_type = 'function_call'
		
		self.end = self.pos
		
	def tab(self):
		self.single()
		self.tk_type = 'tab'
		self.scope += 1
		
	def paren_single(self):
		self.pos += 1
		self.start = self.pos
		while self.more() and self.syn.string(self.char()) and self.char() != '\'':
			self.pos += 1
		
		self.end = self.pos
		self.pos += 1
		
		self.tk_type = 'const_string'
	
	# Advancement
	
	def adv(self):
		if self.tk:
			if self.tk.next:
				self.tk = self.tk.next
			else:
				self.tk = self.get()
		else:
			self.tk = self.get()
			self.tkfirst = self.tk
		
		#self.token_reduce()
			
		return self.tk	
		
	def token_reduce(self):
		if self.tk_type == 'name':
			if self.next():
				if self.next().type == 'function_call' or self.next().type == 'function_def':
					self.tk.type = self.next().type
					self.tk.next = self.get()
				
				if self.tk.is_keyword() or self.tk.is_type():
					self.tk.type = self.tk.string()
	
	def next(self):
		if self.tk.next:
			return self.tk.next
		self.tk.next = self.get()
		return self.tk.next
		
	def look(self):
		if self.more():
			return self.src[self.pos + 1]
		return None
		
	def get(self):
		if not self.more():
			return None
					
		if self.char() == ' ':
			self.space()
			
		if self.char() == '#':
			self.pound()
				
		if self.char() == '\n':
			self.newline()
			
		elif self.char() == '\t':
			self.tab()
			
		elif self.char() == '+':
			self.plussign()
			
		elif self.char() == ':':
			self.colon()
			
		elif self.char() == '\'':
			self.paren_single()
		
		elif self.char().isalpha():
			self.name()
			
		elif self.char().isdigit():
			self.number()
		
		
		tk = self.Token(self.src, self.syn, self.tk, self.start, self.end, self.tk_type)
		if self.tk:
			#print(self.tk.pri() + '-' + tk.pri())
			self.tk.next = tk
			
		return tk


	def next_string(self):
		pos = self.pos
		
	def next_skip(self):
		0
		
	def skip(self):
		0
		
class Token2:
	class Str:
		def __init__(self, start, end):
			self.start = 0
			self.end = 0
			self.prev = None
			self.next = None

	def __init__ (self, src, syn):
		self.src = src
		self.syn = syn

		self.pos = 0
		self.begin = 0
		self.end = 0

		self.tk = None

		self.check_nothing()
		
	def check_nothing(self):
		if len(self.src) == 0:
			print('source file is empty')
			exit(0)
			
		while self.more() and self.char_is_newline():
			self.pos += 1
			
		if self.pos == len(self.src):
			print('main not defined')
			exit(0)

	# Helper
		
	def char(self):
		return self.src[self.pos]
		
	def char_is_newline(self):
		return self.char() == '\n'
		
	def more(self):
		return self.pos < len(self.src)
		
	# Advancement
	
	def get_next_tokenz(self):
		if not self.more():
			return None
					
		if self.char() == ' ':
			self.space()
			
		if self.char() == '#':
			self.pound()
				
		if self.char() == '\n':
			self.newline()
			
		elif self.char() == '\t':
			self.tab()
			
		elif self.char() == '+':
			self.plussign()
			
		elif self.char() == ':':
			self.colon()
			
		elif self.char() == '\'':
			self.paren_single()
		
		elif self.char().isalpha():
			self.name()
			
		elif self.char().isdigit():
			self.number()
			
	
	def get_next_string(self):
		0	
			
	def adv(self):
		self.get_next_string()
		return False
	
	
class Generator:
	def __init__ (self):
		0

class Parser:
	class Function:
		def __init__ (self):
			self.args = []
			
	class Namespace:
		def __init__ (self, prev):
			self.items = {}
			self.prev = prev
			self.next = None
			
		def find(self, tk):
			if tk.string() in self.items:
				return True
			return False
			
		def insert(self, tk):
			self.items[tk.string()] = tk.type
		
	def __init__ (self, tokenizer, syn, generator):
		self.tkr = tokenizer
		self.syn = syn
		self.namespace = self.Namespace(None)
		
	# errors
	def err(self, string):
		print('parse error: ' + string);
		exit(0)
		
	# checks
	def begin_check(self, tk):
		if self.syn.begins_statement(tk.type):
			return True
		else:
			self.err('statement can not start with: ' + tk.type)
			
	# types
	def function_def(self):
		if self.namespace.find(self.tkr.tk):			# check for duplicate name
			self.err('duplicate name')
		
	# run
	def run(self):
		while self.tkr.adv() and self.tkr.tk == '\n':		# no newline at start
			self.tkr.tk.adv()
		
		while self.tkr.adv():
			self.tkr.tk.print()
		
		exit(0)
			
		while 1:
			tk.print()

			if tk.type == 'function_def':
				self.function_def()
				0
			elif tk.type == 'function_call':
				0
			elif tk.type == 'variable':
				0
			elif tk.type == 'type_dec':
				0
			elif tk.type == 'keyword':
				0
			

class Compiler:
	def __init__ (self, file):
		self.src = open(file, 'r').read()
		self.syntax = Syntax()
		self.tokenizer = Token2(self.src, self.syntax)
		self.generator = Generator()
		self.parser = Parser(self.tokenizer, self.syntax, self.generator)
		self.parser.run()

compiler = Compiler('main.b')
#compiler = Compiler('nothing')
