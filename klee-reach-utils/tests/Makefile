all: test

clang:
	clang-13 -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone *.c

llvm: clang
	llvm-dis *.bc

test: llvm
	./run.sh

clean:
	rm -f *.bc *.ll *.dist
	rm -rf build
