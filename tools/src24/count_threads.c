#include <inttypes.h>
#include <stdio.h>
#include "core.h"

#ifdef _WIN32
#include <windows.h>
#define pid_self() ((int64_t)GetCurrentProcessId())
static DWORD WINAPI worker(LPVOID arg) {
    (void)arg;
    Sleep(1000);
    return 0;
}
#else
#include <pthread.h>
#include <unistd.h>
#define pid_self() ((int64_t)getpid())
static void *worker(void *arg) {
    (void)arg;
    sleep(1);
    return NULL;
}
#endif

#define WORKERS 4

static void show(const char *when) {
    int32_t n;
    int err = core_proc_threads(pid_self(), &n);
    if (err != 0)
        printf("%s: error %d\n", when, err);
    else
        printf("%s: %d threads\n", when, n);
}

int main(void) {
    show("start");
#ifdef _WIN32
    HANDLE t[WORKERS];
    for (int i = 0; i < WORKERS; i++) {
        t[i] = CreateThread(NULL, 0, worker, NULL, 0, NULL);
        if (t[i] == NULL) {
            printf("CreateThread: error %lu\n", GetLastError());
            return 1;
        }
    }
    show("running");
    WaitForMultipleObjects(WORKERS, t, TRUE, INFINITE);
    for (int i = 0; i < WORKERS; i++)
        CloseHandle(t[i]);
#else
    pthread_t t[WORKERS];
    for (int i = 0; i < WORKERS; i++) {
        int err = pthread_create(&t[i], NULL, worker, NULL);
        if (err != 0) {
            printf("pthread_create: error %d\n", err);
            return 1;
        }
    }
    show("running");
    for (int i = 0; i < WORKERS; i++)
        pthread_join(t[i], NULL);
#endif
    show("joined");
    return 0;
}
