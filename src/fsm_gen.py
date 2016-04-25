"""
Python fsm generate source
This module ysed ply lexer
"""
#map={'one':1, 'two':2}
#'one={one}, two={two}'.format(**map)
from __future__ import print_function
import sys
from fsm_file import fsm_file_parser
from ordered_dict import OrderedDict
#-----------------------------------------------------------------------
out_txt = ''
declarations = {
'callback_args' : "(int evt, void *arg, void *data)",
'func_name' :  "fsm_handle",
'init_name' : "fsm_init",
'event_error' : "do {} while(0)",
'prefix_name' :  "_",
'error_callback' : "fsm_error_callback",
"event_prefix" : "",
"state_prefix" : "",
"callback_prefix" : "  static int ",
"class_name" : "fsm",
}
#-----------------------------------------------------------------------
table = {}
includes = []
events = {}
states = {}
callbacks = {}
masked_entry = []
out_file = sys.stdout
#-----------------------------------------------------------------------
def prefix(name, upper = True):
  result = declarations.get(name, "")
  if len(result):
    result = result + '_'
  if upper:
    result = result.upper()
  return result
#-----------------------------------------------------------------------
class fsm_entry:
  src = ''
  dst = ''
  callback = 'NULL'
  evt = ''
  def __init__(self, statement):
    #print statement
    if len(statement) > 3:
      self.callback = statement[3]
    if len(statement) > 2:
      self.evt = prefix("event_prefix") + statement[2].upper()
    if len(statement) > 1:
      self.src = prefix("state_prefix") + statement[1].upper()
    if len(statement) > 0:
      self.dst = prefix("state_prefix") + statement[0].upper()
    #print self.dst, self.src, self.evt, self.callback
  def __repr__(self):
    return "entry:{{ {0} {1} {2} {3} }}".format(self.dst, self.src, self.evt, self.callback)
#-----------------------------------------------------------------------
def process_entry(entry):
  #print(entry)
  if entry.src != '*' and entry.evt != '*':
    entries = states.get(entry.src, {})
    entries[entry.evt] = entry
    states[entry.src] = entries
  else:
    masked_entry.append(entry)
    return

  if entry.dst != '*':
    entries = states.get(entry.dst, {})
    states[entry.dst] = entries
  else:
    raise Exception("Mask unsuported for destination state")


  if entry.evt != '*':
    events[entry.evt] = 1
  else:
    masked_entry.append(entry)


  if len(entry.callback):
    callbacks[entry.callback] = 1
#-----------------------------------------------------------------------
def process_file(f):
  parser = fsm_file_parser()
  parser.process_file(f)
  for statement in parser.statements.get("declaration", []):
    if len(statement) >= 2:
      if statement[0] == 'include':
        includes.append(statement[1])
      else:
        declarations[statement[0]] = statement[1]

  for statement in parser.statements.get("table", []):
    if len(statement) >= 2:
      process_entry(fsm_entry(statement))
#-----------------------------------------------------------------------
def call_args(src): #(int evt, void *arg, void *data) => (evt, arg, data)
  dst = "("
  for i in xrange(len(src)):
    if src[i] == ',' or src[i] == ')':
      j = i - 1
      while j >= 0:
        if src[j] == ' ' or src[j] == '(' or src[j] == '\t' or src[j] == '*':
          dst += src[j+1:i+1]
          break
        j -= 1;
  #print dst
  return dst
#-----------------------------------------------------------------------
def process_masked_entries():
  #print(masked_entry, file=sys.stderr)
  #print(states, file=sys.stderr)
  for entry in masked_entry:
    if entry.src == '*' and entry.evt == '*':
      raise Exception("Mask unsuported simultaneously for state and event")

    if entry.src == '*':
      for state in states.keys():
        entry.src = state
        if not states.get(entry.src, None):
          process_entry(entry)

    elif entry.evt == '*':
      for event in events.keys():
        entry.evt = event
        entries = states.get(entry.src, {})
        if not entries.get(entry.evt, None):
          process_entry(entry)

