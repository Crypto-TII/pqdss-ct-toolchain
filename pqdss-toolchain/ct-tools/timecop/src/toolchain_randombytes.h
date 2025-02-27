#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <fcntl.h>


#ifndef TOOLCHAIN_CT_RANDOMBYTES_H
#define TOOLCHAIN_CT_RANDOMBYTES_H


// This a copy of the function randombytes() from dudect.h

/* this comes from ebacs */
void ct_randombytes(uint8_t *x, size_t how_much) {
    ssize_t i;
    static int fd = -1;

    ssize_t xlen = (ssize_t)how_much;
    assert(xlen >= 0);
    if (fd == -1) {
        for (;;) {
            fd = open("/dev/urandom", O_RDONLY);
            if (fd != -1)
                break;
            sleep(1);
        }
    }

    while (xlen > 0) {
        if (xlen < 1048576)
            i = xlen;
        else
            i = 1048576;

        i = read(fd, x, (size_t)i);
        if (i < 1) {
            sleep(1);
            continue;
        }

        x += i;
        xlen -= i;
    }
}

#endif //TOOLCHAIN_CT_RANDOMBYTES_H
