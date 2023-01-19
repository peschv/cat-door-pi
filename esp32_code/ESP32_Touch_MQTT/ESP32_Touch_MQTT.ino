/*
 * Optional ESP32 Component
 * Date: Oct 11 2022
 * Author: Vanessa Pesch
 * 
 * Description:
 * Sends message to MQTT broker when touch pin on Adafruit QT Py ESP32-S2 is activated.
 * In this program, two capacitive touch pins are used:
 *    A2(GPIO9) - publishes "OUT" message
 *    SCL(GPIO6) - publishes "IN" message
 * When these pins are touched, the NeoPixel LED briefly turns on, board connects to WiFi
 * then to a public MQTT broker, and publishes relevant message to broker. When message is 
 * successfully sent, NeoPixel LED displays a rainbow sequence.
 * Available touch pins on the QT Py ESP32-S2: A2(GPIO9), A3(GPIO8), SDA(GPIO7), SCL(GPIO6), TX(GPIO5)
 *   
 * Neopixel code adapted from: https://learn.adafruit.com/adafruit-qt-py/neopixel-blink
 * MQTT broker code adapted from: https://www.emqx.com/en/blog/esp32-connects-to-the-free-public-mqtt-broker
*/
#include <Adafruit_NeoPixel.h> //NeoPixel library for LED
#include <WiFi.h>
#include <PubSubClient.h>

//Wifi
const char *ssid = "Your WiFi Name";
const char *password = "yourwifipassword";
//MQTT Broker
const char *mqtt_broker = "broker.emqx.io";
const char *topic = "esp32/catmessage";
const char *mqtt_username = "emqx";
const char *mqtt_password = "public";
const int mqtt_port = 1883;
int touch9_base; //Base value of touch pin GPIO9 
int touch6_base; //Base value of touch pin GPIO6

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

Adafruit_NeoPixel pixels(1, PIN_NEOPIXEL); //Create pixel

void setup() {
  Serial.begin(115200);
  pixels.begin(); //Initialize pixel
  touch9_base = touchRead(9) + 5000; //Create base (i.e. untouched) value for pin GPIO9
  touch6_base = touchRead(6) + 5000; //Create base value for pin GPIO6
}

/*
 * When GPIO pins are touched, connect to broker, publish message to broker,
 * and display rainbow sequence of colors to signal successful delivery.
 */
void loop() {
  if (touchRead(9) > touch9_base) { //For GPIO9 (A2), publish "OUT" message
    connectToBroker();
    mqttClient.publish(topic, "OUT");
    rainbow(); 
  } else if (touchRead(6) > touch6_base) { //For GPIO6 (SCL), publish "IN" message
    connectToBroker(); 
    mqttClient.publish(topic, "IN"); 
    rainbow(); 
  }
}

//Create rainbow sequence for single on-board LED
void rainbow() {
  pixels.setBrightness(125);
  pixels.setPixelColor(0, pixels.Color(255, 0, 0)); //Red
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(230, 125, 0)); //Orange
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(255, 255, 0)); //Yellow
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(0, 255, 0)); //Green
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(0, 0, 255)); //Blue
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(0, 255, 255)); //Indigo
  pixels.show();
  delay(350);
  pixels.setPixelColor(0, pixels.Color(80, 0, 80)); //Violet
  pixels.show();
  delay(350);
  pixels.clear(); //Turn off LED
  pixels.show();
}

//Connect to public MQTT broker
void connectToBroker() {
  
  //Briefly turn on LED to notify user the message is being processed
  pixels.setPixelColor(0, pixels.Color(37, 162, 83)); //Green
  pixels.show();
  delay(500);
  pixels.clear(); //Turn off LED
  pixels.show();

  //Connect to WiFi
  WiFi.begin(ssid, password);
  for (int i = 0; WiFi.status() != WL_CONNECTED && i < 100; i++) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi network!");
  mqttClient.setServer(mqtt_broker, mqtt_port);

  //Connect to public broker
  while (!mqttClient.connected()) {
    String client_id = String(WiFi.macAddress());

    if (mqttClient.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Connected to Public MQTT broker");
    } else {
      Serial.print("Failed to connect to broker");
      Serial.print(mqttClient.state());
      delay(2000);
    }
  }
}
