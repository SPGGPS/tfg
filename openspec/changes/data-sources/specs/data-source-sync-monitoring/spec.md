## ADDED Requirements

### Requirement: Sync Status Tracking
The system SHALL track synchronization status for each data source including last_sync timestamp and sync status.

#### Scenario: Update sync status
- **WHEN** data source synchronization completes
- **THEN** system updates the last_sync timestamp

#### Scenario: Sync status in API responses
- **WHEN** client requests data source details
- **THEN** response includes current sync status and last_sync timestamp

### Requirement: Sync Status Indicators
The system SHALL provide status indicators showing whether a data source is active, inactive, or has sync issues.

#### Scenario: Active status display
- **WHEN** data source is active and recently synced
- **THEN** status indicator shows "active" with last sync time

#### Scenario: Inactive status display
- **WHEN** data source is marked inactive
- **THEN** status indicator shows "inactive"

#### Scenario: Stale sync status display
- **WHEN** data source hasn't synced within expected interval
- **THEN** status indicator shows "stale" with warning

### Requirement: Manual Sync Status Update
The system SHALL allow manual updates to sync status for administrative purposes.

#### Scenario: Manual sync status update
- **WHEN** administrator updates sync status via API
- **THEN** system records the manual update with timestamp

### Requirement: Sync Interval Configuration
The system SHALL support configurable sync intervals for each data source.

#### Scenario: Sync interval in data source config
- **WHEN** creating or updating data source
- **THEN** sync_interval_minutes can be specified

#### Scenario: Sync interval validation
- **WHEN** setting sync interval
- **THEN** value must be positive integer representing minutes</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/specs/data-source-sync-monitoring/spec.md