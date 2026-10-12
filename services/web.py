"""Web Controller & HTTP Server Service for ESP32.

Manages the Microdot asynchronous web application, routes, static asset serving,
telemetry API endpoints, and request lifecycle hooks.
"""

import gc
import json
import sys
import time

# Ensure search paths include local directories
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


# Initialize Microdot application instance
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


async def start_server(host="0.0.0.0", port=80):
    """Starts the asynchronous Microdot web server."""
    await app.start_server(host=host, port=port)
