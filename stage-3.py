
import sys

def print_dic(dic):
  sys.stdout.write('{')
  keys = sorted(dic)
  for key in keys:
    sys.stdout.write("'" + str(key) + "'" + ':' + str(dic[key]) + ', ')
  sys.stdout.write('} ')

class Lex:
  
  class DFA:
    def __init__(self):
      self.table = [[{}, {}]]
      self.optional = {}
      self.accept = []
    
    def new_row(self):
      self.table.append([{}, {}])
      
    def get_row(self, row):
      return self.table[row]
      
    def update(self, row, ex, num):
      self.table[row][0][ex] = num
      
    def update_ref(self, row, ex, num):
      self.table[row][1][ex] = num
      
    def get_productions(self, row):
      return self.table[row][1]
      
    def get_terminals(self, row):
      return self.table[row][0]
      
    def insert_optional(self, start, end):
      self.optional[start] = end
      
    def len(self):
      return len(self.table)
      
    def value(self, row, ex):
      return self.table[row][0][ex]
      
    def value2(self, row, ex):
      return self.table[row][1][ex]
      
    def insert_accept(self, num):
      self.accept.append(num)
      
    def print(self):
      for x, row in enumerate(self.table):
        sys.stdout.write('  ' + str(x) + ' ')
        print_dic(row[0])
        print_dic(row[1])
        print('')
      sys.stdout.write('  optional: ')
      print_dic(self.optional)
      sys.stdout.write('\n  accept: ')
      print(self.accept)
      print('')
  
  def __init__(self):
    self.rules = {}
  
  def insert_rule(self, expr, name):
    dfa = self.DFA()

    row_stack = [0]
    paren_stack = [[]]
    paren_final = []
    repetition_stack = []
    repetition_stack_n = []
    optional_stack = []
    
    do_or = False
    current = 0
    
    for ex in expr:
      
      if ex.isalpha() or ex in [':'] or ex[0] == '@':
        
        if not do_or: 
          dfa.new_row()
        do_or = False
        
        if len(repetition_stack):
          if current == repetition_stack_n[-1]:
            repetition_stack[-1].append((current, ex))
            
        upfunc = dfa.update_ref if ex[0] == '@' else dfa.update
        upfunc(current, ex, dfa.len()-1); current = dfa.len()-1
        
      elif ex in ['(', '{', '[']:
        row_stack.append(current); 
        paren_stack.append([])
        
        if ex == '{':
          repetition_stack.append([]); 
          repetition_stack_n.append(current)
          
        elif ex == '[':
          optional_stack.append(current)
          
      elif ex in  [')', '}', ']']:
        row_stack.pop(); 
        row = dfa.get_row(current - 1)
        
        for x in row[0]:
          if (current, x) not in paren_stack[-1]:
            paren_stack[-1].append((row[0][x], x))
        for x in row[1]:
          if (current, x) not in paren_stack[-1]:
            paren_stack[-1].append((row[1][x], x))
            
        for tup in paren_stack.pop():
          upfunc = dfa.update_ref if tup[1][0] == '@' else dfa.update
          upfunc(tup[0]-1, tup[1], current)
              
        if ex == '}':
          paren_final.append((repetition_stack.pop(), current))
        
        elif ex == ']':
          dfa.insert_optional(optional_stack.pop(), current)
      
      elif ex == '|':
        do_or = True
        row = dfa.get_row(current - 1)
        for x in row[0]:
          paren_stack[-1].append((row[0][x], x))
        current = row_stack[-1]
        
    # do final or update
    for tup in paren_stack.pop():
      upfunc(tup[0]-1, tup[1], current)
    
    # put repetitions back in
    for tup in paren_final:
      for x in tup[0]:
        if x[1][0] == '@':
          upfunc = dfa.update_ref; 
          valfunc = dfa.value2
        else:
          upfunc = dfa.update; 
          valfunc = dfa.value
        upfunc(tup[1], x[1], valfunc(x[0],x[1]))
        
    dfa.insert_accept(current)
    self.rules[name] = dfa
    return dfa
      
  def print_rules(self):
    rules = sorted(self.rules)
    for rule in rules:
      print(rule)
      self.rules[rule].print()
      print('')
  
  def doparse(self, rule, string):
    dfa = self.rules[rule]
    
    pos = 0
    row = 0
    stack = []
    opstack = []
    
    print('\n  --parse ' + rule + ' ' + string + '--')
    
    while pos < len(string):
      
      if row in dfa.accept:
        if pos < len(string)-1:
          return (False, pos)
        print('  --aceppt state--')
        return (True, pos)

      l = len(dfa.get_productions(row))
      if l:
        stack.append((row, pos, sorted(list(dfa.get_productions(row).keys()))))
      
      ch = string[pos]
      
      print('  ' + ch + ' ' + str(dfa.table[row]))
      
      if ch in dfa.get_terminals(row):
        row = dfa.get_terminals(row)[ch];
        pos += 1
        
        if row in dfa.optional:
          print('  --optional--')
          opstack.append((dfa.optional[row], pos))
          
      elif row in dfa.optional:
        print('  --optional--')
        row = dfa.optional[row]
        
      else:
        if len(stack):
          stac = stack[-1]
          
          found = False
          while len(stac[2]):
            pos = stac[1]
            prod = stac[2].pop(0)[1:]

            tup = self.doparse(prod, string[stac[1]:])
            
            if tup[0]:
              pos += tup[1]
              row = dfa.get_productions(stac[0])['@'+prod]
              found = True
              
              break;
          print('')
          if not found:
            if len(opstack):
              print('  --optional rewind--')
              row, pos = opstack.pop(0)
            else:
              return (False, pos)
          
        else:
          return (False, pos)

    if pos < len(string)-1:
      print('  --fail leftover input--')
      return (False, pos)
    
    print('  --aceppt state--')
    if row in dfa.accept:
      return (True, pos)

  def parse(self, rule, string):
    if (self.doparse(rule, string)[0]):
      print('\n--PARSE SUCCESSFUL --')
    else:
      print('\n--PARSE FAIL --')
      
  
