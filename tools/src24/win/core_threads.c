#include <windows.h>
#include <tlhelp32.h>
#include "core.h"

int core_proc_threads(int64_t pid, int32_t *count) {
    PROCESSENTRY32W pe;

    if (count == NULL || pid < 0)
        return ERROR_INVALID_PARAMETER;
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE)
        return (int)GetLastError();
    pe.dwSize = sizeof pe;
    BOOL ok = Process32FirstW(snap, &pe);
    while (ok && pe.th32ProcessID != (DWORD)pid)
        ok = Process32NextW(snap, &pe);
    CloseHandle(snap);
    if (!ok)
        return ERROR_INVALID_PARAMETER;
    *count = (int32_t)pe.cntThreads;
    return 0;
}
