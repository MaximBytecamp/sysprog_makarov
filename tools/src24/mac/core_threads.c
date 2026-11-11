#include <errno.h>
#include <libproc.h>
#include "core.h"

int core_proc_threads(int64_t pid, int32_t *count) {
    struct proc_taskinfo ti;

    if (count == NULL || pid < 0)
        return EINVAL;
    int n = proc_pidinfo((int)pid, PROC_PIDTASKINFO, 0, &ti, sizeof ti);
    if (n <= 0)
        return errno != 0 ? errno : ESRCH;
    if (n < (int)sizeof ti)
        return ESRCH;
    *count = ti.pti_threadnum;
    return 0;
}
