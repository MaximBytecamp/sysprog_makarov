#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include "core.h"

static int read_stat(const char *pid, struct core_proc *p) {
    char path[64], line[512];
    snprintf(path, sizeof path, "/proc/%s/stat", pid);
    FILE *f = fopen(path, "r");
    if (f == NULL)
        return -1;
    size_t len = fread(line, 1, sizeof line - 1, f);
    fclose(f);
    line[len] = '\0';

    char *open = strchr(line, '(');
    char *close = strrchr(line, ')');
    if (open == NULL || close == NULL)
        return -1;
    long long pid_num = 0, ppid = 0;
    if (sscanf(line, "%lld", &pid_num) != 1 || sscanf(close + 2, "%*c %lld", &ppid) != 1)
        return -1;
    p->pid = pid_num;
    p->ppid = ppid;
    snprintf(p->name, sizeof p->name, "%.*s", (int)(close - open - 1), open + 1);
    return 0;
}

int core_list_procs(struct core_proc *out, int32_t max, int32_t *count) {
    struct core_proc p;
    struct dirent *e;
    int32_t found = 0;

    if (count == NULL || max < 0 || (out == NULL && max > 0))
        return EINVAL;
    DIR *d = opendir("/proc");
    if (d == NULL)
        return errno;

    while ((e = readdir(d)) != NULL) {
        if (!isdigit((unsigned char)e->d_name[0]))
            continue;
        if (read_stat(e->d_name, &p) != 0)
            continue;
        if (found < max)
            out[found] = p;
        found++;
    }
    closedir(d);
    *count = found;
    return found > max ? ERANGE : 0;
}
