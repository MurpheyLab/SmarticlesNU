#include <Smarticle.h>


Smarticle smart(1);

void setup() {
  randomSeed(analogRead(A7));
  NeoSerial1.attachInterrupt(handleRxChar);
  smart.init_t4();
  smart.toggle_led(1);
  delay(3000);
  smart.toggle_led(0);
}

void loop() {
  smart.read_sensors();
  smart.transmit_data();
  smart.manage_msg();
}


ISR(TIMER4_COMPA_vect){
  smart.t4_interrupt();
}

static void handleRxChar( uint8_t c)
{
  smart.rx_interrupt(c);
}
