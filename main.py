"""Main application entrypoint for Waveshare ESP32-S3-DEV-KIT-N16R8-M.

Asynchronous web server using Microdot and uasyncio:
- Serves static web assets from static/
- Exposes GET /api/status telemetry endpoint
- Controls WS2812 RGB LED (Green during boot, Blue pulse on request)
- Configures local network discovery via miniweb.local
"""

import gc
import sys
import time

# Ensure subdirectories are in search path before importing project modules
for _dir in ("/settings", "settings", "./settings", "/services", "services", "./services", "/lib", "lib", "./lib"):
    if _dir not in sys.path:
        sys.path.append(_dir)

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    import config
except ImportError:
    from settings import config

try:
    from services import led, wifi
except ImportError:
    import led, wifi

try:
    from microdot import Microdot, Response, send_file
except ImportError:
    # Minimal fallback mock for testing/compilation in host environments
    class Microdot:
        def __init__(self):
            pass
        def route(self, *args, **kwargs):
            return lambda f: f
        def before_request(self, f):
            return f
        async def start_server(self, host="0.0.0.0", port=80):
            while True:
                await asyncio.sleep(3600)
    class Response:
        default_content_type = "text/html"
        def __init__(self, body="", headers=None, status_code=200):
            self.body = body
            self.headers = headers or {}
            self.status_code = status_code
    def send_file(path):
        return Response("Mock file: " + path)

app = Microdot()
Response.default_content_type = "text/html"


@app.before_request
async def on_incoming_request(request):
    """Triggers non-blocking blue pulse on onboard WS2812 RGB LED."""
    led.trigger_blue_pulse()


@app.route("/")
async def serve_index(request):
    """Serves the main dashboard page."""
    return send_file("static/index.html")


@app.route("/static/<path:path>")
async def serve_static(request, path):
    """Serves static files (CSS, JS, images)."""
    return send_file("static/" + path)


@app.route("/api/status")
async def api_status(request):
    """Returns JSON system status and telemetry."""
    try:
        gc.collect()
    except Exception:
        pass

    uptime_s = time.ticks_ms() // 1000 if hasattr(time, "ticks_ms") else int(time.time())
    free_heap = gc.mem_free() if hasattr(gc, "mem_free") else 0
    alloc_heap = gc.mem_alloc() if hasattr(gc, "mem_alloc") else 0

    import json
    payload = json.dumps({
        "status": "online",
        "device_id": getattr(config, "DEVICE_ID", "esp32s3"),
        "device_type": getattr(config, "DEVICE_TYPE", "esp32s3"),
        "hostname": getattr(config, "HOSTNAME", "miniweb"),
        "ip": wifi.get_ip(),
        "rssi": wifi.get_rssi(),
        "uptime_s": uptime_s,
        "free_heap": free_heap,
        "allocated_heap": alloc_heap
    })

    return Response(body=payload, headers={"Content-Type": "application/json"})


async def main():
    """Initializes hardware, connects Wi-Fi, and starts the async web server."""
    print("[Main] Initializing ESP32-S3 MiniWeb...")
    led.set_boot_color()

    # Asynchronous Wi-Fi connection
    connected = await wifi.connect(timeout_s=15)
    if connected:
        print("[Main] Wi-Fi online at IP: {}".format(wifi.get_ip()))
    else:
        print("[Main] Wi-Fi connection pending or failed. Continuing boot...")

    # Ready state: turn off boot LED
    led.set_idle()

    port = getattr(config, "HTTP_PORT", 80)
    hostname = getattr(config, "HOSTNAME", "miniweb")
    print("[Main] Starting Microdot server on port {}...".format(port))
    print("[Main] Accessible at http://{}.local or http://{}".format(hostname, wifi.get_ip()))

    await app.start_server(host="0.0.0.0", port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Main] Stopped by keyboard interrupt.")
        led.set_idle()
