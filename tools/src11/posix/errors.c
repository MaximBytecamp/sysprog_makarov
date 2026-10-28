#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void try_open(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd == -1) {
        int code = errno;
        printf("%-22s fd=-1 errno=%d %s\n", path, code, strerror(code));
        return;
    }
    printf("%-22s fd=%d\n", path, fd);
    close(fd);
}

int main(void) {
    try_open("/etc/hosts");
    try_open("/etc/no-such-file");
    try_open("/etc/sudoers");
    return 0;
}
