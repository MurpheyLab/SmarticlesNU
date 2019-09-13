/*
  Smarticle.cpp - Arduino Library for NU-Smarticle
  Alex Samland, created Aug 7, 2019
  Last Updated: Aug 29, 2019
  v1.0

  NU-Smarticle v1 Pins:
  A0    --    Photoresistor Back
  A1    --    Servo Current Sense
  A2    --    Photoresistor Front
  A3    --    Microphone (will be changed to resolve pin conflict)
  A3    --    Photoresistor Left
  D2    --    XBee Dout (Arduino SWserial RX)
  D3    --    XBee Din (Arduino SWserial TX)
  D7    --    External pth LED
  D9    --    Right Servo Signal (bridged through D4)
  D10   --    Left Servo Signal
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

Smarticle:: Smarticle(int debug, int run_servos, int transmit, int sample_time_ms, int cycle_period_ms):Xbee(RX_PIN,TX_PIN)
{
  pinMode(LED,OUTPUT);
  //debug currently not implemented; just uncomment print statements for debug help
  _debug = debug;
  _mode = IDLE;
  _run_servos = run_servos;
  _transmit = transmit;
  _sample_time_ms = sample_time_ms;
  cycle_time_ms = cycle_period_ms;
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
    //flag so that t4 interrupt doesnt write to servos
    _plank=1;
    ServoL.write(90);
    ServoR.write(90);
  }else{
    _plank=0;
  }
}


void Smarticle::set_mode(int m)
{
  //sets mode given input
  Xbee.printf("Mode input: %d\n", m);
  switch(m){
    case 0: _mode = IDLE;break;
    case 1: _mode = STREAM;break;
    case 2: _mode = INTERP;break;
    default: _mode = IDLE;
  }
  init_mode();
}


void Smarticle::set_pose(int angL, int angR)
{
  //sets smarticle to given arm angles
  Xbee.printf("set pose: %d, %d",angL,angR);
  ServoL.write(angL);
  ServoR.write(angR);
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
    _run_servos=0;
    _transmit = 0;
    _plank = 0;
    _read_sensors = 0;
    //reset gait se maintains plank position
    _gait_pts=1;
    _t4_TOP = 3906; //delay of 500ms
    _gaitL[0]=90;
    _gaitR[0]=90;
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
  sscanf(msg,":GI:%2d,",&_gait_pts);
  //reconstruct 16 bit integer from two 8 bit chars to get gait delay counts for interrupt
  _t4_TOP = (msg[DELAY_OFFSET]<<8)|(msg[DELAY_OFFSET+1]&0xff);
  _half_t4_TOP = _t4_TOP/2;
  //read each of the specificed number of gait pts and save to an array of integers
  for (int ii=0; ii<_gait_pts; ii++){
    _gaitL[ii]=msg[GAIT_OFFSET+ii]-ASCII_OFFSET;
    _gaitR[ii]=msg[GAIT_OFFSET+MAX_GAIT_SIZE+ii]-ASCII_OFFSET;
    // Xbee.printf("Index:\t%d\tL:%d\tR:%d\n",ii,_gaitL[ii],_gaitR[ii]);
  }
  //set compare match value to delay counts
  OCR4A = _t4_TOP;
  //resent timer counts at 0
  TCNT4 = 0;
  //resent array index back at zero to start gait sequence at the beginning
  _index = 0;

  // Xbee.printf("DEBUG: GI %d ms period, %d points\n",_t4_counter,_gait_pts);
}


void Smarticle::rx_interrupt(uint8_t c)
{
  //runs on every received byte
  static int len;
  //if stream servo command
  if (_mode==STREAM && c==0x12){
    // Serial.printf("stream");
    stream_servo(_input_string[0],_input_string[1]);
    _input_string[len-2]='\0';
    len -=2;

  } else if (_mode==INTERP && c==0x11){  //if sync character 0x11
    //set timer counter to half of its TOP value that triggers the interrupt
    TCNT4 = _half_t4_TOP;

  //else if end of message character '\n'
} else if (c!='\n'){
    //add character to end of input string and move over null character
    _input_string[len++]= c;
    _input_string[len]='\0';
  } else if (c=='\n'){
    //set flag that message has ben received
    _msg_rx++;
    //copy over to input_msg and clear input_string so that incoming bytes can still be stored
    strcpy(_input_msg[(_msg_rx-1)%MSG_BUFF_SIZE],_input_string);
    _input_string[0]='\0';
    len = 0;
  }
}

void Smarticle::manage_msg(void)
{
  if ((_msg_rx-_msg_rd)>0){
    int ind = (_msg_rd++)%MSG_BUFF_SIZE;
    Xbee.printf("msg!:\t");
    interp_msg(_input_msg[ind]);
  }
}


int Smarticle::interp_msg(char* msg)
{
  Xbee.printf("%s\n",msg);
  //ensure message matches command structure of leading with a colon ':'
  // typical message structure example '':M:0' set to mode 0
  if (msg[0]!=':'){
    // Xbee.printf("DEBUG: no match :(\n");
    return 0;
  //determine which command to exectue
  } else if (msg[1]=='M'){ interp_mode(msg);
  } else if (msg[1]=='S'&& msg[3]=='0'){ enable_t4_interrupts();
  } else if (msg[1]=='S'&& msg[3]=='1'){ disable_t4_interrupts();
  } else if (_mode==INTERP&& msg[1]=='G'&& msg[2]=='I'){ init_gait(msg);
  } else if (msg[1]=='T'&& msg[3]=='1'){ set_transmit(1);
  } else if (msg[1]=='T'&& msg[3]=='0'){ set_transmit(0);
  } else if (msg[1]=='R'&& msg[3]=='1'){ set_read(1);
  } else if (msg[1]=='R'&& msg[3]=='0'){ set_read(0);
  } else if (msg[1]=='P'&& msg[3]=='1'){ set_plank(1); //Xbee.printf("DEBUG: START PLANK!\n");
  } else if (msg[1]=='P'&& msg[3]=='0'){ set_plank(0); //Xbee.printf("DEBUG: STOP PLANK!\n");
  } else if (msg[1]=='S'&& msg[2]=='P'){ interp_pose(msg);
  } else {
    // Xbee.printf("DEBUG: no match :(\n");
    return 0;
    Xbee.printf("no match :(\n");
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


void Smarticle::interp_pose(char* msg)
{
  //interpret set pose commands
  set_servos(0);
  int angL=90,angR=90;
  sscanf(msg,":SP:%d,%d",&angL, &angR);
  set_pose(angL,angR);
}


int * Smarticle::read_sensors(void)
{
  if (_read_sensors ==1){
    unsigned long startTime= millis();  // Start of sample window
    int dat[3]={0,0,0};
    //get maximum value from specified sample window
    while(millis() - startTime < _sample_time_ms) {
        dat[0] = max(dat[0],analogRead(PRF));
        dat[1] = max(dat[1],analogRead(PRB));
        dat[2] = max(dat[2],analogRead(MIC));
      }
    sensor_dat[0]=dat[0];
    sensor_dat[1]=dat[1];
    sensor_dat[2]=dat[2];
  }
  return sensor_dat;
}


void Smarticle::transmit_data(void)
{
  //send data: sensor_dat[0]= photo_front, sensor_dat[1]= photo_back, sensor_dat[2]= mic
  if (_transmit && _mode!=IDLE){
    Xbee.printf("%d,%d,%d\n",sensor_dat[0], sensor_dat[1], sensor_dat[2]);
  }
}


void Smarticle::t4_interrupt(void)
{
  //runs when TCNT4 = OCR4A
  // if (_mode!=IDLE){
  //   //if plank flag is set, plank!
  //   if (_plank==1){
  //     ServoL.write(90);
  //     ServoR.write(90);
  //   }else if (_run_servos==1 && _mode==INTERP){
  if (_mode==INTERP){
      gait_interpolate(_gait_pts, _gaitL, _gaitR);
    }
  // }
}


void Smarticle::enable_t4_interrupts(void)
{
  if (_mode==INTERP){
    //enable timer4 compare match A interrupt
    TIMSK4 = 1<<OCIE4A;
    TCNT4 = 0;
    _index=0;
  }
  // Xbee.printf("DEBUG: T2 interrupt enabled!\n");
}


void Smarticle::disable_t4_interrupts(void)
{
  //disable all timer4 interrupts
  TIMSK4 = 0;
  // Xbee.printf("DEBUG: T2 interrupt disabled!\n");
}


void Smarticle:: stream_servo(uint8_t angL, uint8_t angR)
{
  set_pose(angL-ASCII_OFFSET,angR-ASCII_OFFSET);
  // Xbee.printf("DEBUG:Stream!: %d, %d",angL-ASCII_OFFSET), angR-ASCII_OFFSET));

}


void Smarticle::gait_interpolate(int len, uint8_t *servoL_arr, uint8_t *servoR_arr)
{
    //move servos to next position specified in gait array
    set_pose(servoL_arr[_index%len],servoR_arr[(_index++)%len]);
}


void Smarticle::attach_servos(void)
{
  //attach servos and move to position (90,90)
  if (_mode!=IDLE){
    ServoL.attach(SERVO_L,MIN_US,MAX_US);
    ServoR.attach(SERVO_R,MIN_US,MAX_US);
    Xbee.printf("DEBUG: Servos Attached!\n");
    set_pose(90,90);
  }
}


void Smarticle::detach_servos(void)
{
  //detach servos
  ServoL.detach();
  ServoR.detach();
  // Xbee.printf("DEBUG: Servos Detached!\n");
}


void Smarticle::set_servos(int run)
{
   // Xbee.printf("DEBUG: TOGGLE SERVOS!\n");
  _run_servos = run;
  _index = 0;
  TCNT4 = 0;
}
