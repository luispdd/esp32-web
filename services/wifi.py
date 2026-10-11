"""Wi-Fi Service for ESP32.

Handles asynchronous station-mode connection, hostname assignment (miniweb),
and connection telemetry.
"""

import time
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    import config
except ImportError:
    from settings import config

_wlan = None


def get_wlan():
    """Returns the WLAN Station interface singleton."""
    global _wlan
    if _wlan is None:
        try:
            import network
            _wlan = network.WLAN(network.STA_IF)
        except Exception:
            _wlan = None
    return _wlan


def configure_hostname():
    """Sets the device hostname on the network interface."""
    hostname = getattr(config, "HOSTNAME", "miniweb")
    try:
        import network
        if hasattr(network, "hostname"):
            network.hostname(hostname)
    except Exception:
        pass

    wlan = get_wlan()
    if wlan is not None:
        for opt in ("dhcp_hostname", "hostname"):
            try:
                wlan.config(**{opt: hostname})
                break
            except Exception:
                continue


def is_connected():
    """Returns True if the Wi-Fi station is connected."""
    wlan = get_wlan()
    if wlan is not None:
        try:
            return wlan.isconnected()
        except Exception:
            return False
    return False


def get_ip():
    """Returns current IP address or '0.0.0.0'."""
    wlan = get_wlan()
    if wlan is not None and is_connected():
        try:
            return wlan.ifconfig()[0]
        except Exception:
            return "0.0.0.0"
    return "0.0.0.0"


def get_rssi():
    """Returns signal strength in dBm or None if unavailable."""
    wlan = get_wlan()
    if wlan is not None and is_connected():
        try:
            return wlan.status("rssi")
        except Exception:
            return None
    return None


async def connect(timeout_s=15):
    """Asynchronously connects to Wi-Fi station using config credentials."""
    if is_connected():
        return True

    if not config.has_valid_credentials():
        print("[WiFi] Credential error:", config.WIFI_CONFIG_ERROR)
        return False

    wlan = get_wlan()
    if wlan is None:
        print("[WiFi] Network module unavailable in this environment")
        return False

    try:
        wlan.active(True)
        configure_hostname()
        print("[WiFi] Connecting to '{}'...".format(config.WIFI_SSID))
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    except Exception as e:
        print("[WiFi] Connect exception:", e)
        return False

    timeout_ms = timeout_s * 1000
    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            print("[WiFi] Connection timed out after {}s".format(timeout_s))
            return False
        await asyncio.sleep_ms(250)

    ip_info = wlan.ifconfig()
    print("[WiFi] Connected! IP: {}, Hostname: {}.local".format(ip_info[0], getattr(config, "HOSTNAME", "miniweb")))
    return True
