// nodemcu v1, esp-yadashvend
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include <TimeLib.h>
#include <ArduinoJson.h>

#include "emulatetag.h"
#include "NdefMessage.h"


#include <SPI.h>
#include <PN532_SPI.h>
#include "PN532.h"


extern "C" {
#include "user_interface.h"
}

#include "/usr/local/src/yadashvend_setting.h"

const char* clientid                = "ihavenonameyet";
const char* hellotopic              = "HELLO";
const char* yadashvend_req_topic    = "s/req/ihavenonameyet";
const char* yadashven_resp_topic    = "s/resp/ihavenonameyet";

uint8_t saleitem                    = 12;
unsigned long msgid                 = 0;
String yadashvendcmd                = "";
unsigned long yadashvendmsgid       = 0;
String tDashaddr                    = "";
String tDashval                     = "";
unsigned long payreceived           = 0;

IPAddress mqtt_server = MQTT_SERVER;
IPAddress ntp_server = NTP_SERVER;

String syslogPayload;
long lastReconnectAttempt = 0;

unsigned int localPort = 12390;
const int timeZone = 9;
time_t prevDisplay = 0;

volatile uint8_t dashvend_status = 0;
// 0 : not available
// 1 : addr requested
// 2 : addr received, nfc out, reaady
// 3 : paymnnt received


int LED_RED    = 4;
int LED_YELLOW = 0;
int LED_GREEN  = 2;

uint8_t ndefBuf[120];
NdefMessage message;
int messageSize;

uint8_t uid[3] = { 0x12, 0x34, 0x56 };

void ICACHE_RAM_ATTR callback(char* intopic, byte* inpayload, unsigned int length);

WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, callback, wifiClient);
WiFiUDP udp;
PN532_SPI pn532spi(SPI, 5);
EmulateTag nfc(pn532spi);

bool ICACHE_RAM_ATTR sendmqttMsg(const char* topictosend, String payloadtosend, bool retain = false)
{
  unsigned int msg_length = payloadtosend.length();

  byte* p = (byte*)malloc(msg_length);
  memcpy(p, (char*) payloadtosend.c_str(), msg_length);

  if (client.publish(topictosend, p, msg_length, retain))
  {
    free(p);
    client.loop();

    Serial.print("[MQTT] out topic : ");
    Serial.print(topictosend);
    Serial.print(" payload: ");
    Serial.print(payloadtosend);
    Serial.println(" published");

    return true;

  } else {
    free(p);
    client.loop();

    Serial.print("[MQTT] out topic : ");
    Serial.print(topictosend);
    Serial.print(" payload: ");
    Serial.print(payloadtosend);
    Serial.println(" publish failed");

    return false;
  }
}

void req_payment_addr()
{
  DynamicJsonBuffer jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["clientid"] = clientid;
  root["cmd"]      = "order";
  root["item"]     = saleitem;
  msgid            = millis();
  root["msgid"]    = msgid;
  String json;
  root.printTo(json);

  sendmqttMsg(yadashvend_req_topic, json, false);
  dashvend_status = 0;
}

void parseMqttMsg(String receivedpayload, String receivedtopic)
{
  char json[] = "{\"msgid\": 21212121212113763, \"cmd\": \"received\", \"addr\": \"yNBJzPnBckBrhTXd3G3nr2evim56G1kcmj\", \"val\": 0.00000002}";

  receivedpayload.toCharArray(json, 250);
  StaticJsonBuffer<250> jsonBuffer;
  JsonObject& root = jsonBuffer.parseObject(json);

  if (!root.success())
  {
    return;
  }

  if (receivedtopic == yadashven_resp_topic)
  {
    if (root.containsKey("msgid") && root.containsKey("cmd") && root.containsKey("addr") && root.containsKey("val"))
    {
      const char* temp_cmd  = root["cmd"];
      const char* temp_addr = root["addr"];
      const char* temp_val  = root["val"];

      yadashvendcmd   = temp_cmd;
      yadashvendmsgid = root["msgid"];
      tDashaddr       = temp_addr;
      tDashval        = temp_val;

      Serial.print("[MQTT] in msg : msgid: ");
      Serial.print(yadashvendmsgid);
      Serial.print(" cmd: ");
      Serial.print(yadashvendcmd);
      Serial.print(" tDash: ");
      Serial.print(tDashaddr);
      Serial.print(" val: ");
      Serial.println(tDashval);

      if (yadashvendmsgid == msgid)
      {
        Serial.println("[MQTT] msg id is equal");
        if (yadashvendcmd == "order")
        {
          Serial.println("[MQTT] out nfc addr");
          dashvend_status = 1;
        }

        if (yadashvendcmd == "received")
        {
          Serial.println("[MQTT] tDashaddr paid");
          dashvend_status = 4;
          payreceived = millis();
        }
      }
    }
  }
}

