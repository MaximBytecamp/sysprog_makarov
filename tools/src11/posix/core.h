#ifndef CORE_H
#define CORE_H

#include <stdint.h>

#define CORE_HOST_MAX 256

struct core_info {
    int64_t pid;
    int32_t cpus;
    int32_t page_size;
    char    host[CORE_HOST_MAX];
};

int core_get_info(struct core_info *out);

#endif
