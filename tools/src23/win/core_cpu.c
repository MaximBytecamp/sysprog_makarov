#include <windows.h>
#include "core.h"

static int64_t to_us(FILETIME t) {
    ULARGE_INTEGER v;
    v.LowPart = t.dwLowDateTime;
    v.HighPart = t.dwHighDateTime;
    return (int64_t)(v.QuadPart / 10);
}

int core_proc_cpu(int64_t pid, struct core_cpu *out) {
    FILETIME created, exited, kernel, user;

    if (out == NULL || pid < 0)
        return ERROR_INVALID_PARAMETER;
    HANDLE h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, (DWORD)pid);
    if (h == NULL)
        return (int)GetLastError();
    if (!GetProcessTimes(h, &created, &exited, &kernel, &user)) {
        DWORD err = GetLastError();
        CloseHandle(h);
        return (int)err;
    }
    CloseHandle(h);
    out->user_us = to_us(user);
    out->kernel_us = to_us(kernel);
    return 0;
}
