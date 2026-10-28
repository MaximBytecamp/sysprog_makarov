#include <windows.h>
#include "core.h"

int core_get_info(struct core_info *out) {
    SYSTEM_INFO si;
    WCHAR name[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD len = MAX_COMPUTERNAME_LENGTH + 1;

    if (out == NULL)
        return ERROR_INVALID_PARAMETER;
    ZeroMemory(out, sizeof *out);

    out->pid = GetCurrentProcessId();
    GetNativeSystemInfo(&si);
    out->cpus = (int32_t)si.dwNumberOfProcessors;
    out->page_size = (int32_t)si.dwPageSize;

    if (!GetComputerNameW(name, &len))
        return (int)GetLastError();
    if (WideCharToMultiByte(CP_UTF8, 0, name, -1, out->host,
                            sizeof out->host, NULL, NULL) == 0)
        return (int)GetLastError();
    return 0;
}