void ICACHE_RAM_ATTR callback(char* intopic, byte* inpayload, unsigned int length)
{
  String receivedtopic = intopic;
  String receivedpayload ;

  for (unsigned int i = 0; i < length; i++)
  {
    receivedpayload += (char)inpayload[i];
  }

  Serial.print("[MQTT] intopic : ");
  Serial.print(receivedtopic);
  Serial.print(" payload: ");
  Serial.println(receivedpayload);

  parseMqttMsg(receivedpayload, receivedtopic);
}

boolean reconnect()
{
  if (!client.connected())
  {
    if (client.connect(clientid))
    {
      client.subscribe(yadashven_resp_topic);
    }
    else
    {
      Serial.print("[MQTT] mqtt failed, rc=");
      Serial.println(client.state());
    }
  }

  return client.connected();
}

void ArduinoOTA_config()
{
  //OTA
  // Port defaults to 8266
  ArduinoOTA.setPort(8266);
  ArduinoOTA.setHostname("esp-dashvend");
  ArduinoOTA.setPassword(OTA_PASSWORD);
  ArduinoOTA.onStart([]()
  {
  });
  ArduinoOTA.onEnd([]()
  {
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
  {
  });
  ArduinoOTA.onError([](ota_error_t error)
  {
    //ESP.restart();
    if (error == OTA_AUTH_ERROR) abort();
    else if (error == OTA_BEGIN_ERROR) abort();
    else if (error == OTA_CONNECT_ERROR) abort();
    else if (error == OTA_RECEIVE_ERROR) abort();
    else if (error == OTA_END_ERROR) abort();
  });

  ArduinoOTA.begin();
}

/*-------- NTP code ----------*/
const int NTP_PACKET_SIZE = 48;
byte packetBuffer[NTP_PACKET_SIZE];

void sendNTPpacket(IPAddress & address)
{
  memset(packetBuffer, 0, NTP_PACKET_SIZE);
  packetBuffer[0] = 0b11100011;
  packetBuffer[1] = 0;
  packetBuffer[2] = 6;
  packetBuffer[3] = 0xEC;
  packetBuffer[12]  = 49;
  packetBuffer[13]  = 0x4E;
  packetBuffer[14]  = 49;
  packetBuffer[15]  = 52;
  udp.beginPacket(address, 123);
  udp.write(packetBuffer, NTP_PACKET_SIZE);
  udp.endPacket();
}

time_t getNtpTime()
{
  while (udp.parsePacket() > 0) ;
  sendNTPpacket(ntp_server);
  uint32_t beginWait = millis();
  while (millis() - beginWait < 2500)
  {
    int size = udp.parsePacket();
    if (size >= NTP_PACKET_SIZE)
    {
      udp.read(packetBuffer, NTP_PACKET_SIZE);
      unsigned long secsSince1900;
      secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
      secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
      secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
      secsSince1900 |= (unsigned long)packetBuffer[43];
      return secsSince1900 - 2208988800UL + timeZone * SECS_PER_HOUR + 3;
    }
  }
  return 0;
}

void printDigits(int digits)
{
  Serial.print(":");
  if (digits < 10)
    Serial.print('0');
  Serial.print(digits);
}

void digitalClockDisplay()
{
  Serial.print("[TIME] ");
  Serial.print(hour());
  printDigits(minute());
  printDigits(second());
  Serial.print(" ");
  Serial.print(day());
  Serial.print(" ");
  Serial.print(month());
  Serial.print(" ");
  Serial.println(year());
}

void wifi_connect()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println();
    Serial.print("[WIFI] Connecting to ");
    Serial.println(WIFI_SSID);

    delay(10);
    WiFi.setOutputPower(20);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    WiFi.hostname("esp-dashvend");

    int Attempt = 0;
    while (WiFi.status() != WL_CONNECTED)
    {
      Serial.print(". ");
      Serial.print(Attempt);
      delay(100);
      Attempt++;
      if (Attempt == 150)
      {
        Serial.println();
        Serial.println("[WIFI] Could not connect to WIFI, restarting...");
        Serial.flush();
        ESP.restart();
        delay(200);
      }
    }

    Serial.println();
    Serial.print("[WIFI] connected");
    Serial.print(" --> IP address: ");
    Serial.println(WiFi.localIP());

  }
}

