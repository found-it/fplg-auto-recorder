#include <stdio.h>
#include "tmp007.h"


int main()
{
    printf("TMP007 Hello\n\n");
    
    int fd = tmp007_setup();
    float far;
    while (1)
    {
        far = tmp007_read_temp(fd);
        printf("Temp [F]: %0.2f\n", far);
    }

    return SUCCESS;
}
