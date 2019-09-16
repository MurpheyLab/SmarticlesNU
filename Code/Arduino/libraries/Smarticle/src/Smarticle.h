/*
  Smarticle.h - Arduino Library for NU-Smarticle
  header file for
  Alex Samland, created Aug 7, 2019
  Last Updated: Aug 29, 2019
  v1.0

  NU-Smarticle v1 Pins:
  A0    --    Photoresistor Back
  A1    --    Servo Current Sense
  A2    --    Photoresistor Front
  A3    --    Microphone (will be changed to resolve pin conflict)
  A3    --    Photoresistor Left
  D2    --    XBee Dout (Arduino serial RX)
  D3    --    XBee Din (Arduino serial TX)
  D7    --    External pth LED
  D9    --    Right Servo Signal (bridged through D4)
  D10   --    Left Servo Signal
  D13   --    SCK Red Led


  Smarticle Modes:
  0   --    Inactive
  1   --    Streamed Gait
  2   --    Interpolated Gait


*/

#ifndef __SMARTICLE_H__
#define __SMARTICLE_H__

#include <string.h>
#include "Arduino.h"
#include "PWMServo.h"
#include "NeoSWSerial.h"

//max microsecond pulse sent to servos; adjust to change 180 deg position
#define MAX_US 2500
//min microsecond pulse sent to servos; adjust to change 0 deg position
#define MIN_US 600
#define RX_PIN 2
#define TX_PIN 3
#define LED 13
#define SERVO_L 10
#define SERVO_R 9
#define PRF A2 //photoresistor front
#define PRB A0 //photoresistor back
#define MIC A3 //microphone
//max number of gait points that can be sent to smarticle in gait interpolation mode
#define MAX_GAIT_SIZE 15
//offsets for gait interpolation message interpretation
#define DELAY_OFFSET 7
#define GAIT_OFFSET 10
#define ASCII_OFFSET 32
//max data that can be sent in an xbee message
#define MAX_DATA_PAYLOAD 108
#define MAX_MSG_SIZE 50
#define MSG_BUFF_SIZE 4


enum STATES{IDLE = 0, STREAM=1, INTERP=2};

class Smarticle
{
  public:
    Smarticle(int debug=0, int run_servos=0, int transmit=0, int sample_time_ms = 15, int cycle_period_ms = 33);

    void set_led(int state);
    void set_transmit(int state);
    void set_read(int state);
    void set_plank(int state);
    void set_mode(int mode);
    void set_pose(int angL, int angR);
    void set_servos(int state);

    void init_t4(void);
    void init_mode(void);
    void init_gait(char* msg);

    void rx_interrupt(uint8_t c);
    void manage_msg(void);

    int interp_msg(char* msg);
    void interp_mode(char* msg);
    void interp_pose(char* msg);

    int * read_sensors(void);
    void transmit_data(void);


    void t4_interrupt(void);
    void enable_t4_interrupts(void);
    void disable_t4_interrupts(void);

    void stream_servo(uint8_t angL, uint8_t angR);
    void gait_interpolate(int len, uint8_t* servoL_arr, uint8_t* servoR_arr);

    void attach_servos(void);
    void detach_servos(void);
    PWMServo ServoL;
    PWMServo ServoR;
    NeoSWSerial Xbee;
    int cycle_time_ms;
    int sensor_dat[3]={0,0,0};
  private:
    enum STATES _mode;
    char _input_msg[MSG_BUFF_SIZE][MAX_MSG_SIZE];
    //flags
    volatile uint32_t _msg_rx = 0;
    uint32_t _msg_rd=0;
    int _debug=0;
    int _run_servos=0;
    int _read_sensors=0;
    int _transmit=0;
    int _plank=0;
    int _sample_time_ms=15;
    void _plankf(void);
    uint8_t _gaitL[MAX_GAIT_SIZE];
    uint8_t _gaitR[MAX_GAIT_SIZE];
    uint16_t _t4_TOP = 3906; //500ms
    uint16_t _half_t4_TOP = 1953;
    int _gait_pts=1;
    uint16_t _index = 0;

};

#endif