class Reader:
  def __init__(self, file, lex):
    self.src = open(file).read()
    self.lex = lex
    self.expr = []
    self.reset()
    self.run()
    
  def err(self, string):
    print('reader error: ' + string)
    exit(0)
    
  def reset(self):
    self.read_mode = 'read_name'
    self.regex_mode = 'read_id'
    self.insert_mode = 'none'
    
    self.name = ''
    self.name_r = ''
    
    self.expr[:] = []
    
  def run(self):
    for ch in self.src:
      if ch in [' ']:  
        if self.read_mode == 'read_name':
          self.read_mode = 'read_equals'
          self.do_name = True
      
      if ch == '#':
        break;
        
      elif ch == ';':
        self.lex.insert_rule(self.expr, self.name)
        self.reset()
      
      elif self.read_mode == 'read_name' and ch not in  ['\n', '\t', ' ']:
        if not ch.isalpha() and ch not in ['.', '_']: self.err('not a name')
        self.name += ch

      elif self.read_mode == 'read_equals' and ch not in ['\n', '\t', ' ']:
        if ch != '=': self.err('expecting =')
        self.read_mode = 'read_regex'
      
      elif self.read_mode == 'read_regex':
        if ch == '"':
          self.regex_mode = 'read_literal' if self.regex_mode == 'read_id' else 'read_id'
          literal = ''

        elif ch in [' ', '\n', '\t']:    
          if self.regex_mode == 'read_id' and len(self.name_r):
            self.expr.append('@' + self.name_r)
            self.name_r = ''
            
          elif self.regex_mode == 'read_literal':
            self.expr.append(ch)
            
        elif ch.isalnum() or ch in ['.','+','-',':']:
          if self.regex_mode == 'read_literal':
            self.expr.append(ch)
          elif self.regex_mode == 'read_id':
            self.name_r += ch
        
        elif ch in ['(', ')', '|', '{', '}', '[', ']']:
          if self.regex_mode == 'read_id' and len(self.name_r):
            self.expr.append('@' + self.name_r)
            self.name_r = ''
          
          self.expr.append(ch)
          literal = ''

lex = Lex()
reader = Reader('stage-3.rules', lex)
lex.print_rules()

string = 'abarz'
print('--PARSE \'' + string + '\'')
lex.parse('func_def', 'abarz')


