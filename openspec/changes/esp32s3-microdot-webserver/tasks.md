## 1. Configuration & Project Structure

- [x] 1.1 Update `settings/config.py` with `PIN_RGB_LED = 38` for Waveshare ESP32-S3-DEV-KIT-N16R8-M, define `HOSTNAME = "miniweb"`, add `services` to `sys.path`, and verify syntax.
- [x] 1.2 Create the required directory structure (`services/`, `static/`, `static/css/`, `static/js/`) ensuring no helper files are placed at repository root.

## 2. Core Services

- [x] 2.1 Implement `services/led.py` providing an asynchronous WS2812 LED controller on GPIO 38 with `set_boot_color()` (green), `set_idle()` (off), and non-blocking `blink_blue()` pulse.
- [x] 2.2 Implement `services/wifi.py` with asynchronous connection logic, hostname assignment (`miniweb`), and connection status helpers.

## 3. Static Web Assets

- [x] 3.1 Create `static/index.html` with a modern UI layout, live system status card, and connection test buttons.
- [x] 3.2 Create `static/css/style.css` styling the dashboard with a sleek dark theme, responsive grid, and status badges.
- [x] 3.3 Create `static/js/app.js` with client-side JavaScript to periodically poll `GET /api/status` and update the UI in real time.

## 4. Server Application & Entrypoint

- [x] 4.1 Implement `main.py` as the sole root entrypoint, integrating Microdot async routes (`/`, `/static/<path:path>`, `/api/status`), the request hook for LED blue pulses, and the `uasyncio` main loop.
- [x] 4.2 Verify file placement (confirm only `main.py` resides at root) and validate that all Python files compile cleanly.
