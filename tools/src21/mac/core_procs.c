#include <errno.h>
#include <libproc.h>
#include <stdio.h>
#include "core.h"

int core_list_procs(struct core_proc *out, int32_t max, int32_t *count) {
    static pid_t pids[8192];
    struct proc_bsdshortinfo si;
    int32_t found = 0;

    if (count == NULL || max < 0 || (out == NULL && max > 0))
        return EINVAL;
    int n = proc_listallpids(pids, sizeof pids);
    if (n < 0)
        return errno;

    for (int i = 0; i < n; i++) {
        if (proc_pidinfo(pids[i], PROC_PIDT_SHORTBSDINFO, 0, &si, sizeof si) != sizeof si)
            continue;
        if (found < max) {
            out[found].pid = pids[i];
            out[found].ppid = si.pbsi_ppid;
            snprintf(out[found].name, sizeof out[found].name, "%s", si.pbsi_comm);
        }
        found++;
    }
    *count = found;
    return found > max ? ERANGE : 0;
}
