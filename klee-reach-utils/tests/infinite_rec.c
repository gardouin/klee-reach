#include "klee/klee.h"
#define X 12

void bar();
void foo();

void foo(int x) {
	x--;
	bar(x);
}

void bar(int x) {
	x -= 2;
	foo(x);
}

int main() {
	foo(X);
	klee_reach();
	return 0;
}
