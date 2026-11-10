#include <errno.h>
#include <libproc.h>
#include <mach/mach_time.h>
#include "core.h"

int core_proc_cpu(int64_t pid, struct core_cpu *out) {
    struct proc_taskinfo ti;
    mach_timebase_info_data_t tb;

    if (out == NULL || pid < 0)
        return EINVAL;
    int n = proc_pidinfo((int)pid, PROC_PIDTASKINFO, 0, &ti, sizeof ti);
    if (n <= 0)
        return errno != 0 ? errno : ESRCH;
    if (n < (int)sizeof ti)
        return ESRCH;
    mach_timebase_info(&tb);
    out->user_us = (int64_t)(ti.pti_total_user * tb.numer / tb.denom / 1000);
    out->kernel_us = (int64_t)(ti.pti_total_system * tb.numer / tb.denom / 1000);
    return 0;
}
