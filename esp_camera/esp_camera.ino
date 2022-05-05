/*
 * File: Web Server Code
 * Date: 11/1/2021
 * Author: Rakan AlZagha & Arduino ESP32 Example Fragments
 * 
 * Purpose: Generate a web server with live stream
 */

#include "esp_camera.h"
#include "camera_pins.h"
#include "button_and_led_pins.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h" //disable brownout problems
#include "soc/rtc_cntl_reg.h"  //disable brownout problems
#include "esp_http_server.h"
#include <ezButton.h>

#define PART_BOUNDARY "123456789000000000000987654321"

// network credentials
const char* ssid = "ESP32";
const char* password = "Raal2112!";

// create a new button on programmed pin #15
ezButton button(15);

// set the necessary details for the HTTP server API
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";
httpd_handle_t stream_httpd = NULL;


// Set your Static IP address
IPAddress local_IP(192, 168, 137, 184);
// Set your Gateway IP address
IPAddress gateway(192, 168, 137, 1);
IPAddress subnet(255, 255, 0, 0);
IPAddress primaryDNS(8, 8, 8, 8); //optional
IPAddress secondaryDNS(8, 8, 4, 4); //optional

/*
 * Set up the web server and supporting components
 * 
 */
void setup() {
  serialSetup();
  camera_config_t config = cameraConfig(config);
  pinSetup();
  
  // initialize camera
  esp_err_t err = esp_camera_init(&config);
  sensor_t *s = cameraSensorConfig();

  // error-checking 
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  // Wi-Fi connection
  wifiAndButtonSetup();
  serialPrint();

  // set debounce time to 50 milliseconds
  button.setDebounceTime(DEBOUNCE_TIME); 
}

/*
 * Provide start-up features for program
 * 
 */
 
void loop() {
  button.loop();
  // toggle white LED when function button is pressed
  if(button.isPressed()){
    digitalWrite(LED_BUILTIN, HIGH);
    startCameraServer();
  } 
  delay(1);
}

/*
 * Set up the serial debug output
 * 
 */
 
void serialSetup(){
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
}

/*
 * Set up the pin config for the ESP-EYE
 * 
 */
 
void pinSetup(){
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

/*
 * Set up the WiFi and button start up
 * 
 */
 
void wifiAndButtonSetup(){
  // Wi-Fi connection
  if(!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_PIN, HIGH);
    Serial.print(".");
    delay(500);
  }
  digitalWrite(LED_PIN, LOW);  
}

/*
 * Serial monitor print messages
 * 
 */
 
void serialPrint(){
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("Camera Stream Ready! Go to: http://");
  Serial.print(WiFi.localIP());
}

/*
 * Set up the stream handler for active camera stream
 * 
 * ADAPTED from ESP32 Documentation Examples
 * 
 */
 
static esp_err_t stream_handler(httpd_req_t *request){
  camera_fb_t * frame_buffer = NULL;
  esp_err_t response = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

  // set http response type
  response = httpd_resp_set_type(request, _STREAM_CONTENT_TYPE);
  if(response != ESP_OK){
    return response;
  }

  while(true){
    // get frame by frame
    frame_buffer = esp_camera_fb_get();
    // no frames in buffer
    if (!frame_buffer) {
      Serial.println("Camera capture failed");
      response = ESP_FAIL;
    } 
    // frames captured
    else {
      if(frame_buffer->width > 400){
        if(frame_buffer->format != PIXFORMAT_JPEG){
          // convert frame to mJPEG
          bool jpeg_converted = frame2jpg(frame_buffer, 80, &_jpg_buf, &_jpg_buf_len);
          esp_camera_fb_return(frame_buffer);
          frame_buffer = NULL;
          if(!jpeg_converted){
            Serial.println("JPEG compression failed");
            response = ESP_FAIL;
          }
        } 
        else {
          _jpg_buf_len = frame_buffer->len;
          _jpg_buf = frame_buffer->buf;
        }
      }
    }
    //  send requests as reponses if ESP_OK
    if(response == ESP_OK){
      size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, _jpg_buf_len);
      response = httpd_resp_send_chunk(request, (const char *)part_buf, hlen);
    }
    if(response == ESP_OK){
      response = httpd_resp_send_chunk(request, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if(response == ESP_OK){
      response = httpd_resp_send_chunk(request, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }
    if(frame_buffer){
      esp_camera_fb_return(frame_buffer);
      frame_buffer = NULL;
      _jpg_buf = NULL;
    } 
    else if(_jpg_buf){
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if(response != ESP_OK){
      break;
    }
  }
  return response;
}

/*
 * Set up the the basics of the server to extract mJPEGs
 * 
 */
 
void startCameraServer(){
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t http_request = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  Serial.println("");
  Serial.printf("The web server is starting on default port: '%d'\n", config.server_port);
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &http_request);
  }
  else{
    Serial.printf("The web server is failing to start on default port: '%d'\n", config.server_port);
  }
}