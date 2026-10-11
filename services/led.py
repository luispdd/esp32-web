"""LED Service for Waveshare ESP32-S3-DEV-KIT-N16R8-M.

Controls the onboard WS2812 RGB LED (NeoPixel) on GPIO 38:
- Booting: Solid Green
- Idle/Ready: Off
- Incoming HTTP Request: Non-blocking Blue pulse (~100ms)
"""

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    import config
except ImportError:
    from settings import config

# Color Definitions (R, G, B) - Using brightness of 32 (safe & visible)
COLOR_GREEN = (0, 32, 0)
COLOR_BLUE = (0, 0, 32)
COLOR_OFF = (0, 0, 0)

_pixel = None
_pulse_active = False

try:
    import machine
    import neopixel
    _pin = machine.Pin(getattr(config, "PIN_RGB_LED", 38))
    _pixel = neopixel.NeoPixel(_pin, 1)
except Exception as e:
    # Allows module to import in simulation/host testing environments
    _pixel = None


def set_color(r, g, b):
    """Sets the RGB LED to a specific color."""
    global _pixel
    if _pixel is not None:
        try:
            _pixel[0] = (r, g, b)
            _pixel.write()
        except Exception:
            pass


def set_boot_color():
    """Sets the LED to green during boot / Wi-Fi connection."""
    set_color(*COLOR_GREEN)


def set_idle():
    """Turns the LED off when ready and idle."""
    set_color(*COLOR_OFF)


async def blink_blue(duration_ms=100):
    """Asynchronous pulse that turns the LED blue for duration_ms then off."""
    global _pulse_active
    _pulse_active = True
    try:
        set_color(*COLOR_BLUE)
        await asyncio.sleep_ms(duration_ms)
    finally:
        set_color(*COLOR_OFF)
        _pulse_active = False


def trigger_blue_pulse(duration_ms=100):
    """Spawns a fire-and-forget background task to pulse blue on request."""
    try:
        asyncio.create_task(blink_blue(duration_ms))
    except Exception:
        # Fallback if event loop is not yet running
        pass
