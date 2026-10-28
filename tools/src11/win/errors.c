#include <windows.h>
#include <stdio.h>

static void try_open(const WCHAR *path) {
    HANDLE h = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ, NULL,
                           OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        DWORD code = GetLastError();
        printf("%-40ls error %lu\n", path, code);
        return;
    }
    printf("%-40ls handle %p\n", path, (void *)h);
    CloseHandle(h);
}

int main(void) {
    try_open(L"C:\\Windows\\win.ini");
    try_open(L"C:\\Windows\\no-such-file.ini");
    try_open(L"C:\\Windows\\System32\\config\\SAM");
    return 0;
}
