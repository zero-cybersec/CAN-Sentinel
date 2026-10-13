#include "can_common.h"
#include <net/if.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <unistd.h>

int can_open(const char *ifname)
{
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) { perror("socket"); return -1; }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof ifr);
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) { perror("ioctl SIOCGIFINDEX"); close(s); return -1; }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof addr);
    addr.can_family  = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(s, (struct sockaddr *)&addr, sizeof addr) < 0) { perror("bind"); close(s); return -1; }
    return s;
}

int can_send(int s, canid_t id, const unsigned char *data, unsigned char len)
{
    struct can_frame f;
    memset(&f, 0, sizeof f);
    f.can_id  = id;
    f.can_dlc = len > 8 ? 8 : len;
    memcpy(f.data, data, f.can_dlc);
    if (write(s, &f, sizeof f) != sizeof f) { perror("write"); return -1; }
    return 0;
}

void can_print(const char *tag, const struct can_frame *f)
{
    printf("%-6s %03X [%d] ", tag, f->can_id & CAN_EFF_MASK, f->can_dlc);
    for (int i = 0; i < f->can_dlc; i++) printf("%02X ", f->data[i]);
    printf("\n");
    fflush(stdout);
}
