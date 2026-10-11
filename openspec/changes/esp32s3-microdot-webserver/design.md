## Context

See `proposal.md` for background and motivation. The project runs on MicroPython on a Waveshare ESP32-S3-DEV-KIT-N16R8-M. The pre-installed `lib/microdot.mpy` library serves as the web framework. The repository previously had pin definitions from an ESP32-C6-Zero that must be adjusted for the ESP32-S3 board.

## Goals / Non-Goals

**Goals:**
- Maintain an asynchronous, non-blocking execution model using `uasyncio`.
- Enforce the root directory rule: only `main.py` resides at the workspace root; other modules reside in `services/`, `settings/`, `static/`, or `lib/`.
- Provide non-blocking visual feedback on the onboard WS2812 RGB LED (GPIO 38): solid green while booting/connecting, off when idle, blue pulse on HTTP request.
- Serve static web files (`index.html`, `style.css`, `app.js`) and dynamic JSON API endpoints (`/api/status`).
- Enable local network discovery through DHCP/mDNS hostname `miniweb`.

**Non-Goals:**
- Implementing authentication or user sessions at this phase.
- Sensor polling or peripheral actuation beyond the onboard WS2812 LED.
- HTTPS/TLS termination (handled over plain HTTP on port 80 for local testing).

## Decisions

### 1. Directory Structure & Path Resolution
- **Decision:** Place all helper modules in `services/` (`wifi.py`, `led.py`), configuration in `settings/`, static assets in `static/`, and web library in `lib/`. Only `main.py` sits at root.
- **Rationale:** Ensures clean code organization without root clutter. `settings/config.py` updates `sys.path` to include `services`, `settings`, and `lib` so cross-imports resolve cleanly.
- **Alternatives Considered:** Flat root structure (placing `wifi.py`, `led.py` in root). Rejected due to explicit requirement to keep only `main.py` at root.

### 2. Microdot Async Integration
- **Decision:** Run Microdot natively inside the `uasyncio` event loop using async route handlers and `app.start_server(port=80)`.
- **Rationale:** Microdot v2 is built for asyncio. Running `app.start_server()` allows other asynchronous coroutines (e.g. background LED timers, Wi-Fi health watchdogs) to run concurrently without blocking request processing.
- **Alternatives Considered:** Synchronous `app.run()`. Rejected because it blocks background async tasks and makes responsive LED control cumbersome.

### 3. WS2812 LED Driver & Non-blocking Request Pulse
- **Decision:** Drive the onboard WS2812 LED on GPIO 38 using MicroPython's built-in `neopixel` module. Use `asyncio.create_task()` in Microdot's `before_request` hook to trigger a 100ms blue pulse `(0, 0, 32)` without delaying HTTP responses.
- **Rationale:** The LED is an addressable NeoPixel, not a standard GPIO; `neopixel.NeoPixel(Pin(38), 1)` is required. Fire-and-forget task execution ensures request response times remain unaffected.
- **Alternatives Considered:** Awaiting the LED delay inside the route handler. Rejected because it would add 100ms artificial latency to every HTTP response.

### 4. Local Hostname Resolution
- **Decision:** Call `wlan.config(dhcp_hostname=HOSTNAME)` and `network.hostname(HOSTNAME)` during Wi-Fi activation.
- **Rationale:** Most modern home routers automatically populate local DNS / mDNS records from DHCP hostname requests, making the device reachable at `miniweb.local` without requiring heavy external mDNS libraries.
- **Alternatives Considered:** Full Python-based mDNS multicast responder. Kept as optional fallback if DHCP hostname does not resolve on specific router configurations.

### 5. Static File & Status API Design
- **Decision:** Serve `static/index.html` at `GET /`, and static assets under `GET /static/<path:path>` using `send_file`. Implement `GET /api/status` returning `status`, `device_id`, `uptime_s`, `free_heap`, `ip`, and `rssi`.
- **Rationale:** Clean separation between static web presentation and JSON telemetry.

## Risks / Trade-offs

- **[Risk] MicroPython heap memory fragmentation from repeated file serving** → Mitigation: Use streaming/chunked responses where applicable and run `gc.collect()` periodically or in request hooks.
- **[Risk] Home router does not register DHCP hostname for `.local`** → Mitigation: Print IP address explicitly to serial output on boot so the device can always be reached via direct IP as a fallback.
- **[Risk] Rapid HTTP requests causing concurrent LED tasks** → Mitigation: Use a simple boolean flag or lock in the LED controller so new requests refresh the pulse timer rather than piling up competing write loops.
