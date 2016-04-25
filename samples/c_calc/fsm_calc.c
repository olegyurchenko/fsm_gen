/*----------------------------------------------------------------------------*/
/**
* @pkg fsm_calc
*/
/**
* Demo for fsm_gen - calculator fsm.
*
* Long description of fsm_calc.<br>
* (C) T&T team, Kiev, Ukraine 2013.<br>
* started 21.08.2013 18:10:17<br>
* @pkgdoc fsm_calc
* @author oleg
* @version 0.01
*/
/*----------------------------------------------------------------------------*/
#include <stdio.h>
#define CALC_BODY
#define CALC_CALLBACKS
#include "fsm_calc.h"
/*----------------------------------------------------------------------------*/
void calculator_reset(CALC_DATA *data)
{
  data->arg1[0] = '\0';
  data->arg2[0] = '\0';
  data->arg_count = 0;
  data->arg_size = 0;
  data->oper = 0;
}
/*----------------------------------------------------------------------------*/
int calculator_do(CALC_DATA *data)
{
  int arg1, arg2;

  if(!data->arg_count || !data->arg_size)
  {
    fprintf(stderr, "Operand absent\n");
    return 1;
  }

  arg1 = atoi(data->arg1);
  arg2 = atoi(data->arg2);
  switch(data->oper)
  {
  case '-':
    arg1 = arg1 - arg2;
    break;
  case '+':
    arg1 = arg1 + arg2;
    break;
  case '*':
    arg1 = arg1 * arg2;
    break;
  case '/':
    if(!arg2)
    {
      fprintf(stderr, "Integer divide by 0\n");
      return 1;
    }
    arg1 = arg1 / arg2;
    break;
  default:
    fprintf(stderr, "Invalid operator '%c'\n", data->oper);
    return 1;
  }

  snprintf(data->arg1, ARG_SIZE, "%d", arg1);
  data->arg2[0] = '\0';
  data->arg_count = 0;
  data->arg_size = 0;
  return 0;
}
/*----------------------------------------------------------------------------*/
#define UNUSED_ARGS (void)state; (void)evt; (void)arg; (void)data
static int on_digit_enter(CALC_FSM_STATE *state, int evt, int arg, CALC_DATA *data)
{
  char *buffer;
  UNUSED_ARGS;
  //printf("on_digit_enter '%c'\n", arg);
  if(!data->arg_count)
    buffer = data->arg1;
  else
    buffer = data->arg2;

  buffer[data->arg_size] = arg;
  data->arg_size ++;
  if(data->arg_size >= ARG_SIZE)
  {
    fprintf(stderr, "Argument size riched\n");
    return 1;
  }
  buffer[data->arg_size] = '\0';

  return 0;
}
/*----------------------------------------------------------------------------*/
static int on_oper_enter(CALC_FSM_STATE *state, int evt, int arg, CALC_DATA *data)
{
  UNUSED_ARGS;
  //printf("on_oper_enter '%c'\n", arg);
  if(data->arg_count && calculator_do(data))
    return 1;
  data->arg_count ++;
  data->oper = arg;
  data->arg_size = 0;
  return 0;
}
/*----------------------------------------------------------------------------*/
static int on_signum_enter(CALC_FSM_STATE *state, int evt, int arg, CALC_DATA *data)
{
  char *buffer;
  UNUSED_ARGS;
  //printf("on_signum_enter '%c'\n", arg);
  if(!data->arg_count)
    buffer = data->arg1;
  else
    buffer = data->arg2;

  buffer[data->arg_size] = arg;
  data->arg_size ++;
  if(data->arg_size >= ARG_SIZE)
  {
    fprintf(stderr, "Argument size riched\n");
    return 1;
  }
  buffer[data->arg_size] = '\0';
  return 0;
}
/*----------------------------------------------------------------------------*/
static int on_equal_enter(CALC_FSM_STATE *state, int evt, int arg, CALC_DATA *data)
{
  UNUSED_ARGS;
  //printf("on_equal_enter '%c'\n", arg);
  if(calculator_do(data))
    return 1;
  printf("result=%s\n", data->arg1);
  calculator_reset(data);
  return 0;
}
/*----------------------------------------------------------------------------*/


