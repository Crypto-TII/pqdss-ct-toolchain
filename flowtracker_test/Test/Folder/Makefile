CFLAGS:= -Wall -g
SHAREDLIB_PATH = /usr/lib/

SRC = ../../utils/utils.c
INCS = ../../utils/utils.h

all: test_harness_cnt_comp taint_cnt_comp taint_cnt_comp.o dude_cnt_comp test_harness_rej_sample rej_sample_taint rej_sample_taint.o rej_sample_dude

dude_cnt_comp: dude_cnt_comp.c $(SRC) $(INCS)
	gcc dude_cnt_comp.c $(SRC)  $(CFLAGS)  -std=c11 -lm -I. $(INCS) -o dude_cnt_comp

test_harness_cnt_comp: test_harness_cnt_comp.c $(SRC) $(INCS)
	gcc test_harness_cnt_comp.c $(SRC) -g -static  $(CFLAGS) -I. $(INCS) -o test_harness_cnt_comp

taint_cnt_comp: taint_cnt_comp.c $(SRC) $(INCS)
	gcc taint_cnt_comp.c $(SRC) -L. $(SHAREDLIB_PATH)libctgrind.so  $(CFLAGS) -L. -lctgrind -I. $(INCS) -o taint_cnt_comp

taint_cnt_comp.o: taint_cnt_comp.c $(SRC) $(INCS)
	gcc taint_cnt_comp.c $(SRC) -L. $(SHAREDLIB_PATH)libctgrind.so  $(CFLAGS) -L. -lctgrind -I. $(INCS) -o taint_cnt_comp.o


rej_sample_dude: rej_sample_dude.c $(SRC) $(INCS)
	gcc rej_sample_dude.c $(SRC)  $(CFLAGS)  -std=c11 -lm -I. $(INCS) -o rej_sample_dude

test_harness_rej_sample: rej_sample_test_harness.c $(SRC) $(INCS)
	gcc rej_sample_test_harness.c $(SRC) -g -static  $(CFLAGS) -I. $(INCS) -o test_harness_rej_sample

rej_sample_taint: rej_sample_taint.c $(SRC) $(INCS)
	gcc rej_sample_taint.c $(SRC) -L. $(SHAREDLIB_PATH)libctgrind.so  $(CFLAGS) -L. -lctgrind -I. $(INCS) -o rej_sample_taint

rej_sample_taint.o: rej_sample_taint.c $(SRC) $(INCS)
	gcc rej_sample_taint.c $(SRC) -L. $(SHAREDLIB_PATH)libctgrind.so  $(CFLAGS) -L. -lctgrind -I. $(INCS) -o rej_sample_taint.o


clean:
	rm -rf dude_cnt_comp.o dude_cnt_comp test_harness_cnt_comp taint_cnt_comp test_harness_rej_sample rej_sample_taint rej_sample_taint.o
