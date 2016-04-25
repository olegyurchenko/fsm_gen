"""
Python fsm files parser
"""
from __future__ import print_function
import ast
from fsm_lex import fsm_lex
import sys
#--------------------------------------------------------------
#token types
#--------------------------------------------------------------
STATEMENT = 1
SECTION = 2
class token:
  type = -1
  src = None
  def __init__(self, type = -1, src = None):
    self.type = type
    self.src = src

  def __str__(self):
    return "tok:{{type:{0}, src:{1}}}".format(self.type, self.src)
  def __repr__(self):
    return "tok:{{type:{0}, src:{1}}}".format(self.type, self.src)
#--------------------------------------------------------------
# lexer class
#--------------------------------------------------------------
class fsm_file_lexer(fsm_lex):

  IDENT_EXPR = 0
  STRING_EXPR = 1

  def __init__(self, filename):
    fsm_lex.__init__(self)
    self.filename = filename
    f = open(filename, "r")
    self.src = f.read()

    self.line = 0
    self.col = 0
    self.pos = 0
    self.tok = None
    self.expression = -1

    self.char_tbl = {}
    for c in range(ord('a'), ord('z')+1):
      self.char_tbl[chr(c)] = self.ALPHA
    for c in range(ord('A'), ord('Z')+1):
      self.char_tbl[chr(c)] = self.ALPHA
    for c in range(ord('0'), ord('9')+1):
      self.char_tbl[chr(c)] = self.DIGIT

    self.char_tbl['_'] = self.ALPHA
    self.char_tbl['*'] = self.ASTERISK

    self.char_tbl[' '] = self.BLANK
    self.char_tbl['\t'] = self.BLANK
    self.char_tbl['\r'] = self.BLANK
    self.char_tbl['\n'] = self.NEWLINE
    self.char_tbl['\''] = self.APOS
    self.char_tbl['['] = self.LBRACKET
    self.char_tbl['#'] = self.NUMBER
    self.char_tbl['\"'] = self.QUOT
    self.char_tbl[']'] = self.RBRACKET
    self.char_tbl['\\'] = self.SLASH
    self.char_tbl[']'] = self.RBRACKET
    #print(self.char_tbl)

    self.section = token(SECTION)
    self.statement = token(STATEMENT)

  def token(self):
    self.tok = None
    while self.pos < len(self.src) and not self.tok:
      evt = self.char_tbl.get(self.src[self.pos], self.SYMBOL)
      self.handle(evt)
      self.pos += 1
      if evt == self.NEWLINE:
        self.line += 1
        self.col = 0
    return self.tok

  def error(self, evt):
    print("Invalid event={0}({1}) for state={2}({3})".format(self.events.get(evt, '????'), evt, self.states.get(self.current_state), self.current_state), file=sys.stderr)
    raise Exception("{0}:{1}:{2} Invalid character '{3}' in input stream".format(self.filename, self.line, self.col, self.src[self.pos]))

  def on_begin_section(self, evt):
    self.start_pos = self.pos + 1
    return self.OK_ANSWER

  def on_end_section(self, evt):
    self.section.src = self.src[self.start_pos : self.pos]
    self.tok = self.section
    return self.OK_ANSWER


  def on_begin_statement(self, evt):
    self.statement.src = []
    self.on_begin_ident(evt)
    return self.OK_ANSWER

  def on_end_statement(self, evt):
    if self.expression == self.IDENT_EXPR:
      self.on_end_ident(evt)
    elif self.expression == self.STRING_EXPR:
      self.on_end_string(evt)
    self.tok = self.statement
    return self.OK_ANSWER


  def on_begin_string(self, evt):
    self.expression = self.STRING_EXPR
    self.start_pos = self.pos
    return self.OK_ANSWER

  def on_end_string(self, evt):
    #print('on_end_string', self.src[self.start_pos : self.pos], file=sys.stderr)
    self.statement.src.append(ast.literal_eval(self.src[self.start_pos : self.pos + 1]))
    self.expression = -1
    return self.OK_ANSWER


  def on_begin_ident(self, evt):
    self.expression = self.IDENT_EXPR
    self.start_pos = self.pos
    return self.OK_ANSWER

  def on_end_ident(self, evt):
    self.statement.src.append(self.src[self.start_pos : self.pos])
    #print("on_end_indent", `self.statement.src`)
    self.expression = -1
    return self.OK_ANSWER
#--------------------------------------------------------------
# parser class
#--------------------------------------------------------------
class fsm_file_parser:
  def __init__(self, default_encoding='utf8'):
    self.default_encoding = default_encoding
    self.filename = ''
    self.src = ''
    self.section = ''
    self.statements = {}

  def process_file(self, filename):
    self.filename = filename
    lex = fsm_file_lexer(filename)
    while True:
      tok = lex.token()
      if not tok:
        break
      #print(tok)
      if tok.type == STATEMENT:
        if not self.statements.get(self.section, None):
          self.statements[self.section] = []
        self.statements[self.section].append(tok.src)
      elif tok.type == SECTION:
        self.section = tok.src

if __name__ == "__main__":
  import sys
  parser = fsm_file_parser()
  for f in sys.argv[1:]:
    parser.process_file(f)
