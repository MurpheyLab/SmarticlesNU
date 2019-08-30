#include <Smarticle.h>


Smarticle smart(1);

void setup() {
  smart.Xbee.attachInterrupt(handleRxChar);
  smart.Xbee.begin(9600);
  smart.set_led(1);
  delay(3000);
  smart.set_led(0);
}

void loop() {
 smart.read_sensors();
 smart.transmit_data();
 if (smart.msg_flag==1){
    smart.interp_msg();
  }
}


ISR(TIMER4_COMPA_vect){
  smart.t4_interrupt();
}

static void handleRxChar( uint8_t c)
{
  smart.rx_interrupt(c);
}
