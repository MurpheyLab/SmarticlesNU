/*
  Smarticle.h - Arduino Library for NU-Smarticle
  header file for
  Alex Samland, created Aug 7, 2019
  Last Updated: Oct 31, 2019
  v2.0


  NU-Smarticle v2 Pins:
  A0    --    Photoresistor Right
  A1    --    Servo Current Sense
  A2    --    Photoresistor Back
  A3    --    Photoresistor Front
  --    --    XBee Dout (Serial1)
  --    --    XBee Din (Serial1)
  D7    --    External pth LED
  D10    --    Right Servo Signal
  D9   --    Left Servo Signal
  D13   --    SCK Red LED


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
#include "NeoHWSerial.h"

//max microsecond pulse sent to servos; adjust to change 180 deg position
#define MAX_US 2500
//min microsecond pulse sent to servos; adjust to change 0 deg position
#define MIN_US 600
#define RX_PIN 2
#define TX_PIN 3
#define LED 13
#define SERVO_L 9
#define SERVO_R 10
#define PRF A3 //photoresistor front
#define PRB A2 //photoresistor back
#define PRR A0 //photoresistor Right
#define STRESS A1 //Current Sense
//max number of gait points that can be sent to smarticle in gait interpolation mode
#define MAX_GAIT_SIZE 15
#define MAX_GAIT_NUM 8
//offsets for gait interpolation message interpretation
#define DELAY_OFFSET 9
#define GAIT_OFFSET 12
#define ASCII_OFFSET 32
//max data that can be sent in an xbee message
#define MAX_DATA_PAYLOAD 108
#define MAX_MSG_SIZE 50
#define MSG_BUFF_SIZE 4


enum STATES{IDLE = 0, STREAM=1, INTERP=2};

class Smarticle
{
  public:
    Smarticle(int debug=0);

    void set_led(int state);
    void set_transmit(int state);
    void set_read(int state);
    void set_plank(int state);
    void set_gait_num(char* msg);
    void set_mode(int mode);
    void set_threshold(int* thresh);
    void set_pose(int angL, int angR);
    void set_stream_delay(int state, int max_delay_val);

    void init_t4(void);
    void init_mode(void);
    void init_gait(char* msg);

    void rx_interrupt(uint8_t c);
    void manage_msg(void);

    int interp_msg(char* msg);
    void interp_threshold(char* msg);
    void interp_epsilon(char* msg);
    void interp_mode(char* msg);
    void interp_pose(char* msg);
    void interp_pose_noise(char* msg);
    void interp_sync_noise(char* msg);
    void interp_delay(char* msg);

    int * read_sensors(void);
    void transmit_data(void);


    void t4_interrupt(void);
    void enable_t4_interrupts(void);
    void disable_t4_interrupts(void);

    void stream_servo(void);
    void gait_interpolate(int len, uint8_t* servoL_arr, uint8_t* servoR_arr);

    void attach_servos(void);
    void detach_servos(void);
    PWMServo ServoL;
    PWMServo ServoR;
    int sensor_dat[4]={0,0,0,0};
  private:
    enum STATES _mode;
    char _input_msg[MSG_BUFF_SIZE][MAX_MSG_SIZE];
    //flags
    volatile uint32_t _msg_rx = 0;
    uint32_t _msg_rd=0;
    uint8_t _stream_arr[2]={0,0};
    int _sensor_threshold_constant[4]={1500,1500,1500,1500};
    int _sensor_threshold[4]={1500,1500,1500,1500};
    int _transmit_dat[4]={0,0,0,0};
    int _transmit_counts;
    int _stream_cmd=0;
    int _stream_delay = 0;
    int _random_delay_max  = 50;
    int _debug=0;
    int _read_sensors=0;
    int _transmit=0;
    int _light_plank=0;
    int _plank =0;
    int _sample_time_ms=10;
    int _servos_attached= 0;
    uint8_t _gaitL[MAX_GAIT_NUM][MAX_GAIT_SIZE];
    uint8_t _gaitR[MAX_GAIT_NUM][MAX_GAIT_SIZE];
    uint16_t _t4_TOP = 3906; //500ms
    uint16_t _half_t4_TOP = 1953;
    int _gait_pts[MAX_GAIT_NUM];
    int _gait_num = 0;
    uint16_t _index = 0;
    int _pose_noise = 0;
    int _sync_noise = 0;
    int _epsilon = 0;

};

#endif
