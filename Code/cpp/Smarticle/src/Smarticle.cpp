/*
  Smarticle.cpp - Arduino Library for NU-Smarticle
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

#include <Smarticle.h>

Smarticle:: Smarticle(int debug, int run_servos, int transmit, int sample_time_ms, int cycle_period_ms):Xbee(RX_PIN,TX_PIN)
{
  pinMode(LED,OUTPUT);
  _debug = debug;
  _mode = IDLE;
  _run_servos = run_servos;
  _transmit = transmit;
  _sample_time_ms = sample_time_ms;
  cycle_time_ms = cycle_period_ms;
  //set prescaler to 32 >> overflow period = 2.048ms
  TCCR2B = (0<<CS20)|(0<<CS21)|(1<<CS22);
  /* Clear overflow flag */
  TIFR2  = 0<<TOV2;
}

void Smarticle::led_on(int stat)
{
  if (stat==1){
    digitalWrite(LED,HIGH);
  }else{
    digitalWrite(LED,LOW);
  }
  return;
}

void Smarticle::inactive(void)
{
  return;
}
void Smarticle::_plankf(void)
{
  ServoL.write(90);
  ServoR.write(90);
  disable_t2_interrupts();
}

void Smarticle::timer_interrupt(void)
{
  if (_run_servos&_mode!=IDLE){
    if (_plank==1){
      _plankf();
    }else{
      switch (_mode) {
        case INTERP: gait_interpolate(_gait_period, _gait_pts, _gaitL, _gaitR);break;
        case STREAM: stream_servo();break;
        default: return;
      }
    }
  }
  return;
}

void Smarticle::gait_interpolate(int delay, int len, uint8_t *servoL_arr, uint8_t *servoR_arr)
{
  static int tt, index;
  if (tt>=(2*delay)){
    tt = 0;
    if (index>= len){
      index = 0;
    }
    ServoL.write(servoL_arr[index]);
    ServoR.write(servoR_arr[index]);
    index++;
  }
  tt++;
  return;
}

void Smarticle:: stream_servo(void)
{
  return;
}

int Smarticle::set_mode(int mode)
{
  // Xbee.printf("Mode input: %d\n", mode);
  switch(mode){
    case 0: _mode = IDLE;break;
    case 1: _mode = STREAM;break;
    case 2: _mode = INTERP;break;
    default: _mode = IDLE;
  }
  init_mode();
  _plank = 0;
  // Xbee.printf("DEBUG: Mode Set to: %d!\n",_mode);
  return 1;
}

int Smarticle::init_mode()
{
  if (_mode==STREAM ){
    attach_servos();
  }else if (_mode==INTERP){
      attach_servos();
      _gait_pts=1;
      _gait_period = 500;
      _gaitL[0]=90;
      _gaitR[0]=90;
  }else{
    detach_servos();
  }
}


enum STATES Smarticle::get_mode(void)
{
  return _mode;
}

