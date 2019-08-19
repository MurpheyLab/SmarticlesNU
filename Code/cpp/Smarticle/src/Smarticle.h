/*
  Smarticle.h - Arduino Library for NU-Smarticle
  header file for
  Alex Samland, created Aug 7, 2019
  Last Updated: Aug 7, 2019
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


#define MAX_US 2500
#define MIN_US 600
#define RX_PIN 2
#define TX_PIN 3
#define LED 13
#define SERVO_L 10
#define SERVO_R 9
#define PRF A2
#define PRB A0
#define MIC A3
#define MAX_GAIT_SIZE 15
#define GI_OFFSET 12
#define ASCII_OFFSET 32
#define MAX_DATA_PAYLOAD 108





enum STATES{IDLE = 0, STREAM=1, INTERP=2};

class Smarticle
{
  public:
    Smarticle(int debug=0, int run_servos=0, int transmit=0, int sample_time_ms = 15, int cycle_period_ms = 33);
    void led_on(int stat);
    void inactive(void);
    void timer_interrupt(void);
    void gait_interpolate(int delay, int len, uint8_t* servoL_arr, uint8_t* servoR_arr);
    void stream_servo(void);
    int set_mode(int mode);
    int init_mode(void);
    enum STATES get_mode(void);
    int * read_sensors(void);
    int transmit_data(void);
    int interp_msg(void);
    int attach_servos(void);
    int detach_servos(void);
    int run_servos(int);
    int transmit(int);
    int enable_t2_interrupts(void);
    int disable_t2_interrupts(void);
    void rx_interrupt(uint8_t c);
    PWMServo ServoL;
    PWMServo ServoR;
    NeoSWSerial Xbee;
    int cycle_time_ms;
    int sensor_dat[3];
    volatile int msg_flag = 0;
  private:
    void _plankf(void);
    enum STATES _mode;
    float _t = 0;
    int _debug;
    int _run_servos;
    int _transmit;
    volatile char  _input_string[108];
    volatile char _input_msg[108];
    int _sample_time_ms;
    uint8_t _gaitL[MAX_GAIT_SIZE];
    uint8_t _gaitR[MAX_GAIT_SIZE];
    int _gait_period=500;
    int _gait_pts=1;
    int _plank;

};

#endif