#-----------------------------------------------------------------------
def sorted_dicts(): #Sort dictionarys by names
  global states, events, callbacks
  states = OrderedDict(sorted(states.items(), key=lambda t: t[0]))
  events = OrderedDict(sorted(events.items(), key=lambda t: t[0]))
  callbacks = OrderedDict(sorted(callbacks.items(), key=lambda t: t[0]))

  for state in states.keys():
    states[state] = OrderedDict(sorted(states[state].items(), key=lambda t: t[0]))
#-----------------------------------------------------------------------
def output(src):
  print(src, file=out_file)
#-----------------------------------------------------------------------
def generate_c_header(): #generate C header
  #print includes
  #print declarations
  #print "events = ", events
  #print "states = ", states
  #print "callbacks = ", callbacks
  declarations["HEADER_MACRO"] = "{prefix_name}_FSM_HEADER".format(**declarations)
  declarations["callback_type"] = "{prefix_name}_fsm_callback".format(**declarations).lower()
  init_state = declarations.get("init_state", states.keys()[0]).upper()
  declarations["init_state"] = init_state
  declarations["call_args"] = call_args(declarations["callback_args"])



  output("""
/*
Generated by {generator}
from {src}
!!! DO NOT EDIT MANUALLY !!!
*/
#ifndef {HEADER_MACRO}
#define {HEADER_MACRO}
""".format(**declarations))

  for f in includes:
    output("#include {0}".format(f));

  output(
"""
typedef struct {prefix_name}_FSM_STATE {prefix_name}_FSM_STATE;
typedef int (*{callback_type}){callback_args};
typedef struct {{int next_state; {callback_type} callback;}} {prefix_name}_FSM_EVT_ENTRY;
typedef struct {{int start_evt; int size; const {prefix_name}_FSM_EVT_ENTRY *events;}} {prefix_name}_FSM_STATE_ENTRY;
struct {prefix_name}_FSM_STATE {{int current_state; const {prefix_name}_FSM_STATE_ENTRY *state_table;}};

int {func_name}{callback_args};
int {init_name}();
enum {prefix_name}_EVENTS {{""".format(**declarations))

  for evt in events.keys():
    output("{0},".format(evt))
  output("{prefix_name}_EVT_SIZE\n}};".format(**declarations))

  output("enum {prefix_name}_STATES {{".format(**declarations))
  for state in states.keys():
    output("{0},".format(state))
  output("{prefix_name}_STATES_SIZE\n}};".format(**declarations))

  output("#ifdef {prefix_name}_CALLBACKS".format(**declarations))
  for cb in callbacks.keys():
    if cb != 'NULL':
      output("{callback_prefix} {0} {callback_args};".format(cb, **declarations));

  output("#endif /*{prefix_name}_CALLBACKS*/".format(**declarations))

  output(
  "#ifdef {prefix_name}_BODY\n"
  "#ifndef {prefix_name}_INVALID_STATE\n"
  "#define {prefix_name}_INVALID_STATE -1\n"
  "#endif /*{prefix_name}_INVALID_STATE*/\n"
  "#ifndef {prefix_name}_ERROR_ANSWER\n"
  "#define {prefix_name}_ERROR_ANSWER -1\n"
  "#endif /*{prefix_name}_ERROR_ANSWER*/\n"
  "#ifndef {prefix_name}_OK_ANSWER\n"
  "#define {prefix_name}_OK_ANSWER 0\n"
  "#endif /*{prefix_name}_OK_ANSWER*/\n"
#  "{callback_prefix} {error_callback} {callback_args}\n"
#  "{{ {event_error}; return -1;}}\n\n"
  .format(**declarations))



  for state in states.keys():
    ss = states[state]
    if not len(ss):
      continue
    output("/*{0} events*/".format(state))
    output("static const {prefix_name}_FSM_EVT_ENTRY {0}_events[] = {{".format(state.lower(), **declarations))
    first = True
    event = None
    comma = ' '
    for evt in ss.keys():
      entry = ss[evt]
      if not first:
        evt_idx = events.keys().index(event) + 1
        while evt_idx >= 0 and evt_idx < len(events.keys()) and evt != events.keys()[evt_idx]:
          output(",{{ {prefix_name}_INVALID_STATE, NULL }} /*{0}*/".format(events.keys()[evt_idx], **declarations))
          evt_idx += 1

      output("{0}{{ {1}, {2} }} /*{3}*/".format(comma, entry.dst, entry.callback, evt))
      event = evt
      first = False
      comma = ','
    output("};\n\n")

  output(
  "/*State table*/\n"
  "static const {prefix_name}_FSM_STATE_ENTRY state_table[] = {{".format(**declarations))

  comma = ' '
  for state in states.keys():
    ss = states[state]
    output("/*{0} state*/".format(state))
    if not len(ss):
      output("{ 0,  0, NULL }")
      continue

    first_evt = ss.keys()[0]
    last_evt = ss.keys()[-1]
    output("{0}{{ {1},  {2} - {3} + 1, {4}_events }}".format(comma, first_evt, last_evt, first_evt, state.lower()))

    comma = ','

  output("};\n\n")

  output(
"""
int {init_name}({prefix_name}_FSM_STATE *dst)
{{
  dst->current_state = {init_state};
  dst->state_table = state_table;
  return 0;
}}
int {func_name} {callback_args}
{{
  const {prefix_name}_FSM_STATE_ENTRY *state_entry;
  int index;
  if(state->current_state < 0 || state->current_state >= {prefix_name}_STATES_SIZE)
  {{
#ifndef {prefix_name}_IGNORE_ERROR
    state->current_state = {init_state};
    {event_error};
#endif /*{prefix_name}_IGNORE_ERROR*/
    return {prefix_name}_ERROR_ANSWER;
  }}
  state_entry = &state->state_table[state->current_state];
  index = evt - state_entry->start_evt;
  if(index < 0
    || index >= state_entry->size
    || {prefix_name}_INVALID_STATE == state_entry->events[index].next_state)
  {{
#ifndef {prefix_name}_IGNORE_ERROR
    state->current_state = {init_state};
    {event_error};
#endif /*{prefix_name}_IGNORE_ERROR*/
    return {prefix_name}_ERROR_ANSWER;
  }}
  state->current_state = state_entry->events[index].next_state;
  if(state_entry->events[index].callback != NULL)
    return state_entry->events[index].callback{call_args};
  return {prefix_name}_OK_ANSWER;
}}
#endif /*{prefix_name}_BODY*/

""".format(**declarations))

  output("#endif /*{HEADER_MACRO}*/".format(**declarations))

