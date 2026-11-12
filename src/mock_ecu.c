#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

static void send_signal(int sock, canid_t id, uint16_t value)
{
    struct can_frame frame = {0};

    frame.can_id = id;
    frame.can_dlc = 2;
    frame.data[0] = (value >> 8) & 0xFF;
    frame.data[1] = value & 0xFF;

    if (write(sock, &frame, sizeof(frame)) != sizeof(frame)) {
        perror("CAN write");
        exit(EXIT_FAILURE);
    }

    printf("CAN ID: 0x%03X | Value: %u\n", id, value);
}

int main(void)
{
    int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    if (sock < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct ifreq ifr = {0};
    strncpy(ifr.ifr_name, "vcan0", IFNAMSIZ - 1);

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("ioctl");
        close(sock);
        return EXIT_FAILURE;
    }

    struct sockaddr_can addr = {0};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return EXIT_FAILURE;
    }

    unsigned int rpm = 800;
    unsigned int speed = 0;
    unsigned int temperature = 85;

    puts("CAN-Sentinel Mock ECU started on vcan0");

    while (1) {
        send_signal(sock, 0x100, rpm);
        send_signal(sock, 0x101, speed);
        send_signal(sock, 0x102, temperature);

        rpm = (rpm >= 3000) ? 800 : rpm + 100;
        speed = (speed >= 120) ? 0 : speed + 5;
        temperature = (temperature >= 100) ? 85 : temperature + 1;

        usleep(500000);
    }

    close(sock);
    return EXIT_SUCCESS;
}
