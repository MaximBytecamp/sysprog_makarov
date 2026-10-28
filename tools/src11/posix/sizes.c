#include <stdio.h>
#include <stdint.h>
#include <sys/types.h>

int main(void) {
    printf("char     %zu\n", sizeof(char));
    printf("int      %zu\n", sizeof(int));
    printf("long     %zu\n", sizeof(long));
    printf("void *   %zu\n", sizeof(void *));
    printf("int64_t  %zu\n", sizeof(int64_t));
    printf("pid_t    %zu\n", sizeof(pid_t));
    return 0;
}