#-----------------------------------------------------------------------
def generate_py_class(): #generate python class
  init_state = declarations.get("init_state", states.keys()[0]).upper()
  declarations["init_state"] = init_state

  output("""
#Generated by {generator}
#from {src}
#!!! DO NOT EDIT MANUALLY !!!

class {class_name}:
  INVALID_STATE = -1
  ERROR_ANSWER = -1
  OK_ANSWER = 0
  ignore_error = False
""".format(**declarations))
  i = 0
  output("  #Events")
  for evt in events.keys():
    output("  {0}={1}".format(evt, i))
    i += 1
  output("  EVENT_COUNT={0}".format(i))


  output("  events = {")
  for evt in events.keys():
    output("    {0} : '{0}',".format(evt))
  output("    }")

  i = 0
  output("  #States")
  for state in states.keys():
    output("  {0}={1}".format(state, i))
    i += 1
  output("  STATE_COUNT={0}".format(i))

  output("  states = {")
  for state in states.keys():
    output("    {0} : '{0}',".format(state))
  output("    }")

  output("  #callbacks")
  for cb in callbacks.keys():
    if cb != 'NULL':
      output("""
  def {0}(self, evt):
    print("{0}({{0}}({{1}})) Next state={{2}}({{3}})".format(self.events.get(evt, '????'), evt, self.states.get(self.current_state), self.current_state))
    return self.OK_ANSWER #Pure virtual
""".format(cb, **declarations))

  output("""
  def __init__(self):
""")

  for state in states.keys():
    ss = states[state]
    if not len(ss):
      continue
    output("    #{0} events".format(state))
    output("    {0}_events = (".format(state.lower(), **declarations))
    first = True
    event = None
    comma = ' '

    for evt in ss.keys():
      entry = ss[evt]
      if not first:
        evt_idx = events.keys().index(event) + 1
        while evt_idx >= 0 and evt_idx < len(events.keys()) and evt != events.keys()[evt_idx]:
          output("      ,( self.INVALID_STATE, None ) #{0}".format(events.keys()[evt_idx], **declarations))
          evt_idx += 1


      if entry.callback == 'NULL':
        cb = 'None'
      else:
        cb = 'self.' + entry.callback;

      output("      {0}( self.{1}, {2} ) #{3}".format(comma, entry.dst, cb, evt))
      event = evt
      first = False
      comma = ','
    output("    )\n\n")

  output(
  "    #State table\n"
  "    self.state_table = (".format(**declarations))

  comma = ' '
  for state in states.keys():
    ss = states[state]
    output("      #{0} state".format(state))
    if not len(ss):
      #print(ss, state, file=sys.stderr)
      print("State {0} has 0 events".format(state), file=sys.stderr)
      output("      {0}( 0,  0, None )".format(comma))
      continue

    first_evt = ss.keys()[0]
    output("      {0}( self.{1},  {2}_events )".format(comma, first_evt, state.lower()))

    comma = ','
  output("    )")
  output("    self.current_state = self.{init_state}".format(**declarations))


  output("""
  def error(self, evt):
    print("Invalid event={{0}}({{1}}) for state={{2}}({{3}})".format(self.events.get(evt, '????'), evt, self.states.get(self.current_state), self.current_state))

  def handle(self, evt):
    if self.current_state < 0 or self.current_state >= self.STATE_COUNT:
      if not self.ignore_error:
        self.error(evt)
        self.current_state = self.{init_state};
      return self.ERROR_ANSWER;

    state_entry = self.state_table[self.current_state]
    index = evt - state_entry[0]
    if(index < 0
      or index >= len(state_entry[1])
      or self.INVALID_STATE == state_entry[1][index][0]):
      if not self.ignore_error:
        self.error(evt)
        self.current_state = self.{init_state};
      return self.ERROR_ANSWER;

    self.current_state = state_entry[1][index][0];
    if state_entry[1][index][1]:
      return state_entry[1][index][1](evt);
    return self.OK_ANSWER;
# ********* class {class_name}
if __name__ == "__main__":
  obj = {class_name}()
""".format(**declarations))
  for evt in events.keys():
    output("  obj.handle(obj.{0})".format(evt))

