/*
  Smarticle.h - Arduino Library for NU-Smarticle
  header file for
  Alex Samland, created Aug 7, 2019
  Last Updated: Feb 11, 2020
  v2.1


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
#define SENSOR_COUNT 4
#define GAIT_OFFSET 7
#define VALUE_OFFSET 3
#define ASCII_OFFSET 32
//max data that can be sent in an xbee message
#define MAX_DATA_PAYLOAD 108
#define MAX_MSG_SIZE 40
#define MSG_BUFF_SIZE 4
//default sensor read time
#define DEFAULT_SAMPLE_TIME_MS 10


enum STATES{IDLE = 0, STREAM=1, INTERP=2};

class Smarticle
{
  public:
    Smarticle(int debug=0);

    void init_t4(void);
    void attach_servos(void);
    void detach_servos(void);

    bool toggle_led(char state);
    uint8_t set_mode(char m);
    void init_mode(void);
    bool toggle_t4_interrupt(char state);
    bool toggle_plank(char state);
    uint8_t select_gait(char n);
    bool toggle_read_sensors(char state);
    bool toggle_transmit(char state);
    uint8_t set_gait_epsilon(char eps);
    uint8_t set_pose_noise(char noise_range);
    void set_plank(uint8_t);
    bool toggle_light_plank(char state);

    void set_pose(uint8_t angL, uint8_t angR);
    uint16_t set_sync_noise(uint16_t max_noise);
    uint16_t set_stream_timing_noise(uint16_t max_delay_val);
    uint8_t set_transmit_counts(uint8_t counts);
    uint8_t set_debug(uint8_t debug);
    uint8_t set_id(uint8_t val);

    void set_light_plank_threshold(uint16_t* thresh);
    void init_gait(volatile char* msg);

    void rx_interrupt(uint8_t c);
    void manage_msg(void);

    uint16_t * read_sensors(void);
    void transmit_data(void);
    void interp_stream_cmd(volatile char* msg);
    void interp_plank_cmd(volatile char* msg);

    void t4_interrupt(void);




    PWMServo ServoL;
    PWMServo ServoR;
    uint16_t sensor_dat[SENSOR_COUNT]={0,0,0,0};
    uint8_t id = 0;
  private:
    enum STATES _mode;

    // Private functions
    uint16_t _convert_to_16bit(char val_7bit_1, char val_7bit_2);
    void _interp_msg(volatile char* msg);
    void _gait_interpolate(int len, uint8_t* servoL_arr, uint8_t* servoR_arr);

    // volatile variables used in ISRs
    // rx_interrupt
    volatile char _input_msg[MSG_BUFF_SIZE][MAX_MSG_SIZE];
    volatile uint32_t _msg_rx = 0;
    volatile bool _stream_cmd=0;
    volatile uint16_t _half_t4_TOP = 1953;
    volatile uint16_t _sync_noise = 0;


    // t4_interrupt
    volatile bool _plank =0;
    // interrupt disabled while modifying these
    uint8_t _gait_pts[MAX_GAIT_NUM];
    uint8_t _gaitL[MAX_GAIT_NUM][MAX_GAIT_SIZE];
    uint8_t _gaitR[MAX_GAIT_NUM][MAX_GAIT_SIZE];
    volatile uint8_t _gait_num = 0;
    volatile uint32_t _index = 0;
    volatile uint8_t _pose_noise = 0;
    volatile uint8_t _gait_epsilon = 0;


    uint8_t _stream_arr[20];
    uint32_t _msg_rd=0;
    uint16_t _sensor_threshold_constant[SENSOR_COUNT]={1500,1500,1500,1500};
    uint16_t _sensor_threshold[SENSOR_COUNT]={1500,1500,1500,1500};
    uint32_t _transmit_dat[4]={0,0,0,0};
    uint16_t _transmit_counts = 10; // how many times you read before you transmit
    uint16_t _random_stream_delay_max  = 0;
    uint8_t _debug=0;
    bool _read_sensors=0;
    bool _transmit=0;
    bool _light_plank=0;
    uint8_t _sample_time_ms= DEFAULT_SAMPLE_TIME_MS;
    bool _servos_attached= 0;
    uint16_t _t4_TOP = 3906; //500ms

};

#endif
