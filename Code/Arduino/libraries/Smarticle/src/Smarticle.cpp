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

Smarticle:: Smarticle(int debug){
  pinMode(LED,OUTPUT);
  _debug = debug;
  _mode = IDLE;
  NeoSerial1.begin(9600);

}

void Smarticle::init_t4(void){
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

void Smarticle::attach_servos(void){
  //attach servos and move to position (90,90)
  if (_mode!=IDLE && _servos_attached==0){
      _servos_attached = 1;
      ServoL.attach(SERVO_L,MIN_US,MAX_US);
      ServoR.attach(SERVO_R,MIN_US,MAX_US);
      set_pose(90,90);
    }
}

void Smarticle::detach_servos(void){
  //detach servos
  ServoL.detach();
  ServoR.detach();
  _servos_attached=0;
}

bool Smarticle::toggle_led(char state){
  //turn on or off system LED on pin 13
  if (state==1){
    digitalWrite(LED,HIGH);
    return 1;
  }else{
    digitalWrite(LED,LOW);
    return 0;
  }
}

uint8_t Smarticle::set_mode(char m){
  //sets mode given input
  switch(m){
    case 0: _mode = IDLE;break;
    case 1: _mode = STREAM;break;
    case 2: _mode = INTERP;break;
    default: _mode = IDLE;
  }
  init_mode();
  return (uint8_t) _mode;
}

void Smarticle::init_mode(){
  //reset gait index to zero
  _index = 0;
  //clear all flags and parameters when switching to IDLE
  if (_mode==IDLE){
    // turn off t4 interrupt
    toggle_t4_interrupt(0);
    detach_servos();
    // flags
    _read_sensors = 0;
    _transmit = 0;
    _plank = 0;
    _light_plank = 0;
    // parameters
    _sync_noise = 0;
    _pose_noise = 0;
    _gait_epsilon = 0;
    _transmit_counts = 1;
    _random_stream_delay_max = 0;
    _sample_time_ms = DEFAULT_SAMPLE_TIME_MS;
    // reset sensor thresholds
    set_light_plank_threshold(_sensor_threshold_constant);
    //reset gait parameters so that gait is just plank position
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

bool Smarticle::toggle_t4_interrupt(char state){
  if (_mode==INTERP && state==1){
    //enable timer4 compare match A interrupt
    TIMSK4 = 1<<OCIE4A;
    TCNT4 = 0;
    // reset gait index
    _index=0;
    return 1;
  } else{
    //disable all timer4 interrupts
    TIMSK4 = 0;
    return 0;
  }
}

bool Smarticle::toggle_plank(char state){
  //sets servos to plank position
  if (state ==1)
  {
    _plank=1;
    ServoL.write(90);
    ServoR.write(90);
  }else{
    _plank=0;
  }
  return _plank;
}

uint8_t Smarticle::select_gait(char n){
  _index = 0;
  _gait_num = n;
  return _gait_num;
}

bool Smarticle::toggle_read_sensors(char state){
  //write to value of _transmit to enable/disable reading sensor data
  if (state==1)
  {
    _read_sensors = state;
    return 1;
  }else{
    _read_sensors=0;
    return 0;
  }
}

bool Smarticle::toggle_transmit(char state){
  //write to value of _transmit to enable/disable transmitting sensor data
  if (state==1)
  {
    _transmit = state;
    return 1;
  }else{
    _transmit=0;
    return 0;
  }
}

uint8_t Smarticle:: set_gait_epsilon(char eps){
  // interpets set epsilon command
  _gait_epsilon = eps;
  return _gait_epsilon;
}

uint8_t Smarticle::set_pose_noise(char noise_range){
  //interpret set pose noise commands
  _pose_noise = noise_range;
  return _pose_noise;
}

void Smarticle::set_plank(uint8_t state)
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

bool Smarticle::toggle_light_plank(char state){
  _light_plank = state;
  return _light_plank;
}

void Smarticle::set_pose(uint8_t angL, uint8_t angR){
  //interpret random angle commands
  if (angL == 190){
    angL = 180*random(2);
  }
  else if (angL == 200){
    angL = random(181);
  }
  if (angR == 190){
    angR = 180*random(2);
  }
  else if (angR == 200){
    angR = random(181);
  }

  if (_gait_epsilon==0){
    ServoL.write(angL-_pose_noise/2+random(_pose_noise+1));
    ServoR.write(angR-_pose_noise/2+random(_pose_noise+1));
  }
  else{
    int coinL = random(101);
    int coinR = random(101);
    if (coinL<=_gait_epsilon){
      ServoL.write(180*random(2));
    }else{
      ServoL.write(angL-_pose_noise/2+random(_pose_noise+1));
    }
    if (coinR<=_gait_epsilon){
      ServoR.write(180*random(2));
    }else{
      ServoR.write(angR-_pose_noise/2+random(_pose_noise+1));
    }
  }
}

uint16_t Smarticle::set_stream_timing_noise(uint16_t max_delay_val){
  _random_stream_delay_max=max_delay_val;
  return _random_stream_delay_max;
}

uint8_t Smarticle::set_transmit_counts(uint8_t counts){
  _transmit_counts=counts;
  return _transmit_counts;
}

uint8_t Smarticle::set_debug(uint8_t debug){
  _debug=debug;
  return _debug;
}

uint8_t Smarticle::set_id(uint8_t val){
  id=val;
  return id;
}

uint16_t Smarticle::set_sync_noise(uint16_t max_noise_val){
  _sync_noise = max_noise_val;
  return _sync_noise;
}

void Smarticle::set_light_plank_threshold(uint16_t* thresh){
  for (int ii=0; ii<SENSOR_COUNT; ii++){
    _sensor_threshold[ii] = thresh[ii];
  }
}

void Smarticle::init_gait(volatile char* msg){
  //get number of gait points
  toggle_t4_interrupt(0);
  char n = msg[VALUE_OFFSET]-ASCII_OFFSET;
  char gait_len = msg[VALUE_OFFSET+1]-ASCII_OFFSET;
  _gait_pts[n]=gait_len;
  //reconstruct 16 bit integer from two 8 bit chars to get gait delay counts for interrupt
  _t4_TOP = _convert_to_16bit(msg[VALUE_OFFSET+2]-ASCII_OFFSET, msg[VALUE_OFFSET+3]-ASCII_OFFSET);
  NeoSerial1.printf("Time Step: %d",_t4_TOP);
  _half_t4_TOP = _t4_TOP/2;
  //read each of the specificed number of gait pts and save to an array of integers
  for (int ii=0; ii<_gait_pts[n]; ii++){
    _gaitL[n][ii]=msg[GAIT_OFFSET+ii]-ASCII_OFFSET;
    _gaitR[n][ii]=msg[GAIT_OFFSET+gait_len+ii]-ASCII_OFFSET;
    if (_debug>=1){NeoSerial1.printf("Number:%d\tIndex:%d \tL:%d\tR:%d\n",n,ii,_gaitL[n][ii],_gaitR[n][ii]);}
  }
  //set compare match value to delay counts
  OCR4A = _t4_TOP;
  //resent timer counts at 0
  TCNT4 = 0;
  //resent array index back at zero to start gait sequence at the beginning
  _index = 0;
}

void Smarticle::rx_interrupt(uint8_t c){
  //runs on every received byte
  static int len=0;
  int ind =(_msg_rx)%MSG_BUFF_SIZE;
  if (c==0x11){  //if sync character 0x11
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

void Smarticle::manage_msg(void){
  // if received messages is more than read messages
  if ((_msg_rx-_msg_rd)>0){
    int ind = (_msg_rd)%MSG_BUFF_SIZE;
    _msg_rd++;
    if(_debug>=2){NeoSerial1.printf("msg!>>");}
    //ensure message matches command structure of leading with a colon ':'
    // typical message structure example '':M:0' set to mode 0
    if (_input_msg[ind][0]==0x13 && _input_msg[ind][1]==0x13){
      _interp_msg(_input_msg[ind]);
    }else if (_debug >=2){
      NeoSerial1.printf("DEBUG: wrong format >>");
      NeoSerial1.printf("%s",_input_msg[ind]);
    }
  }
}

uint16_t * Smarticle::read_sensors(void){
  if (_read_sensors ==1){
    unsigned long startTime= millis();  // Start of sample window
    // initialize sensor reading
    sensor_dat[0] = analogRead(PRF);
    sensor_dat[1] = analogRead(PRB);
    sensor_dat[2] = analogRead(PRR);
    sensor_dat[3] = analogRead(STRESS);
    //get moving average over sample time
    while(millis() - startTime < _sample_time_ms) {
        sensor_dat[0] = (sensor_dat[0]+analogRead(PRF))/2;
        sensor_dat[1] = (sensor_dat[1]+analogRead(PRB))/2;
        sensor_dat[2] = (sensor_dat[2]+analogRead(PRR))/2;
        sensor_dat[3] = (sensor_dat[3]+analogRead(STRESS))/2;
      }
    if (_light_plank==1 && _mode==INTERP){
      bool trigger = (sensor_dat[0]>=_sensor_threshold[0]||
                     sensor_dat[1]>=_sensor_threshold[1]||
                     sensor_dat[2]>=_sensor_threshold[2]||
                     sensor_dat[3]>=_sensor_threshold[3]);
      if (_plank == 0 && trigger){
        toggle_plank(1);
        NeoSerial1.printf("PLANK 1\n");
      }else if (_plank == 1 && !trigger){
        toggle_plank(0);
        NeoSerial1.printf("PLANK 0\n");
      }
    }
  return sensor_dat;
  }
}

void Smarticle::transmit_data(void){
  //send data: sensor_dat[0]= photo_front, sensor_dat[1]= photo_back, sensor_dat[2]= photo_right, sensor_dat[3]= current sense
  static uint16_t count = 0;
  if (_transmit ==1){
    count++;

    if (count >= _transmit_counts){
      NeoSerial1.printf("%d,%d,%d,%d\n",sensor_dat[0], sensor_dat[1], sensor_dat[2],sensor_dat[3]);
      count = 0;
    }

  }
}

void Smarticle::interp_stream_cmd(volatile char* msg){

  if (_mode==STREAM){
    uint8_t msg_len = msg[VALUE_OFFSET]-ASCII_OFFSET;
    for(int ii=VALUE_OFFSET+1; ii<(3*msg_len+VALUE_OFFSET+1); ii=ii+3){
      uint8_t val = msg[ii]-ASCII_OFFSET;
      if (val==0||val==id){
        uint8_t angL = msg[ii+1]-ASCII_OFFSET;
        uint8_t angR = msg[ii+2]-ASCII_OFFSET;
        set_pose(angL, angR);
        if (_debug>0){
          NeoSerial1.printf("DEBUG: stream pose L:%d, R:%d",angL,angR);
        }
        break;
      }
    }
    
  }
}

void Smarticle::interp_plank_cmd(volatile char* msg){

  uint8_t msg_len = msg[VALUE_OFFSET]-ASCII_OFFSET;
  for(int ii=VALUE_OFFSET+1; ii<(2*msg_len+VALUE_OFFSET+1); ii=ii+2){
    uint8_t val = msg[ii]-ASCII_OFFSET;
    if (val==0||val==id){
      uint8_t state = msg[ii+1]-ASCII_OFFSET;
      set_plank(state);
      if (_debug>0){
        NeoSerial1.printf("DEBUG: set plank: %d",state);
      }
      break;
    }
  }
}

void Smarticle::t4_interrupt(void){
  if (_mode==INTERP){
        _gait_interpolate(_gait_pts[_gait_num], _gaitL[_gait_num], _gaitR[_gait_num]);
  }
}

uint16_t Smarticle::_convert_to_16bit(char val_7bit_1, char val_7bit_2){
  //reconstruct 14 bit integer from two 7 bit chars to get gait delay counts for interrupt
  uint16_t out= ((val_7bit_1<<7)|(val_7bit_2&0x7f))&0x3fff;
  return out;
}

void Smarticle::_interp_msg(volatile char* msg){
  if(_debug>=2){NeoSerial1.printf("%s\n>>",msg);}
  //determine which command to exectue
  char msg_code = msg[2];

  if ((msg_code >= 0x20) && (msg_code < 0x30)){
    char value1 = msg[VALUE_OFFSET]-ASCII_OFFSET;
    int ret;
    switch (msg_code) {
      case 0x20:
        // toggle LED
        ret = toggle_led(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: toggle LED: %d\n",ret);}
        break;

      case 0x21:
        // select mode
        ret = set_mode(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set mode: %d\n",ret);}
        break;
      case 0x22:
        // toggle t4 interrupt
        ret = toggle_t4_interrupt(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: toggle t4 interrupt: %d\n", ret);}
        break;
      case 0x23:
        // set transmit counts
        ret = set_transmit_counts(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set transmit counts: %d\n",ret);}
        break;
      case 0x24:
        // select gait
        ret = select_gait(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: select gait: %d\n", ret);}
        break;
      case 0x25:
        // toggle read sensors
        ret = toggle_read_sensors(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: toggle read sensors: %d\n",ret);}
        break;
      case 0x26:
        // toggle transmit
        ret = toggle_transmit(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: toggle transmit sensor values: %d\n",ret);}
        break;
      case 0x27:
        // set gait epsilon
        ret = set_gait_epsilon(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set gait epsilon: %d\n",ret);}
        break;
      case 0x28:
        // set pose noise
        ret = set_pose_noise(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set pose noise: %d\n",ret);}
        break;
      case 0x29:
        // toggle light plank
        ret = toggle_light_plank(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: toggle light plank: %d\n",ret);}
        break;
      case 0x2A:
        // set debug
        ret = set_debug(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set debug: %d\n",ret);}
        break;
      case 0x2B:
        // set id
        ret = set_id(value1);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set id: %d\n",ret);}
        break;
    }
  } else if ((msg_code >= 0x30) && (msg_code <= 0x34)){
    uint8_t value1 = msg[VALUE_OFFSET]-ASCII_OFFSET;
    uint8_t value2 = msg[1+VALUE_OFFSET]-ASCII_OFFSET;
    int ret;
    uint16_t in;
    switch (msg_code) {
      case 0x30:
        // set pose
        set_pose(value1, value2);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set pose: (%d,%d)\n", value1, value2);}
        break;
      case 0x31:
        // set sync noise
        in = _convert_to_16bit(value1, value2);
        ret = set_sync_noise(in);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set sync noise: %d\n",ret);}
        break;
      case 0x32:
        // set stream timing noise
        in = _convert_to_16bit(value1, value2);
        ret = set_stream_timing_noise(in);
        if(_debug>=1){NeoSerial1.printf("DEBUG: set streaming timing noise: %d\n",ret);}
        break;

    }
  } else if (msg_code>=0x40){
      switch (msg_code) {
        case 0x40:
          uint16_t thresh[SENSOR_COUNT], val;
          for(int ii=0; ii<SENSOR_COUNT; ii++){
            val = _convert_to_16bit(msg[VALUE_OFFSET+ii], msg[VALUE_OFFSET+ii+1]);
            thresh[ii]=val;
          }
          set_light_plank_threshold(thresh);
          break;
        case 0x41:
          init_gait(msg);
          break;
        case 0x42:
          // stream command
          interp_stream_cmd(msg);
          break;
        case 0x43:
          interp_plank_cmd(msg);
          break;
      }
  } else {
    if(_debug>=1){
      NeoSerial1.printf("DEBUG: no match :(\n");
    }
  }
}

void Smarticle::_gait_interpolate(int len, uint8_t *servoL_arr, uint8_t *servoR_arr){
    //move servos to next position specified in gait array
    if (_plank ==0){
      set_pose(servoL_arr[_index%len],servoR_arr[(_index)%len]);
    }
    _index++;
}
