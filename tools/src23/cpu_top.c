#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include "core.h"

#ifdef _WIN32
#include <windows.h>
#define PYTHON "python"
static void pause_ms(int ms) { Sleep(ms); }
#else
#include <time.h>
#define PYTHON "python3"
static void pause_ms(int ms) {
    struct timespec t = {ms / 1000, (ms % 1000) * 1000000L};
    nanosleep(&t, NULL);
}
#endif

static int64_t used(int64_t pid) {
    struct core_cpu cpu;
    int err = core_proc_cpu(pid, &cpu);
    if (err != 0) {
        printf("core_proc_cpu: error %d\n", err);
        exit(1);
    }
    printf("pid %" PRId64 ": user %" PRId64 " us, kernel %" PRId64 " us\n", pid, cpu.user_us, cpu.kernel_us);
    return cpu.user_us + cpu.kernel_us;
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        used(atoll(argv[1]));
        return 0;
    }
    char *args[] = {PYTHON, "-c", "import time\nend = time.time() + 2\nwhile time.time() < end: pass", NULL};
    struct core_child child;
    int32_t code;
    int err = core_spawn(args, &child);
    if (err != 0) {
        printf("core_spawn: error %d\n", err);
        return 1;
    }
    pause_ms(300);
    int64_t a = used(child.pid);
    pause_ms(1000);
    int64_t b = used(child.pid);
    core_wait(&child, 5000, &code);
    printf("load: %" PRId64 " us in 1 s = %" PRId64 "%%\n", b - a, (b - a) / 10000);
    return 0;
}
