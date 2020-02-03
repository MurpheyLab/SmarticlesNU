/*
  Smarticle.cpp - Arduino Library for NU-Smarticle
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

  Data Transmit Format:
  '{int phot_front},{int photo_back},{int microphone}\n', where {} indicat field and integer range between 0-1023
  example: '897,1001,456'

*/

#include <Smarticle.h>

Smarticle:: Smarticle(int debug)
{
  pinMode(LED,OUTPUT);
  _debug = debug;
  _mode = IDLE;
  NeoSerial1.begin(9600);
}


void Smarticle::set_led(int state)
{
  //turn on or off system LED on pin 13
  if (state==1){
    digitalWrite(LED,HIGH);
  }else{
    digitalWrite(LED,LOW);
  }
  return;
}


void Smarticle::set_transmit(int state)
{
  //write to value of _transmit to enable/disable transmitting sensor data
  if (state==1)
  {
    _transmit = state;
  }else{ _transmit=0; }
}


void Smarticle::set_read(int state)
{
  //write to value of _transmit to enable/disable reading sensor data
  if (state==1)
  {
    _read_sensors = state;
  }else{ _read_sensors=0; }
}


void Smarticle::set_plank(int state)
{
  //sets servos to plank position
  if (state ==1)
  {
    _plank=1;
    ServoL.write(90);
    ServoR.write(90);
  }else{
    _plank=0;
  }
}

void Smarticle::set_stream_delay(int state, int max_delay_val)
{
  if (state>0){
    if (state==1){
      _stream_delay=1;
    }else{
      _stream_delay=0;
    }
  }
  if (max_delay_val>0){
    _random_delay_max=max_delay_val;
  }
}

void Smarticle::set_mode(int m)
{
  //sets mode given input
  switch(m){
    case 0: _mode = IDLE;break;
    case 1: _mode = STREAM;break;
    case 2: _mode = INTERP;break;
    default: _mode = IDLE;
  }
  init_mode();
}

void Smarticle::set_threshold(int* thresh)
{
  _sensor_threshold[0] = thresh[0];
  _sensor_threshold[1] = thresh[1];
  _sensor_threshold[2] = thresh[2];
  _sensor_threshold[3] = thresh[3];
}


void Smarticle::set_pose(int angL, int angR)
{
  //sets smarticle to given arm angles
  if (_epsilon==0){
    ServoL.write(angL-_pose_noise/2+random(_pose_noise+1));
    ServoR.write(angR-_pose_noise/2+random(_pose_noise+1));
  }
  else{
    int coinL = random(101);
    int coinR = random(101);
    if (coinL<=_epsilon){
      ServoL.write(180*random(2));
    }else{
      ServoL.write(angL-_pose_noise/2+random(_pose_noise+1));
    }
    if (coinR<=_epsilon){
      ServoR.write(180*random(2));
    }else{
      ServoR.write(angR-_pose_noise/2+random(_pose_noise+1));
    }
  }
}

void Smarticle::set_gait_num(char* msg)
{
  int n = 0;
  sscanf(msg,":GN:%d",&n);
  _index = 0;

  _gait_num = n;
}


void Smarticle::init_t4(void)
{
  /* Timer Clock = 8000000 Hz / 1024 */
  TCCR4A = 0;
  //select timer mode and set prescaler to 1024 --> each tick is 0.128ms
  TCCR4B = (0<<WGM43)|(1<<WGM42)|(1<<CS42)|(0<<CS41)|(1<<CS40);
  // initialize compare match value so that interrupt period = 500ms
  // timer 4 is 16bit timer so max compare match value = 2^16= 65,536
  OCR4A = 3906;
  /* Clear pending interrupts on timer4 */
  TIFR4  = 0;
}


void Smarticle::init_mode()
{
  //clear all flags on mode change
  _index = 0;
  if (_mode==IDLE){
    detach_servos();
    _transmit = 0;
    _read_sensors = 0;
    _plank = 0;
    _light_plank = 0;
    _epsilon = 0;
    // reset sensor thresholds
    set_threshold(_sensor_threshold_constant);
    //reset gait so that it maintains plank position
    _gait_num = 0;
    _t4_TOP = 3906; //delay of 500ms
    for (int ii=0; ii<MAX_GAIT_NUM; ii++){
      _gaitL[ii][0]=90;
      _gaitR[ii][0]=90;
      _gait_pts[ii]=1;
    }
  }else{
    attach_servos();
  }
  //clear pending t4 interrupts
  TIFR4  = 0;
  TCNT4 = 0;
}


