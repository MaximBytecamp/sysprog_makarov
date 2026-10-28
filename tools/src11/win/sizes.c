#include <windows.h>
#include <stdio.h>
#include <stdint.h>

int main(void) {
    printf("char     %zu\n", sizeof(char));
    printf("int      %zu\n", sizeof(int));
    printf("long     %zu\n", sizeof(long));
    printf("void *   %zu\n", sizeof(void *));
    printf("int64_t  %zu\n", sizeof(int64_t));
    printf("DWORD    %zu\n", sizeof(DWORD));
    printf("WCHAR    %zu\n", sizeof(WCHAR));
    printf("HANDLE   %zu\n", sizeof(HANDLE));
    return 0;
}
