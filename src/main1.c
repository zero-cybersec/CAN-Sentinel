
#include "can_common.h"
#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t running = 1;
static void on_sig(int s) { (void)s; running = 0; }

typedef struct { unsigned rpm; unsigned speed; int coolant; } engine_t;

static void simulate(engine_t *e, double t)
{
    e->rpm     = (unsigned)(2000 + 1500 * sin(t * 0.5));
    e->speed   = (unsigned)(60 + 40 * sin(t * 0.2));
    e->coolant = (int)(t < 60 ? 20 + t * 1.2 : 92);
}

static void handle_obd(int s, const struct can_frame *f, const engine_t *e)
{
    if (f->can_dlc < 3 || f->data[1] != 0x01) return;
    unsigned char r[8] = {0, 0x41, f->data[2], 0x55, 0x55, 0x55, 0x55, 0x55};
    switch (f->data[2]) {
    case PID_RPM: { unsigned v = e->rpm * 4; r[0] = 4; r[3] = v >> 8; r[4] = v & 0xFF; break; }
    case PID_SPEED:   r[0] = 3; r[3] = (unsigned char)e->speed; break;
    case PID_COOLANT: r[0] = 3; r[3] = (unsigned char)(e->coolant + 40); break;
    default: return;
    }
    can_send(s, ID_OBD_RESPONSE, r, 8);
    printf("OBD response PID 0x%02X sent\n", f->data[2]);
}

int main(int argc, char **argv)
{
    const char *ifn = argc > 1 ? argv[1] : "vcan0";
    int s = can_open(ifn);
    if (s < 0) return 1;


    struct can_filter flt = { ID_OBD_REQUEST, CAN_SFF_MASK };
    setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &flt, sizeof flt);

    signal(SIGINT, on_sig);
    printf("Mock ECU running on %s (Ctrl+C to stop)\n", ifn);

    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    engine_t e = {0};
    unsigned char counter = 0;

    while (running) {
        clock_gettime(CLOCK_MONOTONIC, &now);
        double t = (now.tv_sec - t0.tv_sec) + (now.tv_nsec - t0.tv_nsec) / 1e9;
        simulate(&e, t);


        unsigned char d[5] = { e.rpm >> 8, e.rpm & 0xFF, (unsigned char)e.speed,
                               (unsigned char)(e.coolant + 40), counter++ };
        can_send(s, ID_ENGINE_STATUS, d, 5);


        fd_set rf; FD_ZERO(&rf); FD_SET(s, &rf);
        struct timeval tv = {0, 100000};
        while (select(s + 1, &rf, NULL, NULL, &tv) > 0) {
            struct can_frame f;
            if (read(s, &f, sizeof f) == sizeof f) { can_print("RX", &f); handle_obd(s, &f, &e); }
            FD_ZERO(&rf); FD_SET(s, &rf);
        }
    }
    close(s);
    puts("\nECU stopped.");
    return 0;
}