void Smarticle::init_gait(char* msg)
{
  //get number of gait points
  disable_t4_interrupts();
  int n;
  int gait_len;
  sscanf(msg,":GI:%d,%2d,",&n, &gait_len);
  _gait_pts[n]=gait_len;
  //reconstruct 16 bit integer from two 8 bit chars to get gait delay counts for interrupt
  _t4_TOP = (msg[DELAY_OFFSET]<<8)|(msg[DELAY_OFFSET+1]&0xff);
  _half_t4_TOP = _t4_TOP/2;
  //read each of the specificed number of gait pts and save to an array of integers
  for (int ii=0; ii<_gait_pts[n]; ii++){
    _gaitL[n][ii]=msg[GAIT_OFFSET+ii]-ASCII_OFFSET;
    _gaitR[n][ii]=msg[GAIT_OFFSET+MAX_GAIT_SIZE+ii]-ASCII_OFFSET;
    if (_debug==1){NeoSerial1.printf("Number:%d\tIndex:%d\tL:%d\tR:%d\n",n,ii,_gaitL[n][ii],_gaitR[n][ii]);}
  }
  //set compare match value to delay counts
  OCR4A = _t4_TOP;
  //resent timer counts at 0
  TCNT4 = 0;
  //resent array index back at zero to start gait sequence at the beginning
  _index = 0;
}


void Smarticle::rx_interrupt(uint8_t c)
{
  //runs on every received byte
  static int len=0;
  int ind =(_msg_rx)%MSG_BUFF_SIZE;
  //if stream servo command
  if (c==0x12){
    _stream_arr[0]=_input_msg[ind][0];
    _stream_arr[1]=_input_msg[ind][1];
    _stream_cmd=1;
    _input_msg[ind][0]='\0';
    len =0;
  } else if (c==0x11){  //if sync character 0x11
    //set timer counter to half of its TOP value that triggers the interrupt
    TCNT4 = _half_t4_TOP+random(_sync_noise+1);
  //else if end of message character '\n'
  } else if (c!='\n'){
      //add character to end of input string and move over null character
      _input_msg[ind][len++]= c;
      _input_msg[ind][len]='\0';
  } else if (c=='\n'){
    //set flag that message has ben received
    _msg_rx++;
    len = 0;
  }
}

void Smarticle::manage_msg(void)
{
  // if received messages is more than read messages
  if ((_msg_rx-_msg_rd)>0){
    int ind = (_msg_rd)%MSG_BUFF_SIZE;
    _msg_rd++;
    if(_debug==1){NeoSerial1.printf("msg!>>");}
    //ensure message matches command structure of leading with a colon ':'
    // typical message structure example '':M:0' set to mode 0
    if (_input_msg[ind][0]==':'){
      interp_msg(_input_msg[ind]);
    }else if (_debug == 1){
      NeoSerial1.printf("DEBUG: wrong format >>");
      NeoSerial1.printf("%c",_input_msg[ind][0]);
    }
  }
}


