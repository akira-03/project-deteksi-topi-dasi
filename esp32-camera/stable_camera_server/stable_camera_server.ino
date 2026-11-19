#include "esp_camera.h"
#include "esp_http_server.h"
#include <WiFi.h>

const char* WIFI_SSID = "FAZ NET";
const char* WIFI_PASSWORD = "GANTI_PASSWORD_WIFI";

#define PWDN_GPIO_NUM   -1
#define RESET_GPIO_NUM  -1
#define XCLK_GPIO_NUM   5
#define Y9_GPIO_NUM     4
#define Y8_GPIO_NUM     6
#define Y7_GPIO_NUM     7
#define Y6_GPIO_NUM     14
#define Y5_GPIO_NUM     17
#define Y4_GPIO_NUM     21
#define Y3_GPIO_NUM     18
#define Y2_GPIO_NUM     16
#define VSYNC_GPIO_NUM  1
#define HREF_GPIO_NUM   2
#define PCLK_GPIO_NUM   15
#define SIOD_GPIO_NUM   8
#define SIOC_GPIO_NUM   9

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

static httpd_handle_t httpd = NULL;

static esp_err_t index_handler(httpd_req_t* req) {
  const char* html =
    "<!doctype html><html><body>"
    "<h2>ESP32 Camera Ready</h2>"
    "<p><a href='/capture'>Capture</a></p>"
    "<p><img src='/stream' style='max-width:100%;height:auto'></p>"
    "</body></html>";
  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, html, strlen(html));
}

static esp_err_t capture_handler(httpd_req_t* req) {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("ERR: esp_camera_fb_get failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  esp_err_t res = httpd_resp_send(req, (const char*)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

static esp_err_t stream_handler(httpd_req_t* req) {
  httpd_resp_set_type(req, STREAM_TYPE);
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");

  while (true) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("ERR: stream capture failed");
      return ESP_FAIL;
    }

    char header[64];
    int header_len = snprintf(header, sizeof(header), STREAM_PART, fb->len);

    esp_err_t res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
    if (res == ESP_OK) res = httpd_resp_send_chunk(req, header, header_len);
    if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);

    esp_camera_fb_return(fb);

    if (res != ESP_OK) {
      break;
    }
    delay(80);
  }

  return ESP_OK;
}

static esp_err_t control_handler(httpd_req_t* req) {
  char query[96];
  char var[24];
  char val[24];

  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK ||
      httpd_query_key_value(query, "var", var, sizeof(var)) != ESP_OK ||
      httpd_query_key_value(query, "val", val, sizeof(val)) != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Bad request");
    return ESP_FAIL;
  }

  sensor_t* s = esp_camera_sensor_get();
  int value = atoi(val);
  int res = 0;

  if (!strcmp(var, "framesize")) res = s->set_framesize(s, (framesize_t)value);
  else if (!strcmp(var, "quality")) res = s->set_quality(s, value);
  else if (!strcmp(var, "brightness")) res = s->set_brightness(s, value);
  else if (!strcmp(var, "contrast")) res = s->set_contrast(s, value);
  else if (!strcmp(var, "saturation")) res = s->set_saturation(s, value);
  else if (!strcmp(var, "vflip")) res = s->set_vflip(s, value);
  else if (!strcmp(var, "hmirror")) res = s->set_hmirror(s, value);
  else {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Unknown variable");
    return ESP_FAIL;
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  if (res) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  return httpd_resp_sendstr(req, "OK");
}

void startServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  // Port 8080 avoids networks that block device-to-device HTTP on port 80.
  config.server_port = 8080;
  config.max_uri_handlers = 8;
  config.stack_size = 8192;

  httpd_uri_t index_uri = { .uri = "/", .method = HTTP_GET, .handler = index_handler, .user_ctx = NULL };
  httpd_uri_t capture_uri = { .uri = "/capture", .method = HTTP_GET, .handler = capture_handler, .user_ctx = NULL };
  httpd_uri_t stream_uri = { .uri = "/stream", .method = HTTP_GET, .handler = stream_handler, .user_ctx = NULL };
  httpd_uri_t control_uri = { .uri = "/control", .method = HTTP_GET, .handler = control_handler, .user_ctx = NULL };

  if (httpd_start(&httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(httpd, &index_uri);
    httpd_register_uri_handler(httpd, &capture_uri);
    httpd_register_uri_handler(httpd, &stream_uri);
    httpd_register_uri_handler(httpd, &control_uri);
  }
}

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 8;
  // Two PSRAM framebuffers let /stream and /capture run at the same time.
  // This is required for live preview plus continuous YOLO detection.
  if (psramFound()) {
    config.fb_count = 2;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    Serial.println("WARNING: PSRAM tidak ditemukan; realtime deteksi tidak optimal.");
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    while (true) delay(1000);
  }

  sensor_t* s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_SVGA);
  s->set_quality(s, 8);
  Serial.println("Camera init OK");
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println();
  Serial.println("Booting stable ESP32 camera server");

  setupCamera();

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());

  startServer();
  Serial.println("Endpoints: /capture /stream /control");
}

void loop() {
  delay(10000);
}
