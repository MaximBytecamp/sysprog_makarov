#include <stdio.h>
#include "core.h"
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

#define N 20

static void report(const char *when) {
#ifdef _WIN32
    DWORD handles = 0;
    GetProcessHandleCount(GetCurrentProcess(), &handles);
    printf("%s: handles %lu\n", when, (unsigned long)handles);
#else
    int ppid, zombies = 0;
    char stat[8];
    FILE *ps = popen("ps -A -o ppid=,stat=", "r");
    while (ps != NULL && fscanf(ps, "%d %7s", &ppid, stat) == 2)
        if (ppid == (int)getpid() && stat[0] == 'Z')
            zombies++;
    if (ps != NULL)
        pclose(ps);
    printf("%s: zombies %d\n", when, zombies);
#endif
}

int main(void) {
#ifdef _WIN32
    char *args[] = {"cmd", "/c", "exit", NULL};
#else
    char *args[] = {"true", NULL};
#endif
    struct core_child child;

    report("before");
    for (int i = 0; i < N; i++)
        core_spawn(args, &child);
#ifdef _WIN32
    Sleep(1000);
#else
    sleep(1);
#endif
    report("after 20 core_spawn without core_wait");
    return 0;
}
