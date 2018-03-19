##
#   File:   Makefile
#   Author: James Petersen <jpetersenames@gmail.com>
#
#   Usage:
#       make
#       make clean
##

CC      = gcc
CFLAGS  = -shared


all: #tmp007/* vl6180/*
	make vl6180
	make tmp007

vl6180: vl6180/vl6180.c vl6180/vl6180.h
	$(CC) -shared -Wl,-soname,vl6180 -o vl6180/vl6180.so -fPIC vl6180/vl6180.c

tmp007: tmp007/tmp007.c tmp007/tmp007.h
	$(CC) -shared -Wl,-soname,tmp007 -o tmp007/tmp007.so -fPIC tmp007/tmp007.c

clean:
	@echo
	@echo "I'm good, clean yourself."
	@echo
