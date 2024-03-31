#include "klee/klee.h"

int main() {
	int x;
	if (x >= 0) {
		if (x < 0) {
			klee_reach();
		}
	}
	return 0;
}
