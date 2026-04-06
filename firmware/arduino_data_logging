#include <Wire.h>
#include <Adafruit_ADS1X15.h>
// ===== ADC OBJECT =====
Adafruit_ADS1115 ads;
// ===== GLOBAL CONSTANTS =====
const float VDD = 3.3;              // Supply voltage
const float ADC_GAIN = 0.256;       // ADS1115 full-scale for GAIN_SIXTEEN
const int ADC_RESOLUTION = 32768;   // 16-bit signed
// Sensor parameters (from datasheet)
const float SENSITIVITY = 0.002;    // α = 2 mV/V/N = 0.002 V/V/N
// Offset (beta)
float beta = 0.0;
// ===== SETUP =====
void setup() {
   Serial.begin(115200);
   Wire.begin();
   if (!ads.begin()) {
       Serial.println("ADC not found!");
       while (1);
   }
   // Increase gain for small signals
   ads.setGain(GAIN_SIXTEEN);  // ±0.256V
   delay(1000);  // allow system to stabilise
   calibrateZero();  // measure offset
}
// ===== READ DIFFERENTIAL VOLTAGE =====
float readDifferentialVoltage() {
   int16_t raw = ads.readADC_Differential_0_1();
   float voltage = (raw * ADC_GAIN) / ADC_RESOLUTION;
   return voltage;  // in volts
}
// ===== VOLTAGE → FORCE (datasheet model) =====
float voltageToForce(float v_out) {
   float normalized = v_out / VDD;              // remove Vdd scaling
   float force = (normalized - beta) / SENSITIVITY;
   return force;
}
// ===== ZERO CALIBRATION =====
void calibrateZero() {
   Serial.println("Calibrating offset (no load)...");
   float sum = 0;
   int samples = 200;
   for (int i = 0; i < samples; i++) {
       sum += readDifferentialVoltage();
       delay(5);
   }
   float avg_voltage = sum / samples;
   beta = avg_voltage / VDD;  // convert to normalized offset
   Serial.print("Beta (offset): ");
   Serial.println(beta, 6);
}
// ===== GET FORCE (WITH FILTERING) =====
float getForce() {
   const int N = 10;  // averaging window
   float sum = 0;
   for (int i = 0; i < N; i++) {
       float v = readDifferentialVoltage();
       sum += voltageToForce(v);
   }
   return sum / N;
}
// ===== MAIN LOOP =====
void loop() {
   float force = getForce();
   Serial.print("Force (N): ");
   Serial.println(-force, 4);
   delay(200);
}
