#ifndef CORE_H
#define CORE_H

#include <stdint.h>

#ifdef _WIN32
#define CORE_API __declspec(dllexport)
#else
#define CORE_API
#endif

#define CORE_HOST_MAX 256

struct core_info {
    int64_t pid;
    int32_t cpus;
    int32_t page_size;
    char    host[CORE_HOST_MAX];
};

CORE_API int core_get_info(struct core_info *out);

#endif
