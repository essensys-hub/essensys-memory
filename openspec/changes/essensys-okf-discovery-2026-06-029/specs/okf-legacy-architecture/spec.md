# okf-legacy-architecture

## ADDED Requirements

### Requirement: Armoire architecture knowledge

The OKF base MUST contain a dedicated architecture view of the ESSENSYS armoire and its embedded boards.

#### Scenario: Armoire boards are represented

- **GIVEN** the discovery covers firmware and board repositories
- **WHEN** OKF generation completes
- **THEN** the OKF base includes concepts for SC944D, SC940, SC941C, SC942C, SC945D, SC946D, SC947-xB, SC840, SC841, and SC843D where sources exist
- **AND** it identifies the role of each board in the armoire architecture
- **AND** it links board concepts to the platform overview and protocol concepts

#### Scenario: Architecture synthesis exists

- **GIVEN** board and firmware concepts have been generated
- **WHEN** synthesis generation completes
- **THEN** `okf/synthesis/` contains an armoire architecture overview describing master board, actuator boards, screen/IHM, alarm/siren, DFE, benches, and server/gateway interactions

### Requirement: Table d'échange contract

The OKF base MUST document the table d'échange as a compatibility contract across firmware, screen, server backend, cloud portal, and user interfaces.

#### Scenario: Critical indices are documented

- **GIVEN** the discovery reads existing wiki and protocol sources
- **WHEN** the table d'échange OKF concept is generated
- **THEN** it documents indices 590, 591-919, 605-622, 409-411, and 566-589
- **AND** it describes scenarios, lights, shutters, alarm, shutter travel times, OR bitwise merge, and action expansion rules
- **AND** it cites source wiki/code pointers including `TableEchange.h`, `IHM_ECHANGES.INC`, Go constants, and cloud order expansion when available

#### Scenario: Contradictions are not hidden

- **GIVEN** firmware, backend, frontend, or cloud sources disagree on an index or semantic
- **WHEN** the discovery detects the contradiction
- **THEN** the OKF concept records the contradiction with both sources cited
- **AND** the coverage report lists it as a follow-up item

### Requirement: Legacy HTTP protocol contract

The OKF base MUST document the legacy HTTP port/protocol contract as frozen compatibility knowledge.

#### Scenario: Legacy endpoints are documented as frozen

- **GIVEN** the discovery covers legacy client and backend sources
- **WHEN** the legacy HTTP OKF concept is generated
- **THEN** it documents `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, and `/api/done/{guid}`
- **AND** it marks these endpoints as compatibility-critical and not to be modernized without explicit firmware regression work

#### Scenario: Wire quirks are documented

- **GIVEN** legacy protocol behavior is described in wiki or source code
- **WHEN** the legacy HTTP OKF concept is generated
- **THEN** it records JSON normalization, historical `Content-Type`, Basic Auth, AES alarm payloads, single-packet TCP response requirement, `_de67f` ordering, and `/api/myactions` to `/api/done/{guid}` flow
