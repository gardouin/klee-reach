
#include "klee/klee.h"

void foo() {
	klee_reach();
}

int main() {
	foo();
	return 0;
}
