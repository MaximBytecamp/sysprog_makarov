#include <windows.h>
#include <stdio.h>
#include <string.h>

static void dump(const void *p, size_t n) {
    const unsigned char *b = p;
    for (size_t i = 0; i < n; i++)
        printf("%02x ", b[i]);
    printf("\n");
}

int main(void) {
    WCHAR name[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD len = MAX_COMPUTERNAME_LENGTH + 1;
    char utf8[64];
    WCHAR tiny[4];
    DWORD tiny_len = 4;

    GetComputerNameW(name, &len);
    printf("WCHAR: %lu characters\n", len);
    dump(name, (len + 1) * sizeof(WCHAR));

    WideCharToMultiByte(CP_UTF8, 0, name, -1, utf8, sizeof utf8, NULL, NULL);
    printf("UTF-8: \"%s\", length %zu\n", utf8, strlen(utf8));
    dump(utf8, strlen(utf8) + 1);

    if (!GetComputerNameW(tiny, &tiny_len))
        printf("tiny: error %lu, needed %lu\n", GetLastError(), tiny_len);
    return 0;
}
