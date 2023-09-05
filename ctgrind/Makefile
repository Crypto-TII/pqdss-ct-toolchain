CFLAGS:= -Wall -ggdb -g -std=c99  -Wextra -lm
SHAREDLIB_PATH = /usr/lib/

all: testing.o


testing.o: test.c
	gcc test.c -L. $(SHAREDLIB_PATH)libctgrind.so  $(CFLAGS)  -L. -lctgrind -o testing.o




clean:
	rm -rf testing.o
