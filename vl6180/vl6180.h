/*
 *  File:   vl6180.h
 *  Author: James Petersen <jpetersenames@gmail.com>
 */

#ifndef VL6180_H
#define VL6180_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define VL6180_DEV "/dev/i2c-1"
#define VL6180_ID  0x29

#define SUCCESS 0
#define ERROR  -1
#define EXIT    1

/*
 *  UNUSED
 */
typedef struct i2c_dev
{
    int      fd;
    int      addr;
    char    *dev;
    uint8_t (*read)();
}i2c_dev_t;

int vl6180_setup();
int vl6180_read_range(int fd);

#endif
