/*----------------------------------------------------------------------------*/
/**
* @pkg calc
*/
/**
* Demo for fsm_gen - calculator fsm.
*
* Long description of calc.<br>
* (C) T&T team, Kiev, Ukraine 2013.<br>
* started 21.08.2013 18:10:17<br>
* @pkgdoc calc
* @author oleg
* @version 0.01 
*/
/*----------------------------------------------------------------------------*/
#ifndef CALC_H_1377097817
#define CALC_H_1377097817
/*----------------------------------------------------------------------------*/
#define ARG_SIZE 20
typedef struct
{
  char arg1[ARG_SIZE];
  char arg2[ARG_SIZE];
  int oper;
  int arg_count;
  int arg_size;
} CALC_DATA;

#ifdef __cplusplus
extern "C" {
#endif /*__cplusplus*/

void calculator_reset(CALC_DATA *data);

#ifdef __cplusplus
} //extern "C"
#endif /*__cplusplus*/
/*----------------------------------------------------------------------------*/
#endif /*CALC_H_1377097817*/

