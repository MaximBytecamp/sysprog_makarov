#include <stdint.h>
int64_t burn(int64_t n) { volatile int64_t x = 0; while (n--) x++; return x; }