#-----------------------------------------------------------------------
def help(argv0, file=sys.stdout):
  print("""
Usage: python {0} [options] <fsm_file1> ...
where options:
  --help or -h                                  This help
  --c-header or -c                              (default) Generate C header
  --py-class or -p                              Generate python base class
  --output filename or -o filename              Set output to filename
""".format(argv0), file=file)
#-----------------------------------------------------------------------
if __name__ == "__main__":
  generate = generate_c_header
  files = 0
  ignore = False
  declarations["generator"] = sys.argv[0]
  for arg in range(1, len(sys.argv)):
    if ignore:
      ignore = False
      continue
    f = sys.argv[arg]
    if f == '-h' or f == '--help':
      help(sys.argv[0])
      sys.exit(0);

    if f == '-c' or f == '--c-header':
      generate = generate_c_header
      continue

    if f == '-p' or f == '--py-class':
      generate = generate_py_class
      continue

    if f == '-o' or f == '--output':
      arg += 1
      out_file = open(sys.argv[arg], "w")
      ignore = True
      continue

    declarations["src"] = ("" if not declarations.get("src", None) else declarations["src"] + ",") + f
    process_file(f)
    files += 1
  if not files:
    print("No output files", file=sys.stderr)
    help(sys.argv[0], sys.stderr)
    sys.exit(2);

  process_masked_entries()
  sorted_dicts()
  generate()
