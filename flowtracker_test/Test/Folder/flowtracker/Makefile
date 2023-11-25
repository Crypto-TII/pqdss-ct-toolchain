CC = clang


CAND1 = ../../../utils/utils.c
CAND1_INCS = ../../../utils/utils.h

CAND2 = ../../../utils/funct1.c
CAND2_INCS =../../../utils/funct1.h


SRC = ../../../utils/utils.c
SRC_INCS = ../../../utils/utils.h


all: common_file.bc common_file.rbc taint.bc taint.rbc



common_file.bc: $(SRC) $(SRC_INCS)
	$(CC) -emit-llvm  -c -g $(SRC) -o common_file.bc

common_file.rbc: common_file.bc
	opt -instnamer -mem2reg common_file.bc > common_file.rbc


taint.bc: $(CAND2)
	$(CC) -emit-llvm  -c -g $(SRC) -o taint.bc

taint.rbc: taint.bc
	opt -instnamer -mem2reg taint.bc > taint.rbc


clean:
	rm *.bc *.rbc  #common_file.bc common_file.rbc taint.bc taint.rbc
	rm *.txt *.out *.dot *.png *.ps *.svg


