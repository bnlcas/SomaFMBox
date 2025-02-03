#include <Encoder.h>

// Example: Rotary Encoder connected to pins 2 and 3
Encoder channelEncoder(5, 6);
Encoder volumeEncoder(7,8);


// Define pin assignments for potentiometer, toggle, and reset button
const int onOffSwitchPin = 2;
const int scannerSwitchPin = 4;  // large switch for police scanner
const int resetButtonPin = 3;    // reset button

// Variables to store state
long lastEncoderPos = 0;
long lastVolumePos = 0;
bool lastOnOffState = HIGH;
bool lastScannerState = HIGH;  // assume using internal pull-up so default is HIGH
bool lastResetState = HIGH;

void setup() {
  Serial.begin(9600);
  
  // Setup digital pins
  pinMode(onOffSwitchPin, INPUT_PULLUP);
  pinMode(scannerSwitchPin, INPUT_PULLUP);
  pinMode(resetButtonPin, INPUT_PULLUP);
}

void loop() {
  // --- Rotary Encoder for channel selection ---
  long newEncoderPos = channelEncoder.read();
  if (newEncoderPos != lastEncoderPos) {
    lastEncoderPos = newEncoderPos;
    // Convert the encoder count to a channel index (for example, channel = encoder count modulo number of channels)
    int channel = (int)(newEncoderPos % 24);  // assume 10 channels for instance
    if (channel < 0) channel += 16;
    Serial.print("CHANNEL:");
    Serial.println(channel);
    delay(100);  // small delay to avoid flooding messages
  }

  long newVolumeneEncoderPos = volumeEncoder.read();
  if (newVolumeneEncoderPos != lastVolumePos) {
    lastVolumePos = newVolumeneEncoderPos;
    // Convert the encoder count to a channel index (for example, channel = encoder count modulo number of channels)
    int volume = (int)(newVolumeneEncoderPos % 16);  // assume 10 channels for instance
    if (volume < 0) volume += 16;
    Serial.print("VOLUME:");
    Serial.println(volume);
    delay(100);  // small delay to avoid flooding messages
  }
  
  // --- Potentiometer for volume control ---
  /*
  int potValue = analogRead(potPin);
  // Map the analog value (0-1023) to a volume percentage (say 0-100)
  int volume = map(potValue, 0, 1023, 0, 100);
  // Only send update if there’s a significant change
  if (abs(volume - lastPotValue) > 2) {  // adjust threshold as needed
    lastPotValue = volume;
    Serial.print("VOLUME:");
    Serial.println(volume);
    delay(50);
  }*/
  bool onState = digitalRead(onOffSwitchPin);
  //Serial.println(onState);
  if (onState != lastOnOffState) {
    lastOnOffState = onState;
    if (onState == LOW) {  // pressed
      Serial.println("ON");
    } else{
      Serial.println("OFF");

    }
      delay(100); // simple debounce delay

  }
  
  // --- Scanner Switch (police scanner) ---
  bool scannerState = digitalRead(scannerSwitchPin);
  if (scannerState != lastScannerState) {
    lastScannerState = scannerState;
    if (scannerState == LOW) {  // assuming LOW when switched on
      Serial.println("SCANNER_ON");
    } else {
      // When switch is turned off, you may want to revert to the previous stream/channel
      Serial.println("SCANNER_OFF");
    }
    delay(100);
  }
  
  // --- Reset Button ---
  bool resetState = digitalRead(resetButtonPin);
  if (resetState != lastResetState) {
    lastResetState = resetState;
          Serial.println("RESET");

    if (resetState == LOW) {  // pressed
      Serial.println("RESET");
      delay(500); // simple debounce delay
    }
  }

  
  
  // Add additional sensors/controls as desired...
}
