#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "core.h"

int core_proc_cpu(int64_t pid, struct core_cpu *out) {
    char path[64], line[512];
    unsigned long long utime, stime;

    if (out == NULL || pid < 0)
        return EINVAL;
    snprintf(path, sizeof path, "/proc/%lld/stat", (long long)pid);
    FILE *f = fopen(path, "r");
    if (f == NULL)
        return errno;
    size_t len = fread(line, 1, sizeof line - 1, f);
    fclose(f);
    line[len] = '\0';

    char *close = strrchr(line, ')');
    if (close == NULL)
        return EINVAL;
    if (sscanf(close + 2, "%*c %*d %*d %*d %*d %*d %*u %*u %*u %*u %*u %llu %llu", &utime, &stime) != 2)
        return EINVAL;
    long hz = sysconf(_SC_CLK_TCK);
    out->user_us = (int64_t)(utime * 1000000ULL / hz);
    out->kernel_us = (int64_t)(stime * 1000000ULL / hz);
    return 0;
}
