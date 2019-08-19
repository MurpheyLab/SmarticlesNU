#include <Smarticle.h>

#define CYCLE_MS 50

Smarticle smart(1);

void setup() {
smart.led_on(1);
delay(4000);
smart.led_on(0);
smart.Xbee.attachInterrupt(handleRxChar);
smart.Xbee.begin(9600);
Serial.begin(9600);
}

void loop() {
  int t0 = millis();
  if (smart.get_mode()!=0){
    smart.read_sensors();
    smart.transmit_data();
  }
  if (smart.msg_flag==1){
    smart.interp_msg();
  }
  while (millis()-t0<CYCLE_MS){}
}


ISR(TIMER2_OVF_vect){
  smart.timer_interrupt();
}

static void handleRxChar( uint8_t c)
{
  smart.rx_interrupt(c);
}
