SRC = ptask uss taskPoll

all: $(SRC)

$(SRC):
	cython $@.pyx
	gcc -shared -fPIC -o $@.so $@.c -I/usr/include/python3.4

