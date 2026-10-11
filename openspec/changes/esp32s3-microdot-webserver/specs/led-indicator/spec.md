## Purpose

Controls the onboard WS2812 addressable RGB LED to provide clear visual feedback for system boot, network readiness, and incoming HTTP request activity.

## ADDED Requirements

### Requirement: Boot state LED indication
The system SHALL illuminate the onboard WS2812 RGB LED on GPIO 38 in solid green during system initialization and Wi-Fi connection, and turn it off once the web server is ready.

#### Scenario: Device booting and connecting
- **WHEN** the device powers on and initiates boot and Wi-Fi connection
- **THEN** the onboard RGB LED is illuminated green

#### Scenario: Server ready and listening
- **WHEN** the Wi-Fi connection is established and the web server starts listening for connections
- **THEN** the onboard RGB LED is turned off

### Requirement: HTTP request activity pulse
The system SHALL pulse the onboard WS2812 RGB LED in blue for approximately 100 milliseconds upon receiving any incoming HTTP request without blocking the HTTP response.

#### Scenario: HTTP request received
- **WHEN** any HTTP request arrives at the web server
- **THEN** the RGB LED turns blue immediately and turns off after 100 milliseconds in a non-blocking background task
