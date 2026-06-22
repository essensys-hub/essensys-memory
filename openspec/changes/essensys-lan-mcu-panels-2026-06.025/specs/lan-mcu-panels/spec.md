# lan-mcu-panels

## ADDED Requirements

### Requirement: LAN-only MCU panels

The system SHALL allow ESP32 and Raspberry Pi Pico W devices to act as physical button panels that trigger scenarios and heating actions exclusively over the local network (`*.local` or private IP), with no WAN-accessible endpoints for MCU control.

#### Scenario: Button triggers scenario on LAN

- **WHEN** a enrolled MCU panel sends a valid button press to the gateway at `https://mon.essensys.local`
- **AND** the button is mapped to scenario ID `S`
- **THEN** the gateway launches scenario `S` using the same semantics as the local UI
- **AND** the request is rejected if the client source IP is not on the LAN

#### Scenario: Button triggers heating action

- **WHEN** a enrolled MCU panel sends a button press mapped to a predefined heating action
- **THEN** the gateway writes the corresponding heating indices to the exchange table
- **AND** the action is limited to predefined modes documented in the admin UI (not full weekly planner editing)

#### Scenario: WAN request blocked

- **WHEN** an MCU or client attempts MCU panel API from a non-private IP or via the public cloud hostname
- **THEN** the gateway returns HTTP 403
- **AND** no scenario or heating state changes

### Requirement: Trusted device enrollment

MCU panels SHALL be enrolled using the trusted devices capability from change **2026-06.013** before any button press is accepted.

#### Scenario: Unenrolled panel rejected

- **WHEN** a device presents an unknown or revoked device token
- **THEN** button press requests are rejected with HTTP 401

#### Scenario: Admin enrolls new panel

- **WHEN** an administrator completes the « Add MCU panel » flow in the local dashboard
- **THEN** a device credential is issued and can be provisioned into ESP32/Pico firmware
- **AND** the panel appears in the trusted device registry

### Requirement: Button mapping configuration

The local dashboard SHALL allow mapping each physical button index on a panel to either a scenario launch or a predefined heating action.

#### Scenario: Configure four-button panel

- **WHEN** an administrator assigns button 1 to scenario « Soirée » and button 2 to heating action « Boost 1h »
- **THEN** subsequent presses invoke only those mappings
- **AND** unmapped buttons produce no side effect (or optional LED error feedback in firmware)

### Requirement: Reference firmware

The project SHALL provide reference firmware for ESP32 and Pico W implementing debounced GPIO input, HTTPS to the gateway `.local` hostname, and secure storage of the device token.

#### Scenario: Flash reference ESP32 firmware

- **WHEN** an installer flashes the reference PlatformIO project with provisioned gateway host and token
- **THEN** the device can register button presses against the enrolled panel ID without cloud connectivity
