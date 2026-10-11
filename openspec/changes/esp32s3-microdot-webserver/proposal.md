## Why

Establish a lightweight, fully asynchronous web server on the Waveshare ESP32-S3-DEV-KIT-N16R8-M development board using Microdot and MicroPython's `uasyncio`. The device must connect to local Wi-Fi, be addressable as `miniweb.local`, serve static web pages and a REST API status endpoint, and provide visual feedback via its onboard addressable RGB LED.

## What Changes

- Update `settings/config.py` pin definitions for Waveshare ESP32-S3-DEV-KIT-N16R8-M (correct onboard WS2812 LED pin from GPIO 8 to GPIO 38, define local hostname `miniweb`).
- Structure the project keeping only `main.py` in the root directory and modular code in dedicated subdirectories (`services/`, `settings/`, `static/`, `lib/`).
- Implement an asynchronous Wi-Fi manager (`services/wifi.py`) that connects to Wi-Fi and configures DHCP/mDNS hostname `miniweb`.
- Implement an asynchronous WS2812 LED controller (`services/led.py`) that illuminates green during boot, turns off when ready, and blinks blue for ~100ms non-blocking upon receiving HTTP requests.
- Implement static asset serving from `static/` (serving `index.html`, `css/style.css`, `js/app.js`).
- Implement a REST API endpoint `GET /api/status` returning JSON with system health, uptime, free heap memory, IP address, and Wi-Fi RSSI.
- Provide `main.py` as the sole root entrypoint running the `uasyncio` event loop and Microdot app.

## Capabilities

### New Capabilities
- `web-server`: Asynchronous HTTP web server serving static assets and REST API endpoints, accessible locally via `miniweb.local`.
- `led-indicator`: Hardware status and activity signaling via the onboard WS2812 RGB LED (green on boot, blue pulse on HTTP request).

### Modified Capabilities
<!-- None: This is the initial capability set for this project -->

## Impact

- **Hardware/Pin Mappings**: Corrects `PIN_RGB_LED` to GPIO 38 for ESP32-S3-DEV-KIT-N16R8-M (WS2812 NeoPixel).
- **Filesystem**: Organizes files into `services/` and `static/`, leaving only `main.py` at repository root.
- **Dependencies**: Relies on `lib/microdot.mpy` (pre-installed on board) and built-in `uasyncio`, `machine`, `neopixel`, and `network` modules.
