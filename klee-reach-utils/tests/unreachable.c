#include "klee/klee.h"

void foo() {
	klee_reach();
}

int main() {
	return 0;
}
