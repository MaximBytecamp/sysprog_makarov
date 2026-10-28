#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void dump(const char *buf, size_t n) {
    for (size_t i = 0; i < n; i++)
        printf("%02x ", (unsigned char)buf[i]);
    printf("\n");
}

int main(void) {
    char host[256];
    char tiny[4];

    gethostname(host, sizeof host);
    printf("host  \"%s\", length %zu\n", host, strlen(host));
    dump(host, strlen(host) + 1);

    memset(tiny, 'X', sizeof tiny);
    int rc = gethostname(tiny, sizeof tiny);
    printf("tiny  rc=%d errno=%d (%s)\n", rc, rc ? errno : 0, rc ? strerror(errno) : "-");
    dump(tiny, sizeof tiny);
    return 0;
}
