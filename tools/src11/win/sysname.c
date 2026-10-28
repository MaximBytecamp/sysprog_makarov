#include <windows.h>
#include <stdio.h>

int main(void) {
    SYSTEM_INFO si;

    GetNativeSystemInfo(&si);
    printf("processors   %lu\n", si.dwNumberOfProcessors);
    printf("page size    %lu\n", si.dwPageSize);
    printf("architecture %u\n", si.wProcessorArchitecture);
    printf("sizeof       %zu\n", sizeof si);
    return 0;
}
