#include <stdio.h>
#include <sys/utsname.h>

int main(void) {
    struct utsname u;

    if (uname(&u) != 0) {
        perror("uname");
        return 1;
    }
    printf("sysname  %s\n", u.sysname);
    printf("release  %s\n", u.release);
    printf("machine  %s\n", u.machine);
    printf("nodename %s\n", u.nodename);
    printf("sizeof   %zu\n", sizeof u);
    return 0;
}
