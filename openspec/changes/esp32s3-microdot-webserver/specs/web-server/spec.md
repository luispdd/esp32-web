## Purpose

Provides an asynchronous HTTP server on the ESP32-S3 that serves static web assets and REST API endpoints, accessible locally via standard network hostname resolution.

## ADDED Requirements

### Requirement: Device connects to Wi-Fi with local hostname
The system SHALL connect to the configured Wi-Fi network and register the hostname `miniweb` to enable local network access via `http://miniweb.local`.

#### Scenario: Successful network connection
- **WHEN** the board boots with valid Wi-Fi credentials in `settings/secrets.py`
- **THEN** it connects to the local access point and obtains an IP address with hostname `miniweb`

#### Scenario: Missing or invalid credentials
- **WHEN** `settings/secrets.py` is missing or contains default placeholders
- **THEN** the system logs an error without crashing and retries connection on configured intervals

### Requirement: Server serves static files
The system SHALL serve static files including HTML, CSS, and JavaScript from the `static/` directory over HTTP port 80.

#### Scenario: Client requests root path
- **WHEN** an HTTP GET request is received for `/`
- **THEN** the server responds with HTTP 200 and the contents of `static/index.html`

#### Scenario: Client requests static asset
- **WHEN** an HTTP GET request is received for `/static/css/style.css`
- **THEN** the server responds with HTTP 200 and the corresponding stylesheet file

#### Scenario: Client requests non-existent file
- **WHEN** an HTTP GET request is received for an unmapped route or missing file
- **THEN** the server responds with HTTP 404 Not Found

### Requirement: Server provides system status API
The system SHALL expose an endpoint at `GET /api/status` returning a JSON payload with device telemetry and operating status.

#### Scenario: Successful status query
- **WHEN** an HTTP GET request is received for `/api/status`
- **THEN** the server responds with HTTP 200 and a JSON object containing `status`, `device_id`, `uptime_s`, `free_heap`, `ip`, and `rssi`
