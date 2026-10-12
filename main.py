"""Main application entrypoint for Waveshare ESP32-S3-DEV-KIT-N16R8-M.

Bootstraps hardware services, connects to Wi-Fi, and starts the asynchronous
web server.
"""

import sys

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
    from services import led, wifi, web
except ImportError:
    import led, wifi, web


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

    await web.start_server(host="0.0.0.0", port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Main] Stopped by keyboard interrupt.")
        led.set_idle()

