

class Compiler:

	class Rules:
		
		class Reader:
			def __init__(self, src):
				self.src = open(src).read()
				self.pos = 0
				self.line = 1
				self.col = 0
				
			def char(self):
				if self.more():
					return self.src[self.pos]
				else:
					return 'eof'
				
			def more(self):
				return self.pos < len(self.src)
				
			def adv(self):
				self.col += 1
				if self.char() == '\n':
					self.line += 1
					self.col = 0
				self.pos += 1
			
			def adv_end(self):
				self.pos = len(self.src)
								
			def skip_whitespace(self):
				while self.more() and self.char() == ' ' or self.char() == '\n' or self.char() == '\t':
					self.adv()
					
			def skip_space_and_tab(self):
				while self.more() and self.char() == ' ' or self.char() == '\t':
					self.adv()
			
			def get_name(self):
				self.skip_whitespace()
				start = self.pos
				while self.char().isalpha() or self.char() == '_':
					self.adv()
				
				if start == self.pos:
					return None
			
				return self.src[start:self.pos]		
				
			def match_adv(self, string):
				self.skip_whitespace()
				x = 0
				while self.more() and x < len(string) and self.src[self.pos + x] == string[x]:
					x += 1

				if x == len(string):
					self.pos += x
					return True

				return False
				
			def get_single(self):
				self.skip_whitespace()
			
				if self.char() == '\\':
					self.adv()
					if not self.more():
						return None
					
					if self.char() == 'n':
						ch =  '\n'
					elif self.char() == 't':
						ch =  '\t'
				
				else:
					ch =  self.char()
				
				self.adv()
					
				return ch
						
		class DFA:
			
			class State:
				
				class Transition:
					def __init__(self, value, function, state):
						self.value = value
						self.function = function
						self.state = state
					
					def match(self, input):
						return self.function(self.value, input)
						
				def __init__(self):
					self.transitions = [] # ('a', match_one, state)
					self.accept = False
					self.type = None
					self.id = None
		
				def set_type(self, type):
					self.accept = True
					self.type = type
					
				def get_reachable_states(self, input_single):
					transition_states = []
					for transition in self.transitions:
						if transition.match(input_single):
							transition_states.append(transition.state)	
					return transition_states

				def transition_single(self, transition_value, input_single):
					return  input_single == transition_value
					
				def transition_range(self, transition_range, input_single):
					return transition_range.within(input_single)

				def get_transition_cnt(self):
					return len(self.transitions)			
								
				def create_and_insert_transition_range(self, input_range):
					transition = self.Transition(input_range, self.transition_range, self.__class__())
					self.transitions.append(transition)
					return transition
						
				def create_and_insert_transition_single(self, input_single):				
					transition = self.Transition(input_single, self.transition_single, self.__class__())
					self.transitions.append(transition)
					return transition

				def print_transitions(self):
					for trans in self.transitions:
						if str(type(trans.value)) == "<class '__main__.Compiler.Rules.Range'>":
							print(trans.value.min + ':' + trans.value.max)
						else:
							print(trans.value)

			def __init__(self, reader):
				self.reader = reader
				self.state_start = self.State()
				self.state_start.type = 'start'
				self.state_start.id = 0
				
				self.states_cnt = 1
				self.states = []
				self.states.append(self.state_start)
			
			def err(self, string):
				print('DFA error: ' + string)
				exit(0)
				
			def insert(self, state):
				state.id = self.states_cnt
				self.states_cnt += 1
				self.states.append(state)
			
			def set_states_type(self, states, type):
				for state in states:
					if not state.type:
						#print('state[' + str(state.id)+ '] = ' + type)
						state.set_type(type)
			
			def set_states_range_kleene_star(self, states, input_range):
				for state in states:
					transition = state.create_and_insert_transition_range(input_range)
					transition.state = state
			
			def get_reachable_states_single(self, states, input_single):
				states_r = []
				for state in states:
					states_r += state.get_reachable_states(input_single)
					
				return states_r

			def get_reachable_states_range(self, states, input_range, states_all):
							
				states_reachable = []
				for input_number in range(ord(input_range.min), ord(input_range.max)):
					input_single = chr(input_number)
					
					state_r = self.get_reachable_states_single(states, input_single)
					
					for state in state_r:
						if state and state not in states_reachable:
							states_reachable.append(state)
				states_all += states_reachable
						
				if len(states_reachable) == 0:
					return states_all
				else:
					return self.get_reachable_states_range(states_reachable, input_range, states_all)

			def get_reachable_state(self, state, ch):
				states = state.get_reachable_states(ch)
				if len(states) > 0:
					return states[0]
				return None

			def create_and_insert_transition_single(self, states, input_single):
				states_all = []
				for state in states:
					states_all.append(state.create_and_insert_transition_single(input_single).state)
					self.insert(states_all[-1])
				return states_all
			
			def create_and_insert_transition_range(self, states, input_range):
				states_all = []
				for state in states:
					states_all.append(state.create_and_insert_transition_range(input_range).state)
					self.insert(states_all[-1])
				return states_all
	
		class Symbol:
			def __init__(self, value):
				self.value = value
				special = [';', '|', '[', ']', '*']
				singles = [':', '=', '+', '-', '\n', '\t']
				if value in special:
					self.type = value			
				elif value.isalnum() or value in singles:
					self.type = 'single'				
				else:	
					self.type = 'invalid'

		def get_symbol(self):		# change to parse_symbol?
			symbol = self.Symbol(self.reader.get_single())
			if not symbol:
				self.err('symbol err restricted')
			return symbol
		
		class Range:
			def __init__(self, min, max):
				self.min = min
				self.max = max
				self.length = ord(max) - ord(min) + 1
				
			def within(self, input):
				return input >= self.min and input <= self.max
				
			def print(self):
				print('range:' + self.min + '-' + self.max)
		
		def parse_range(self):
			ch = self.reader.char()
			self.reader.adv()
			if self.reader.char() != '-':
				print('err expecting -')
				exit(0)
			self.reader.adv()
			ch2 = self.reader.char()
			self.reader.adv()				# check for closing ]
			self.reader.adv()
			
			return self.Range(ch, ch2)
			
		def __init__(self, src):
			self.reader = self.Reader(src)
			self.dfa = self.DFA(self.reader)
			self.parse_lexer_rules()
			
			self.nfa = self.NFA()
			self.parse_parser_rules()
			
		def err(self, string):
			print('rule parse err: ' + str(self.reader.line) + ":" + str(self.reader.col) + " " + string)
			exit(0)
			
		def get_type_name_and_read_set_operator(self):
			name = self.reader.get_name()
			if not name:
				self.err('rule must start with name')
					
			if not self.reader.match_adv('=>'):
				self.err('name must be followed by => operator')
			return name
			
		def parse_regex(self, states, states_stack, type_name, input_last_single, input_last_range):
			symbol = self.get_symbol()
			
			input_single = None
			input_range = None
							
			if symbol.type == ';':
				self.dfa.set_states_type(states, type_name)
				return
			
			elif symbol.type == '|':														# skipping handle double | error		
				self.dfa.set_states_type(states, type_name)
				states = states_stack[-1]
				
			elif symbol.type == '[':
				input_range = self.parse_range()
				
			elif symbol.type == '*':			
				if input_last_range:
					self.dfa.set_states_range_kleene_star(states, input_last_range)
		
			elif symbol.type == 'single':
				input_single = symbol.value
				#print(symbol.value)
				
			elif symbol.type == 'invalid':
				self.err('restricted symbol in regex')

			if input_single:
				
				#print(symbol.value)
				
				states_r = self.dfa.get_reachable_states_single(states, input_single)
				if not states_r:
					states = self.dfa.create_and_insert_transition_single(states, input_single)
				else:
					states = states_r
					
				input_last_single = input_single
				input_last_range = None
			
			elif input_range:	
				
				input_last_single = None
				input_last_range = input_range	
				
				states_r = self.dfa.get_reachable_states_range(states, input_range, [])
				states_r += states
				
				if len(states_r) == input_range.length:
					0
				else:
					states_r += self.dfa.create_and_insert_transition_range(states_r, input_range)

				states = states_r
			
			self.parse_regex(states, states_stack, type_name, input_last_single, input_last_range)	

		def parse_lexer_rules(self):
			
			while self.reader.more() and self.reader.char() != '#':
				
				type_name = self.get_type_name_and_read_set_operator()
				self.parse_regex([self.dfa.state_start], [[self.dfa.state_start]], type_name, None, None)
				
				self.reader.skip_whitespace()
							
			self.done()
								
		def done(self):
			
			state = self.dfa.state_start
			
			#state = self.dfa.get_reachable_state(state, '\n')
				
			#state = self.dfa.get_reachable_state(state, 'n')
			#print(state.type)
			
			#exit(0)
			
			#state.print_transitions()
			
			#print('\ntype-is:' + str(self.check('\n')))
			
			#print('CONTINUE id only works for a* fix for others ')
			#print('need to decouple states from transitions, multiple transitions to one state')
			
			print('\n--done--')
			
		def check(self, string):
			x = 0
			state = self.dfa.state_start
			while x < len(string):
				
				states = state.get_reachable_states(string[x])
				
				if len(states) == 0:
					state = None
				else:
					state = states[0]
						
				if not state:
					return None
				else:
					if len(state.transitions):
						0
						#print(state.transitions[0].value)
						
				x += 1
			
			return state.type
		
		# NFA and Parser Rules
		class NFAA:
			
			class State:
				
				class Transition:
					def __init__(self, value, function, state):
						self.value = value
						self.function = function
						self.state = state
					
					def match(self, input):
						return self.function(self.value, input)
						
				def __init__(self):
					self.transitions = [] # ('a', match_one, state)
					self.accept = False
					self.type = None
					self.id = None
		
				def set_type(self, type):
					self.accept = True
					self.type = type
					
				def get_reachable_states(self, input_single):
					transition_states = []
					for transition in self.transitions:
						if transition.match(input_single):
							transition_states.append(transition.state)	
					return transition_states

				def transition_single(self, transition_value, input_single):
					return  input_single == transition_value
					
				def transition_range(self, transition_range, input_single):
					return transition_range.within(input_single)

				def get_transition_cnt(self):
					return len(self.transitions)			
								
				def create_and_insert_transition_range(self, input_range):
					transition = self.Transition(input_range, self.transition_range, self.__class__())
					self.transitions.append(transition)
					return transition
						
				def create_and_insert_transition_single(self, input_single):				
					transition = self.Transition(input_single, self.transition_single, self.__class__())
					self.transitions.append(transition)
					return transition

				def print_transitions(self):
					for trans in self.transitions:
						if str(type(trans.value)) == "<class '__main__.Compiler.Rules.Range'>":
							print(trans.value.min + ':' + trans.value.max)
						else:
							print(trans.value)

			def __init__(self):
				self.state_start = self.State()
				self.state_start.type = 'start'
				self.state_start.id = 0
				
				self.states_cnt = 1
				self.states = []
				self.states.append(self.state_start)
			
			def err(self, string):
				print('DFA error: ' + string)
				exit(0)
				
			def insert(self, state):
				state.id = self.states_cnt
				self.states_cnt += 1
				self.states.append(state)
			
			def set_states_type(self, states, type):
				for state in states:
					if not state.type:
						#print('state[' + str(state.id)+ '] = ' + type)
						state.set_type(type)
			
			def set_states_range_kleene_star(self, states, input_range):
				for state in states:
					transition = state.create_and_insert_transition_range(input_range)
					transition.state = state
			
			def get_reachable_states_single(self, states, input_single):
				states_r = []
				for state in states:
					states_r += state.get_reachable_states(input_single)
					
				return states_r

			def get_reachable_states_range(self, states, input_range, states_all):
							
				states_reachable = []
				for input_number in range(ord(input_range.min), ord(input_range.max)):
					input_single = chr(input_number)
					
					state_r = self.get_reachable_states_single(states, input_single)
					
					for state in state_r:
						if state and state not in states_reachable:
							states_reachable.append(state)
				states_all += states_reachable
						
				if len(states_reachable) == 0:
					return states_all
				else:
					return self.get_reachable_states_range(states_reachable, input_range, states_all)

			def get_reachable_state(self, state, ch):
				states = state.get_reachable_states(ch)
				if len(states) > 0:
					return states[0]
				return None

			def create_and_insert_transition_single(self, states, input_single):
				states_all = []
				for state in states:
					states_all.append(state.create_and_insert_transition_single(input_single).state)
					self.insert(states_all[-1])
				return states_all
			
			def create_and_insert_transition_range(self, states, input_range):
				states_all = []
				for state in states:
					states_all.append(state.create_and_insert_transition_range(input_range).state)
					self.insert(states_all[-1])
				return states_all
		
		class Node:
			def __init__(self):
				self.types = []
				self.star = False
				self.optional = False
				self.next = None
	
		class NFA:
	
			class State:
				def __init__(self, name):
					self.star = False
					self.optional = False
					self.name = name
					self.next = {}
			
			def __init__(self):
				self.state_start = self.State('start')
				self.nonterminals = {}
			
			def find_or_insert(self, name):
				0
	
		def parse_grammar_rules(self, name, state, states_next, stack):
			
			self.reader.skip_whitespace()
			if self.reader.match_adv(';'):
				return
			
			if self.reader.match_adv('('):
				stack.append(state)
			
			elif self.reader.match_adv(')'):
				stack.pop()
			
			elif self.reader.match_adv('*'):
				0
				
			elif self.reader.match_adv('->'):
				node = stack[-1]
				
			
			elif self.reader.match_adv('|'):
				name = self.reader.get_name()
			
			else:
				name = self.reader.get_name()
				#states_next.append(
				
			self.parse_grammar_rules(name, state, states_next, stack)
			
		def parse_parser_rules(self):
			
			self.reader.adv()
			
			while self.reader.more() and self.reader.char() != '#':	
				self.reader.skip_whitespace()
				
				name = self.reader.get_name()
				
				if name in self.nfa.nonterminals:
					self.err('compound already exists')
				else:
					self.nfa.nonterminals[name] = self.Node()

				self.reader.skip_whitespace()
				if self.reader.char() != '=':
					self.err('parse rules error no equal sign')
				
				self.reader.adv()
				self.parse_grammar_rules(name, self.nfa.state_start, [], [])
				self.reader.skip_whitespace()
				
	class Tokens:
		
		class Reader:
			def __init__(self, file):
				self.src = open(file).read()
				self.pos = 0
				self.delimeters = [' ', ':', '=', '+', '-', '\t', '\n', 'eof']
				
			def char(self):
				if self.pos >= len(self.src):
					return 'eof'
				return self.src[self.pos]
			
			def get_char(self):
				if self.pos >= len(self.src):
					return 'eof'
				self.pos += 1
				return self.src[self.pos-1]
				
			def adv(self):
				self.pos += 1
				
			def dec(self):
				self.pos -= 1
				
			def skip_space(self):
				while self.char() == ' ':
					self.adv()
				
		class Token:
			def __init__(self, src, str, start, end, type):
				self.src = src
				self.string = str
				self.start = start
				self.end = end
				self.type = type
				self.prev = None
				self.next = None
				
			def print(self):
				if self.src[self.start:self.end] == '\n':
					string = '\\n'
				else:
					string = self.src[self.start:self.end]
				print('(' + string + ',' + str(self.type) + ')')
		
		def __init__(self, rules, src):
			self.rules = rules
			self.reader = self.Reader(src)
			
		def get_next(self):
			start = self.reader.pos
			
			state = self.rules.dfa.state_start
			#state.print_transitions()

			ch = self.reader.get_char()

			state_last = None
			
			while state and ch != 'eof':
				
				state = self.rules.dfa.get_reachable_state(state, ch)
				
				if state:
					ch = self.reader.get_char()
					state_last = state
				
			
			if self.reader.pos == start:
				self.reader.adv()
			else:
				self.reader.dec()
			
			end = self.reader.pos
			
			self.reader.skip_space()
			
			if ch == 'eof':
				type = 'end'
			
			elif state_last:
				if state_last.accept:
					type = state_last.type
				else:
					type = '?'
			else:
				print('no state error')
				type = 'end'
				
			#print(str(start) + ":" + str(end) + ' ' + self.reader.src[start:end] + ' ' + str(type))

			return self.Token(self.reader.src, self.reader.src[start:end], start, end, type)
		
	class Parser:

		def __init__(self):
			0
			
	def __init__(self, src_rules, src_file):
		self.rules = self.Rules(src_rules)
		self.tokens = self.Tokens(self.rules, src_file)
		
		return
		
		tk = self.tokens.get_next()
		tk.print()
		while tk.type != 'end':
			tk = self.tokens.get_next()
			tk.print()

compiler = Compiler('rules', 'main.b')