String macToStr(const uint8_t* mac)
{
  String result;
  for (int i = 0; i < 6; ++i)
  {
    result += String(mac[i], 16);
    if (i < 5)
      result += ':';
  }
  return result;
}


void digitalWrite_led(int r, int y, int g)
{
  digitalWrite(LED_RED, r);
  digitalWrite(LED_YELLOW, y);
  digitalWrite(LED_GREEN, g);
}

void nfcemulate(String address, String amounts)
{
  Serial.println("------- Emulate Tag --------");

  String addressvalue = "http://192.168.10.10:1880/sendto?addr=";
  addressvalue += tDashaddr;
  addressvalue += "&val=";
  addressvalue += tDashval;

  message = NdefMessage();
  message.addUriRecord(addressvalue);
  //message.addUriRecord("dash:XuhHHnjLbm559kzByxtQ6gHMpjs32MHKb2?amount=0.01");
  //message.addUriRecord("http://192.168.10.10:1880/sendto?addr=xyz&val=10");
  messageSize = message.getEncodedSize();
  if (messageSize > sizeof(ndefBuf)) {
    Serial.println("ndefBuf is too small");
    while (1) { }
  }

  Serial.print("Ndef encoded message size: ");
  Serial.println(messageSize);

  message.encode(ndefBuf);
  nfc.setNdefFile(ndefBuf, messageSize);
  nfc.setUid(uid);
  nfc.init();
  nfc.emulate();
  nfc.setTagWriteable(false);

  if (nfc.writeOccured()) {
    Serial.println("\nWrite occured !");
    uint8_t* tag_buf;
    uint16_t length;

    nfc.getContent(&tag_buf, &length);
    NdefMessage msg = NdefMessage(tag_buf, length);
    msg.print();
  }
  dashvend_status = 3;
  Serial.println("------- End Emulate Tag --------");
}

void change_status()
{
  switch (dashvend_status)
  {
    case 0:
      digitalWrite_led(1, 0, 0);
      break;

    // addr received
    case 1:
      digitalWrite_led(0, 1, 0);
      dashvend_status = 2;
      break;

    case 2:
      digitalWrite_led(0, 1, 0);
      nfcemulate(tDashaddr, tDashval);
      break;

    case 4:
      digitalWrite_led(0, 0, 1);
      if ( millis() - payreceived > 2000)
      {
        req_payment_addr();
      }
      break;

    default:
      break;
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println();
  Serial.println("Starting....... ");

  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  digitalWrite(LED_RED, 1);

  wifi_connect();
  configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  // ntp update
  udp.begin(localPort);
  if (timeStatus() == timeNotSet)
  {
    //Serial.println("[NTP] get ntp time");
    setSyncProvider(getNtpTime);
    delay(500);
  }

  ArduinoOTA_config();
  reconnect();
  lastReconnectAttempt = 0;
  req_payment_addr();
}

void loop()
{
  if (now() != prevDisplay)
  {
    prevDisplay = now();
    if (timeStatus() == timeSet)
    {
      //digitalClockDisplay();
    }
    else
    {
      Serial.println("[TIME] time not set");
    }
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    if (!client.connected())
    {
      long now = millis();
      if (now - lastReconnectAttempt > 1000)
      {
        lastReconnectAttempt = now;
        if (reconnect())
        {
          lastReconnectAttempt = 0;
        }
      }
    }
    else
    {
      change_status();
      client.loop();
    }
    ArduinoOTA.handle();
  }
  else
  {
    wifi_connect();
  }
}
