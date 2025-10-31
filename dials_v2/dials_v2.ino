//#include <Encoder.h>
#include <ESP32Encoder.h>

// Example: Rotary Encoder connected to pins 2 and 3
const int volumeHighPin = A0;
const int encoderHighPin = A8;

//Encoder channelEncoder(5, 6);
ESP32Encoder channelEncoder;
const int channelEncoderSteps = 24;
int lastEncoderPos = -1;


const int volumePotentiometerPin = A1;
const int volumeEncoderSteps = 16;
const int volumeStepSize = 4096 / volumeEncoderSteps;
int lastVolumeMeasure = 100000;

void setup() {
  Serial.begin(9600);
  
  // Setup digital pins
  pinMode(volumePotentiometerPin, INPUT);
  pinMode(volumeHighPin,OUTPUT);
  pinMode(encoderHighPin, OUTPUT);

  //ESP32Encoder::useInternalWeakPullResistors = UP; // use internal pullups
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  channelEncoder.attachHalfQuad(5, 6);
  channelEncoder.clearCount();

}

void loop() {
  // --- Rotary Encoder for channel selection ---
  digitalWrite(encoderHighPin, HIGH);
  digitalWrite(volumeHighPin, HIGH);
  //digitalWrite(volumeGroundPin, LOW);


  
  int newEncoderPos = channelEncoder.getCount();//channelEncoder.read();
  if (newEncoderPos != lastEncoderPos) {
    lastEncoderPos = newEncoderPos;
    // Convert the encoder count to a channel index (for example, channel = encoder count modulo number of channels)
    int channel = ((int)(newEncoderPos)) % channelEncoderSteps;

    if (channel < 0) channel += channelEncoderSteps;
    Serial.print("CHANNEL:");
    Serial.println(channel);
    delay(200);  // small delay to avoid flooding messages
  }

  int volumeLevel = analogRead(volumePotentiometerPin);



  if (abs(volumeLevel - lastVolumeMeasure) >  volumeStepSize){

    lastVolumeMeasure = volumeLevel;
    int volume = 100 - volumeLevel / 41;//clamp to 0-100 out of 4096
    Serial.print("VOLUME:");
    Serial.println(volume);
    delay(200);  // small delay to avoid flooding messages
  }
}
