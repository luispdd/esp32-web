# ESP32-S3 MiniWeb

An asynchronous, lightweight embedded web server and real-time telemetry dashboard designed for the **Waveshare ESP32-S3-DEV-KIT-N16R8-M** running **MicroPython** and **Microdot**.

---

## Features

- **Asynchronous Architecture**: Powered by MicroPython's `uasyncio` and [Microdot](https://microdot.readthedocs.io/), running a non-blocking event loop.
- **Modern Responsive Dashboard**: Serves a sleek, dark-themed dashboard (`index.html`, `style.css`, `app.js`) with glassmorphic cards, live polling, and latency tracking.
- **REST Telemetry API**: Exposes `GET /api/status` returning real-time device stats (uptime, free/allocated heap memory, IP address, and Wi-Fi RSSI).
- **Onboard WS2812 RGB LED Feedback**:
  - **Solid Green**: Device booting and connecting to Wi-Fi.
  - **Off / Idle**: Connected and ready for requests.
  - **Blue Pulse (~100ms)**: Fire-and-forget non-blocking visual indicator on incoming HTTP requests.
- **Local Network Discovery**: Registers hostname `miniweb` via DHCP / mDNS, allowing access via `http://miniweb.local` or direct IP.
- **Modular Directory Layout**: Root directory kept clean with only `main.py`; modules structured cleanly in `services/`, `settings/`, `static/`, and `lib/`.
- **Safe Secrets Management**: Wi-Fi credentials isolated in `settings/secrets.py` (ignored by git) via `secrets.py.example`.

---

## Hardware Specifications

- **Target Board**: Waveshare ESP32-S3-DEV-KIT-N16R8-M (16MB Flash, 8MB Octal PSRAM)
- **RGB LED**: Onboard WS2812 NeoPixel mapped to **GPIO 38**
- **Default Port**: HTTP Port 80
- **Default Hostname**: `miniweb.local`

---

## Project Structure

```text
esp32-web/
├── main.py                  # Main entrypoint: initializes hardware, Wi-Fi, and Microdot server
├── settings/
│   ├── __init__.py
│   ├── config.py            # Pin definitions, network settings, and path configuration
│   ├── secrets.py.example   # Template for Wi-Fi credentials
│   └── secrets.py           # Untracked credentials file (created by user)
├── services/
│   ├── __init__.py
│   ├── led.py               # Asynchronous WS2812 RGB NeoPixel driver & pulse handler
│   ├── wifi.py              # Asynchronous Wi-Fi connection manager & hostname config
│   └── web.py               # Microdot web controller: routing, telemetry API, static files
├── static/
│   ├── index.html           # Single-page dashboard HTML
│   ├── css/
│   │   └── style.css        # Dashboard styling (dark theme, glassmorphism, responsive)
│   └── js/
│       └── app.js           # Client-side heartbeat polling and LED ping controller
├── lib/                     # Third-party libraries (e.g. microdot.mpy)
└── README.md
```

---

## Getting Started

### 1. Prerequisites

- **MicroPython Firmware**: Flashed onto your ESP32-S3 (e.g. ESP32-S3 firmware with SPIRAM support).
- **Microdot Library**: Ensure `microdot.py` or compiled `microdot.mpy` is installed on your board's `/lib` directory or root `lib/`. You can install it via mip:
  ```bash
  mpremote mip install microdot
  ```
- **Deployment Tool**: [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), [rshell](https://github.com/dhylands/rshell), [ampy](https://github.com/scientifichackers/ampy), or an IDE such as VS Code (MicroPico) or Thonny.

### 2. Configure Wi-Fi Credentials

Copy the example secrets file and edit it with your Wi-Fi details:

```bash
cp settings/secrets.py.example settings/secrets.py
```

Edit `settings/secrets.py`:

```python
WIFI_SSID = "Your_WiFi_Network"
WIFI_PASSWORD = "Your_WiFi_Password"
DEVICE_ID = "esp32s3"
DEVICE_TYPE = "esp32s3"
```

> **Note**: `settings/secrets.py` should be kept private and not committed to public repositories.

### 3. Upload Files to the ESP32-S3

Using `mpremote`:

```bash
# Upload project directories and main entrypoint
mpremote fs cp -r settings/ :settings/
mpremote fs cp -r services/ :services/
mpremote fs cp -r static/ :static/
mpremote fs cp main.py :main.py
```

### 4. Run the Application

Execute directly on the board:

```bash
mpremote run main.py
# Or reset the board:
mpremote reset
```

---

## Usage

### Web Dashboard

Once connected, find the IP address from serial output or navigate to:

```text
http://miniweb.local
```
*(or `http://<device-ip>` if your network router doesn't resolve mDNS)*

The dashboard provides:
- Live status indicators.
- Memory telemetry (Free Heap vs Allocated Heap).
- Uptime counter and Wi-Fi RSSI signal strength.
- An interactive **"Send Ping / Pulse LED"** button that measures round-trip latency and flashes the onboard RGB LED blue.

### REST API

#### `GET /api/status`

Returns system telemetry in JSON format.

**Example Request:**
```bash
curl http://miniweb.local/api/status
```

**Example Response:**
```json
{
  "status": "online",
  "device_id": "esp32s3",
  "device_type": "esp32s3",
  "hostname": "miniweb",
  "ip": "192.168.1.120",
  "rssi": -58,
  "uptime_s": 42,
  "free_heap": 4125820,
  "allocated_heap": 68912
}
```

---

## LED Status Indicator Reference

| State | Color | Behavior | Description |
| :--- | :--- | :--- | :--- |
| **Booting / Connecting** | Green | Solid | Connecting to configured Wi-Fi network |
| **Ready / Idle** | Off | - | Connected, server listening for requests |
| **HTTP Request** | Blue | Pulse (~100ms) | Triggered non-blocking in `before_request` hook |

---

## Local Simulation & Host Testing

`main.py` and service modules include fallback mocks for host environments:
```bash
python3 main.py
```
This enables basic syntax and import checks without requiring attached hardware.