int Smarticle::interp_msg(void)
{
  // Xbee.printf("DEBUG: MESSAGE RECEIVED!!\n");
  // Xbee.printf("Received message: %s\n",_input_msg);
  disable_t2_interrupts();
  msg_flag = 0;
  if (_input_msg[0]!=':'){
    // Xbee.printf("DEBUG: no match :(\n");
    // enable_t2_interrupts();
    return 0;
  }else if (_mode==INTERP&& _input_msg[1]=='G'&& _input_msg[2]=='I'){
      sscanf(_input_msg,":GI:%2d,%4d;",&_gait_pts,&_gait_period);
      for (int ii=0; ii<_gait_pts; ii++){
        _gaitL[ii]=_input_msg[GI_OFFSET+ii]-ASCII_OFFSET;
        _gaitR[ii]=_input_msg[GI_OFFSET+MAX_GAIT_SIZE+ii]-ASCII_OFFSET;
        // Xbee.printf("Index:\t%d\tL:%d\tR:%d\n",ii,_gaitL[ii],_gaitR[ii]);
      }
      // Xbee.printf("DEBUG: GI %dms period, %d points\n",_gait_period,_gait_pts);
      _plank=0;
  }else if (_mode==STREAM){
  }else if (_input_msg[1]=='M'){
    // Xbee.printf("DEBUG: MODE CHANGE!\n");
    _run_servos = 0;
    int m=0;
    if (strlen(_input_msg)==4){
      // Xbee.printf("matches length\n");
      sscanf(_input_msg,":M:%d,",&m);
    }
    // Xbee.printf("m = %d\n",m);
    set_mode(m);
    enable_t2_interrupts();
    return 1;
  } else if(_input_msg[1]=='S'&&_input_msg[3]=='0'){ run_servos(0);
} else if(_input_msg[1]=='S'&&_input_msg[3]=='1'){ run_servos(1);
} else if(_input_msg[1]=='T'&&_input_msg[3]=='1'){ transmit(1);
} else if(_input_msg[1]=='T'&&_input_msg[3]=='0'){ transmit(0);
} else if(_input_msg[1]=='P'&&_input_msg[3]=='1'){ _plank=1; //Xbee.printf("DEBUG: START PLANK!\n");
} else if(_input_msg[1]=='P'&&_input_msg[3]=='0'){ _plank=0; //Xbee.printf("DEBUG: STOP PLANK!\n");
} else if (_input_msg[1]=='S'&&_input_msg[2]=='P'){
  _run_servos=0;
  int angL=90,angR=90;
  sscanf(_input_msg,":SP:%d,%d",&angL, &angR);
  ServoL.write(angL);
  ServoR.write(angR);
  } else{
    // Xbee.printf("DEBUG: no match :(\n");
    // enable_t2_interrupts();
    return 0;
  }
  enable_t2_interrupts();
  return 1;
}


int * Smarticle::read_sensors(void)
{
  unsigned long startTime= millis();  // Start of sample window
  int dat[3]={0,0,0};
  while(millis() - startTime < 30) {
      dat[0] = max(dat[0],analogRead(PRF));
      dat[1] = max(dat[1],analogRead(PRB));
      dat[2] = max(dat[2],analogRead(MIC));
    }
  sensor_dat[0]=dat[0];
  sensor_dat[1]=dat[1];
  sensor_dat[2]=dat[2];
  return sensor_dat;
}


int Smarticle::transmit_data(void)
{
  if (_transmit){
    Xbee.printf("%d, %d, %d\n",sensor_dat[0], sensor_dat[1], sensor_dat[2]);
  }
  return 1;
}


int Smarticle::attach_servos(void)
{
  ServoL.attach(SERVO_L,MIN_US,MAX_US);
  ServoR.attach(SERVO_R,MIN_US,MAX_US);
  ServoL.write(90);
  ServoR.write(90);
  // Xbee.printf("DEBUG: Servos Attached!\n");
}

int Smarticle::detach_servos(void)
{
  ServoL.detach();
  ServoR.detach();
  // Xbee.printf("DEBUG: Servos Detached!\n");
}


int Smarticle::run_servos(int run)
{
   // Xbee.printf("DEBUG: TOGGLE SERVOS!\n");
  _run_servos = run;
  return 1;
}

int Smarticle::transmit(int run)
{
  // Xbee.printf("DEBUG: TOGGLE TRANSMIT!\n");
  _transmit = run;
  return 1;
}

int Smarticle::enable_t2_interrupts(void)
{
  TIMSK2 = 1<<TOIE2;
  // Xbee.printf("DEBUG: T2 interrupt enabled!\n");
}

int Smarticle::disable_t2_interrupts(void)
{
  TIMSK2 = 0<<TOIE2;
  // Xbee.printf("DEBUG: T2 interrupt disabled!\n");
}

void Smarticle::rx_interrupt(uint8_t c)
{
  if (c=='\n'){
    while (msg_flag==1){}
    msg_flag=1;
    strcpy(_input_msg,_input_string);
    _input_string[0]='\0';
  }else{
    int len = strlen(_input_string);
    _input_string[len++]= c;
    _input_string[len]='\0';
  }

}
