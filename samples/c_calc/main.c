#include <stdio.h>
#include "fsm_calc.h"
/*----------------------------------------------------------------------------*/
CALC_FSM_STATE calc_state;
CALC_DATA calc_data;

int main(int argc, char **argv)
{
  FILE *f;
  int line = 1, col = 0;
  int ret;

  f = stdin;
  if(argc > 1)
  {
    f = fopen(argv[1], "rb");
    if(f == NULL)
    {
      fprintf(stderr, "Error open file '%s'\n", argv[1]);
      return 1;
    }
  }


  calc_fsm_init(&calc_state);
  calculator_reset(&calc_data);

  while(!feof(f))
  {
    int c;
    int evt;
    c = fgetc(f);
    if(c == '\n')
    {
      line ++;
      col = 0;
    }
    else
      col ++;
    switch(c)
    {
    case ' ': case '\r': case '\t': case '\n':
      evt = EVENT_BLANK;
      break;
    case '0': case '1': case '2': case '3': case '4':
    case '5': case '6': case '7': case '8': case '9':
      evt = EVENT_DIGIT;
      break;
    case '-':
      evt = EVENT_MINUS;
      break;
    case '+':
      evt = EVENT_PLUS;
      break;
    case '*':
      evt = EVENT_MUL;
      break;
    case '/':
      evt = EVENT_DIV;
      break;
    case '=':
      evt = EVENT_EQUAL;
      break;
    default:
      fprintf(stderr, "%s:%d:%d: Error: invalid char '%c' code:%02x\n",
              f == stdin ? "stdin" : argv[1],
              line,
              col,
              c,
              c
              );
      return 2;
    }
    if((ret = calc_handle_event(&calc_state, evt, c, &calc_data)))
       return ret;
  }
  return 0;
}
/*----------------------------------------------------------------------------*/

