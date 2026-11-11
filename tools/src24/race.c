#include <stdio.h>

#ifdef _WIN32
#include <windows.h>
#define ADD(p) InterlockedIncrement64(p)
#define THREAD_FN DWORD WINAPI
#define THREAD_END 0
#else
#include <pthread.h>
#define ADD(p) __atomic_fetch_add(p, 1, __ATOMIC_SEQ_CST)
#define THREAD_FN void *
#define THREAD_END NULL
#endif

#define WORKERS 4
#define STEPS 1000000

static long long counter = 0;

static THREAD_FN worker(void *arg) {
    (void)arg;
    for (int i = 0; i < STEPS; i++)
        ADD(&counter);
    return THREAD_END;
}

int main(void) {
#ifdef _WIN32
    HANDLE t[WORKERS];
    for (int i = 0; i < WORKERS; i++)
        t[i] = CreateThread(NULL, 0, worker, NULL, 0, NULL);
    WaitForMultipleObjects(WORKERS, t, TRUE, INFINITE);
    for (int i = 0; i < WORKERS; i++)
        CloseHandle(t[i]);
#else
    pthread_t t[WORKERS];
    for (int i = 0; i < WORKERS; i++)
        pthread_create(&t[i], NULL, worker, NULL);
    for (int i = 0; i < WORKERS; i++)
        pthread_join(t[i], NULL);
#endif
    printf("counter = %lld, expected %d\n", counter, WORKERS * STEPS);
    return 0;
}
