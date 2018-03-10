/*
 *  File:   tmp007.c
 *  Author: James Petersen <jpetersenames@gmail.com>
 */

#include "./tmp007.h"

/*
 *  2 byte data union
 */
union data16
{
    uint16_t value;
    uint8_t  byte[2];
};


/*
 *  static function prototypes
 */
static inline int configure_reg(int fd);
static uint16_t read_data(int fd, uint8_t reg);
#define write_data(fd, reg, data) __write_data__(fd, reg, data, sizeof(data)/sizeof(uint8_t))
static ssize_t __write_data__(int fd, uint8_t reg, uint8_t *data, size_t size);
static float convert_temp_f(union data16 data);


/*
 *  setup()
 *
 *  RETURNS: file descriptor if setup is good, ERROR on error
 */
int tmp007_setup()
{
    int fd;
    int addr   = TMP007_ID;
    char* dev  = TMP007_DEV;

    /*
     *   open up the device
     */
    if ((fd = open(dev, O_RDWR)) < 0)
    {
        printf("Opening TMP007\n");
        return ERROR;
    }
    else
        printf("TMP007 Opened Successfully\n");

    /*
     *   initialize the device as a slave
     */
    if (ioctl(fd, I2C_SLAVE, addr) < 0)
    {
        printf("Initializing Communication with TMP007\n");
        return ERROR;
    }
    else
        printf("TMP007 Communication Initialized\n");

    /*
     *  send the configuration to the configure register
     */
    if (configure_reg(fd) < 0)
    {
        printf("Error: Configuring TMP007\n");
        return ERROR;
    }
    else
        printf("TMP007 Configured\n");

    return fd;
}


/*  configure_reg()
 *  RETURNS: number of bytes written */
static inline int configure_reg(int fd)
{
    uint8_t config[2];
    config[0] = 0x15;
    config[1] = 0x40;
    return write_data(fd, CONFIGURATION_REGISTER, config);
}


/*  read_data()
 *  RETURNS: 2 bytes of read data, ERROR otherwise */
static uint16_t read_data(int fd, uint8_t reg)
{
    if (write(fd, &reg, 1) != 1)
        return ERROR;

    uint16_t data;
    if (read(fd, &data, sizeof(data)) != sizeof(data))
    {
        printf("error on read %d\n", __LINE__);
        printf("Register not written, value returned\n");
        return ERROR;
    }
    return data;
}

/*  __write_data__()
 *  This is the main function for the write_data() macro
 *  RETURNS: number of bytes written, ERROR otherwise */
static ssize_t __write_data__(int fd, uint8_t reg, uint8_t *data, size_t size)
{
    if (size > 2)
    {
        printf("Error write_data: cannot write more than 2 bytes, registers are 16 bit\n");
        return ERROR;
    }
    int len = size+1;
    uint8_t w[len];
    w[0] = reg;
    w[1] = data[0];
    if (len == 3)
        w[2] = data[1];

    return write(fd, w, len);
}

/*  convert_temp_f()
 *  RETURNS: converted temperature data in fahrenheit */
static float convert_temp_f(union data16 data)
{
    /*
     *  flip the Intel little-endianess
     */
    uint16_t hb = data.byte[0] << 8;
    uint8_t  lb = data.byte[1] & 0xFC;
    int tmp     = (hb + lb) >> 2;

    float celsius = tmp * 0.03125;
    printf("[C] cels: %0.2f\n", celsius);
    return celsius * 1.8 + 32;
}


/*
 *  tmp007_read_temp()
 *
 *  RETURNS:
 *  TODO: add error checks
 */
float tmp007_read_temp(int fd)
{
    union data16 data;
    if ((data.value = read_data(fd, OBJECT_TEMP_REGISTER)) == ERROR)
    {
        printf("Error getting temp [%s][%s:%d]\n", __FILE__, __func__, __LINE__);
        return ERROR;
    }
    float temp =  convert_temp_f(data);
    printf("[C] Temp: %0.2f\n", temp);
    return temp;
}
