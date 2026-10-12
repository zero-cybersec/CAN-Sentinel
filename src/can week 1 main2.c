#include "can_common.h"
#include <signal.h>
#include <stdio.h>
#include <sys/select.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t running = 1;
static void on_sig(int s) { (void)s; running = 0; }

static void decode(const struct can_frame *f)
{
    unsigned id = f->can_id & CAN_SFF_MASK;
    if (id == ID_ENGINE_STATUS && f->can_dlc >= 5) {
        printf("STATUS  rpm=%4u speed=%3u km/h coolant=%3d C cnt=%u\n",
               (f->data[0] << 8) | f->data[1], f->data[2], f->data[3] - 40, f->data[4]);
    } else if (id == ID_OBD_RESPONSE && f->data[1] == 0x41) {
        switch (f->data[2]) {
        case PID_RPM:     printf("OBD     RPM     = %u\n", ((f->data[3] << 8) | f->data[4]) / 4); break;
        case PID_SPEED:   printf("OBD     Speed   = %u km/h\n", f->data[3]); break;
        case PID_COOLANT: printf("OBD     Coolant = %d C\n", f->data[3] - 40); break;
        }
    } else {
        can_print("OTHER", f);
    }
    fflush(stdout);
}

int main(int argc, char **argv)
{
    const char *ifn = argc > 1 ? argv[1] : "vcan0";
    int s = can_open(ifn);
    if (s < 0) return 1;
    signal(SIGINT, on_sig);

    const unsigned char pids[] = {PID_RPM, PID_SPEED, PID_COOLANT};
    int idx = 0;
    time_t last = 0;

    while (running) {
        time_t now = time(NULL);
        if (now != last) {
            unsigned char req[8] = {2, 0x01, pids[idx++ % 3], 0, 0, 0, 0, 0};
            can_send(s, ID_OBD_REQUEST, req, 8);
            last = now;
        }
        fd_set rf; FD_ZERO(&rf); FD_SET(s, &rf);
        struct timeval tv = {0, 200000};
        if (select(s + 1, &rf, NULL, NULL, &tv) > 0) {
            struct can_frame f;
            if (read(s, &f, sizeof f) == sizeof f) decode(&f);
        }
    }
    close(s);
    return 0;
}
