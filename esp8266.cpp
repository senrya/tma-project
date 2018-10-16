#include <ESP8266WiFi.h>        // Wi-Fi library
#include <PubSubClient.h>		//Client
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <stdlib.h>

const char *ssid			= "AndroidWifi";         // The SSID of the Wi-Fi network
const char *password		= "123456789";			 // The password of the Wi-Fi network
const char *mqtt_server		= "broker.bevywise.com"; // Server broker bevywise
const int   mqtt_port		= 1883;
const char *mqtt_user		= "ZJysbSfNUo7lCMXGMT";
const char *mqtt_pass		= "sInKAYetaBFATb8UqS";
const char *mqtt_client_name= "SmartHome";

String curTime;
unsigned long curTimeMillis;
unsigned long setupMillis;
unsigned long periodTime;
unsigned long periodMillis;
unsigned long alarmTime;
int signalAlarm = 0;

WiFiUDP u;
NTPClient n(u, "vn.pool.ntp.org", 7 * 3600);
WiFiClient espClient;
PubSubClient client(espClient);

void setup();
void subscribe();
void reconnect();
void uploadState();
void callback(char* topic, byte* payload, unsigned int length);
void alarm();
void checkTimeAlarm();

void setup() {
	pinMode(D0, OUTPUT);
	pinMode(D1, OUTPUT);
	pinMode(D2, OUTPUT);
	pinMode(D3, OUTPUT);
	pinMode(D4, OUTPUT);
/*  digitalWrite(D0, LOW);
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW); */
	Serial.begin(9600);
	delay(200);
	client.setServer(mqtt_server, mqtt_port);
	client.setCallback(callback);
}
void subscribe() {
	client.subscribe("/LED/LED0");
	client.subscribe("/LED/LED1");
	client.subscribe("/LED/LED2");
	client.subscribe("/LED/LED3");
	client.subscribe("/LED/LED4");
	client.subscribe("/ALARM/TIME");
    client.subscribe("/ALARM/STATE");
}
void reconnect() {
	Serial.println('\n');
	WiFi.begin(ssid, password); // Connect to the network
	Serial.print("Connecting to ");
	Serial.print(ssid); Serial.println(" ...");
	while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
		Serial.print('.');
        delay(1000);
	}
	Serial.println('\n');
	Serial.println("Connection established!");
	Serial.print("IP address:\t");
	Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer
	//Connect to client
	while (!client.connected()) {
		if (client.connect(mqtt_client_name, mqtt_user, mqtt_pass)) {
			subscribe();
		}
		else {
			delay(5000);
		}
	}
	Serial.println("Client Connected");
	client.publish("/SETUP/WiFi&Client", "ON");
	n.update();
	delay(200);
	Serial.print("Time : ");
	Serial.println(n.getFormattedTime());
	Serial.print("Epoch time : ");
	Serial.println(n.getEpochTime());
}

void callback(char* topic, byte* payload, unsigned int length) {
	Serial.print(topic);
	char temp[40];
	memset(temp, 0, 40);
	memcpy(temp, payload, length);
	Serial.print(" /Payload : ");
	Serial.println(temp);
	if (strcmp(topic, "/LED/LED0") == 0) {//State LED0
		if (strcmp(temp, "ON") == 0) {
			digitalWrite(D0, HIGH);
		}
        else if (strcmp(temp, "OFF") == 0) {
			    digitalWrite(D0, LOW);
		}
	}
    else if (strcmp(topic, "/LED/LED1") == 0) {//State LED1
		if (strcmp(temp, "ON") == 0) {
			digitalWrite(D1, HIGH);
		}
        else if (strcmp(temp, "OFF") == 0) {
			    digitalWrite(D1, LOW);
        }
	}
    else if (strcmp(topic, "/LED/LED2") == 0) {//State LED2
		if (strcmp(temp, "ON") == 0) {
			digitalWrite(D2, HIGH);
		}
        else if (strcmp(temp, "OFF") == 0) {
			    digitalWrite(D2, LOW);
        }
	}
    else if (strcmp(topic, "/LED/LED3") == 0) {//State LED3
		if (strcmp(temp, "ON") == 0) {
			digitalWrite(D3, HIGH);
		}
        else if (strcmp(temp, "OFF") == 0) {
			    digitalWrite(D3, LOW);
        }
	}
    else if (strcmp(topic, "/LED/LED4") == 0) {//State LED4
		if (strcmp(temp, "ON") == 0) {
			digitalWrite(D4, HIGH);
		}
        else if (strcmp(temp, "OFF") == 0) {
			    digitalWrite(D4, LOW);
        }
	}
	else if (strcmp(topic, "/ALARM/TIME") == 0) {
		fgets(temp, 40, stdin);
		periodTime = atoll(temp) - n.getEpochTime(); // PeriodTime to setup alarm (second)
		delay(300);
        Serial.print("Wait until the alarm : ");
		Serial.print(periodTime);
        Serial.println(" second.");
		setupMillis = millis();
		signalAlarm = 1;
	}
}

void uploadState() {
	delay(5000);
	if (digitalRead(D0)) {
		client.publish("/LED/LED0", "ON");
    }
	else {
		client.publish("/LED/LED0", "OFF");
    }
    if (digitalRead(D1)) {
		client.publish("/LED/LED1", "ON");
    }
	else {
		client.publish("/LED/LED1", "OFF");
    }
    if (digitalRead(D2)) {
		client.publish("/LED/LED2", "ON");
    }
	else {
		client.publish("/LED/LED2", "OFF");
    }
    if (digitalRead(D3)) {
		client.publish("/LED/LED3", "ON");
    }
	else {
		client.publish("/LED/LED3", "OFF");
    }
    if (digitalRead(D4)) {
		client.publish("/LED/LED4", "ON");
    }
	else {
		client.publish("/LED/LED4", "OFF");
    }

	
}
void alarm() {
    delay(alarmTime-100);
    client.publish("/ALARM/STATE", "ON");
    Serial.println("bao thuc");
    signalAlarm = 0;
}

void checkTimeAlarm() {
    periodMillis = (millis() - setupMillis); // convert to second (millisecond)
	alarmTime = periodTime * 1000 - periodMillis;
	if (alarmTime > 10000) {
        delay(5000);
    } 
    else if ((alarmTime < 10000) && (alarmTime > 1000)) {   // 10s 
		delay(1000);Serial.println(alarmTime);
	}
	else if (alarmTime < 1500) { // 1.5s
        alarm();
    }

}
void loop() {
	if (!client.connected()) {
		reconnect();
    }
    if (signalAlarm)
        checkTimeAlarm();
	//uploadState();
	client.loop();
}