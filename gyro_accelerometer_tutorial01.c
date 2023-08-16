#include <sys/time.h>
#include <stdint.h>
#include <unistd.h>
#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <time.h>
#include "IMU.c"

#define DT 0.02         // [s/loop] loop period. 20ms
#define AA 0.97         // complementary filter constant

#define A_GAIN 0.0573    // [deg/LSB]
#define G_GAIN 0.070     // [deg/s/LSB]
#define RAD_TO_DEG 57.29578
#define M_PI 3.14159265358979323846

void INThandler(int sig) {
    signal(sig, SIG_IGN);
    exit(0);
}

int mymillis() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec) * 1000 + (tv.tv_usec) / 1000;
}

int timeval_subtract(struct timeval *result, struct timeval *t2, struct timeval *t1) {
    long int diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
    result->tv_sec = diff / 1000000;
    result->tv_usec = diff % 1000000;
    return (diff < 0);
}

int main(int argc, char *argv[]) {
    float rate_gyr_y = 0.0;
    float rate_gyr_x = 0.0;
    float rate_gyr_z = 0.0;
    int accRaw[3];
    int magRaw[3];
    int gyrRaw[3];

    float gyroXangle = 0.0;
    float gyroYangle = 0.0;
    float gyroZangle = 0.0;
    float AccYangle = 0.0;
    float AccXangle = 0.0;
    float CFangleX = 0.0;
    float CFangleY = 0.0;

    int startInt = mymillis();
    struct timeval tvBegin, tvEnd, tvDiff;
    signal(SIGINT, INThandler);
    detectIMU();
    enableIMU();
    gettimeofday(&tvBegin, NULL);

    FILE *outputFile;
    outputFile = fopen("sensor_data.txt", "w");
    if (outputFile == NULL) {
        perror("Error opening file");
        return 1;
    }

    while (1) {
        startInt = mymillis();
        readACC(accRaw);
        readGYR(gyrRaw);
        rate_gyr_x = (float)gyrRaw[0] * G_GAIN;
        rate_gyr_y = (float)gyrRaw[1] * G_GAIN;
        rate_gyr_z = (float)gyrRaw[2] * G_GAIN;
        gyroXangle += rate_gyr_x * DT;
        gyroYangle += rate_gyr_y * DT;
        gyroZangle += rate_gyr_z * DT;
        AccXangle = (float)(atan2(accRaw[1], accRaw[2]) + M_PI) * RAD_TO_DEG;
        AccYangle = (float)(atan2(accRaw[2], accRaw[0]) + M_PI) * RAD_TO_DEG;
        AccXangle -= (float)180.0;
        if (AccYangle > 90)
            AccYangle -= (float)270;
        else
            AccYangle += (float)90;
        CFangleX = AA * (CFangleX + rate_gyr_x * DT) + (1 - AA) * AccXangle;
        CFangleY = AA * (CFangleY + rate_gyr_y * DT) + (1 - AA) * AccYangle;

        // Print and store the values in the TXT file
        fprintf(outputFile, "GyroX: %7.3f\nAccXangle: %7.3f\nCFangleX: %7.3f\nGyroY: %7.3f\nAccYangle: %7.3f\nCFangleY: %7.3f\n",
            gyroXangle, AccXangle, CFangleX, gyroYangle, AccYangle, CFangleY);

        while (mymillis() - startInt < (DT * 1000)) {
            usleep(100);
        }
        printf("Loop Time %d\t", mymillis() - startInt);
    }

    fclose(outputFile);

    return 0;
}