int Smarticle::interp_msg(char* msg)
{
  if(_debug==1){NeoSerial1.printf("%s>>",msg);}
  //determine which command to exectue
  if (msg[1]=='M'){ interp_mode(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set mode");}
  } else if (msg[1]=='S'&& msg[3]=='0'){ disable_t4_interrupts(); if(_debug==1){NeoSerial1.printf("DEBUG: stop interrupts");}
  } else if (msg[1]=='S'&& msg[3]=='1'){ enable_t4_interrupts(); if(_debug==1){NeoSerial1.printf("DEBUG: set interrupts");}
  } else if (_mode==INTERP&& msg[1]=='G'&& msg[2]=='I'){ init_gait(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set gait");}
  } else if (msg[1]=='T'&& msg[3]=='1'){ set_transmit(1); if(_debug==1){NeoSerial1.printf("DEBUG: set transmit");}
  } else if (msg[1]=='T'&& msg[3]=='0'){ set_transmit(0); if(_debug==1){NeoSerial1.printf("DEBUG: stop transmitted");}
  } else if (msg[1]=='R'&& msg[3]=='1'){ set_read(1); if(_debug==1){NeoSerial1.printf("DEBUG: set read");}
  } else if (msg[1]=='R'&& msg[3]=='0'){ set_read(0); if(_debug==1){NeoSerial1.printf("DEBUG: stop read");}
  } else if (msg[1]=='P'&& msg[3]=='1'){ set_plank(1); if(_debug==1){NeoSerial1.printf("DEBUG: start plank");}
  } else if (msg[1]=='P'&& msg[3]=='0'){ set_plank(0); if(_debug==1){NeoSerial1.printf("DEBUG: stop plank");}
  } else if (msg[1]=='L'&& msg[2]=='P' && msg[4]=='1'){ _light_plank=1; if(_debug==1){NeoSerial1.printf("DEBUG: light_plank on");}
  } else if (msg[1]=='L'&& msg[2]=='P' && msg[4]=='0'){ _light_plank=0; if(_debug==1){NeoSerial1.printf("DEBUG: light_plank off");}
  } else if (msg[1]=='S'&& msg[2]=='T'){ interp_threshold(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set threshold");}
  } else if (msg[1]=='S'&& msg[2]=='E'){ interp_epsilon(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set pose epsilon");}
} else if (msg[1]=='G'&& msg[2]=='N'){ set_gait_num(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set gait num");}
  } else if (msg[1]=='S'&& msg[2]=='P'){ interp_pose(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set pose");}
  } else if (msg[1]=='S'&& msg[2]=='D'){ interp_delay(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set delay");}
  } else if (msg[1]=='P'&& msg[2]=='N'){ interp_pose_noise(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set pose noise");}
  } else if (msg[1]=='S'&& msg[2]=='N'){ interp_sync_noise(msg); if(_debug==1){NeoSerial1.printf("DEBUG: set sync noise");}
  } else {
    if(_debug==1){NeoSerial1.printf("DEBUG: no match :(\n");}
    return 0;
  }
  return 1;
}


void Smarticle::interp_mode(char* msg)
{
  //interpret mode change command
  int m=0;
  if (strlen(msg)==4){
    sscanf(msg,":M:%d,",&m);
  }
  set_mode(m);
}

void Smarticle::interp_threshold(char* msg)
{
  // interpret set sensor threshold command
  int thresh[4] = {1500, 1500, 1500, 1500};
  sscanf(msg,":ST:%d,%d,%d,%d",thresh,thresh+1,thresh+2,thresh+3);
  set_threshold(thresh);
}

void Smarticle:: interp_epsilon(char* msg)
{
  // interpets set epsilon command
  int eps = 0;
  sscanf(msg,":SE:%d",&eps);
  _epsilon = eps;
}


void Smarticle::interp_pose(char* msg)
{
  //interpret set pose commands
  disable_t4_interrupts();
  int angL=90,angR=90;
  sscanf(msg,":SP:%d,%d",&angL, &angR);
  set_pose(angL,angR);
}

void Smarticle::interp_pose_noise(char* msg)
{
  //interpret set pose noise commands
  int noise = 0;
  sscanf(msg,":PN:%d",&noise);
  _pose_noise = noise;
}

void Smarticle::interp_sync_noise(char* msg)
{
  //interpret set sync noise commands
  int noise = 0;
  sscanf(msg,":SN:%d",&noise);
  _sync_noise = noise;
}

void Smarticle::interp_delay(char* msg)
{
  int stat=0,max=0;
  sscanf(msg,":SD:%d,%d",&stat, &max);
  set_stream_delay(stat,max);
}


int * Smarticle::read_sensors(void)
{
  if (_read_sensors ==1){
    int dat[4]={0,0,0,0};
    //get maximum value from specified sample window
    unsigned long startTime= millis();  // Start of sample window
    while(millis() - startTime < _sample_time_ms) {
        dat[0] = max(dat[0],analogRead(PRF));
        dat[1] = max(dat[1],analogRead(PRB));
        dat[2] = max(dat[2],analogRead(PRR));
        dat[3] = max(dat[3],analogRead(STRESS));
      }
    sensor_dat[0]=dat[0];
    sensor_dat[1]=dat[1];
    sensor_dat[2]=dat[2];
    sensor_dat[3]=dat[3];
    if (_light_plank==1 && _mode==INTERP){
      bool trigger = (sensor_dat[0]>=_sensor_threshold[0]||
                     sensor_dat[1]>=_sensor_threshold[1]||
                     sensor_dat[2]>=_sensor_threshold[2]||
                     sensor_dat[3]>=_sensor_threshold[3]);
      if (_plank == 0 && trigger){
        set_plank(1);
        NeoSerial1.printf("PLANK 1\n");
      }else if (_plank == 1 && !trigger){
        set_plank(0);
        NeoSerial1.printf("PLANK 0\n");
      }
    }
  return sensor_dat;
  }
}


void Smarticle::transmit_data(void)
{
  //send data: sensor_dat[0]= photo_front, sensor_dat[1]= photo_back, sensor_dat[2]= photo_right, sensor_dat[3]= current sense
  if (_transmit && _mode!=IDLE){
    _transmit_counts++;
    _transmit_dat[0]+=sensor_dat[0];
    _transmit_dat[1]+=sensor_dat[1];
    _transmit_dat[2]+=sensor_dat[2];
    _transmit_dat[3]+=sensor_dat[3];

    if (_transmit_counts >= 10){
      NeoSerial1.printf("%d,%d,%d,%d\n",_transmit_dat[0]/_transmit_counts, _transmit_dat[1]/_transmit_counts, _transmit_dat[2]/_transmit_counts,_transmit_dat[3]/_transmit_counts);
      _transmit_dat[0]=0;
      _transmit_dat[1]=0;
      _transmit_dat[2]=0;
      _transmit_dat[3]=0;
      _transmit_counts = 0;
    }

  }
}


void Smarticle::t4_interrupt(void)
{
  if (_mode==INTERP){
        gait_interpolate(_gait_pts[_gait_num], _gaitL[_gait_num], _gaitR[_gait_num]);
  }
}


void Smarticle::enable_t4_interrupts(void)
{
  if (_mode==INTERP){
    //enable timer4 compare match A interrupt
    TIMSK4 = 1<<OCIE4A;
    TCNT4 = 0;
    _index=0;
  }
}


void Smarticle::disable_t4_interrupts(void)
{
  //disable all timer4 interrupts
  TIMSK4 = 0;
}


void Smarticle::stream_servo(void)
{
  if (_mode==STREAM & _stream_cmd==1){
    _stream_cmd=0;
    if (_stream_delay==1){
        delay(random(_random_delay_max));
    }
    if (_stream_arr[0]==200+ASCII_OFFSET && _stream_arr[1]==200+ASCII_OFFSET){
      set_pose(random(181),random(181));\
      //  sXbee.printf("DEBUG; rand");
    }else if(_stream_arr[0]==190+ASCII_OFFSET && _stream_arr[1]==190+ASCII_OFFSET) {
      set_pose(180*random(2),180*random(2));
    }else{set_pose(_stream_arr[0]-ASCII_OFFSET,_stream_arr[1]-ASCII_OFFSET);}
  }
}


void Smarticle::gait_interpolate(int len, uint8_t *servoL_arr, uint8_t *servoR_arr)
{
    //move servos to next position specified in gait array
    if (_plank ==0){
      set_pose(servoL_arr[_index%len],servoR_arr[(_index)%len]);
    }
    _index++;
}


void Smarticle::attach_servos(void)
{
  //attach servos and move to position (90,90)
  if (_mode!=IDLE && _servos_attached==0){
      _servos_attached = 1;
      ServoL.attach(SERVO_L,MIN_US,MAX_US);
      ServoR.attach(SERVO_R,MIN_US,MAX_US);
      set_pose(90,90);
    }
}


void Smarticle::detach_servos(void)
{
  //detach servos
  ServoL.detach();
  ServoR.detach();
  _servos_attached=0;
}
