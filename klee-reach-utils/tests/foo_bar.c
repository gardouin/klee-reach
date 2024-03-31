#include "klee/klee.h"

#define VALUE 144

int foo(int x) {
	int i = VALUE;
	while (i > x) {
		i--;
	}
	return i;
}

int bar(int x, int y) {
	int a = foo(x);
	int b = foo(y);
	if (a == b) {
		klee_reach();
		return 1; // target here
	}
	return 0;
}

void foobar() {
	bar(0,0);
}

int main() {
	int x;
	int y;
	klee_make_symbolic(&x, sizeof(x), "x");
	klee_make_symbolic(&y, sizeof(y), "y");
	bar(x, y);
	return 0;
}
