#
# Makefile for linux.
#
CC = gcc
CXX = c++

DEBUG = -g -O3 -Wall #-pedantic#-O3
CXXFLAGS = $(DEBUG)
CFLAGS = $(DEBUG) -I. 
CPPFLAGS = -I.
LDLIBS = 

exeext = 
dllext = .so
DEPFILE = dep.xxx


all:  calc$(exeext)

CALC_SRC = main.c fsm_calc.c

fsm_calc.o:fsm_calc.h
fsm_calc.h: calc.txt
	./mk_fsm.sh

CALC_OBJS := $(CALC_SRC:.c=.o)

calc$(exeext): $(CALC_OBJS)
	$(CC) -o $@ $(CXXFLAGS) $(LDFLAGS) $(LDLIBS) $(CALC_OBJS)
.c.o:
	$(CC) -c $(CPPFLAGS) $(CXXFLAGS) $(CFLAGS) -o $@ $<
.cpp.o:
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $(CFLAGS) -o $@ $<


clean:
	-rm -f $(CALC_OBJS)

