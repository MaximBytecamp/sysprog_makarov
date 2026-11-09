#include <errno.h>
#include <spawn.h>
#include <sys/wait.h>
#include <time.h>
#include "core.h"

extern char **environ;

int core_spawn(char *const argv[], struct core_child *out) {
    pid_t pid;

    if (argv == NULL || argv[0] == NULL || out == NULL)
        return EINVAL;
    int err = posix_spawnp(&pid, argv[0], NULL, NULL, argv, environ);
    if (err != 0)
        return err;
    out->pid = pid;
    out->handle = 0;
    return 0;
}

int core_wait(struct core_child *child, int32_t timeout_ms, int32_t *exit_code) {
    struct timespec step = {0, 10 * 1000 * 1000};
    int status;
    int32_t waited = 0;

    if (child == NULL || child->pid <= 0 || exit_code == NULL)
        return EINVAL;
    for (;;) {
        pid_t r = waitpid((pid_t)child->pid, &status, WNOHANG);
        if (r == -1)
            return errno;
        if (r != 0)
            break;
        if (timeout_ms >= 0 && waited >= timeout_ms)
            return ETIMEDOUT;
        nanosleep(&step, NULL);
        waited += 10;
    }
    if (WIFEXITED(status))
        *exit_code = WEXITSTATUS(status);
    else
        *exit_code = 128 + WTERMSIG(status);
    return 0;
}
