## ADDED Requirements

### Requirement: Data Sources Management Page
The frontend SHALL provide a dedicated page for managing data sources at `/data-sources`.

#### Scenario: Data sources list view
- **WHEN** user navigates to data sources page
- **THEN** system displays table of all data sources with key information

#### Scenario: Data source details view
- **WHEN** user selects a data source from the list
- **THEN** system shows detailed information including connection config and status

### Requirement: Data Source CRUD Operations
The frontend SHALL support creating, reading, updating, and deleting data sources through the UI.

#### Scenario: Create data source form
- **WHEN** user clicks "Add Data Source" button
- **THEN** system displays form with fields for name, type, description, and connection config

#### Scenario: Edit data source form
- **WHEN** user clicks edit on a data source
- **THEN** system displays pre-populated form for updating the data source

#### Scenario: Delete data source confirmation
- **WHEN** user clicks delete on a data source
- **THEN** system shows confirmation dialog with impact information

### Requirement: Connection Validation UI
The frontend SHALL provide connection testing functionality in the data sources interface.

#### Scenario: Validation button
- **WHEN** user views data source details
- **THEN** validation button is available to test the connection

#### Scenario: Validation result display
- **WHEN** user runs validation
- **THEN** system shows success/failure message with details

### Requirement: Status Indicators
The frontend SHALL display visual status indicators for data source health and sync status.

#### Scenario: Active/inactive status
- **WHEN** data source has is_active status
- **THEN** visual indicator shows active (green) or inactive (gray) state

#### Scenario: Sync status indicator
- **WHEN** data source has sync information
- **THEN** indicator shows last sync time and status (current/stale/error)

### Requirement: Data Source Filtering Integration
The frontend SHALL integrate data source filtering into the assets management interface.

#### Scenario: Data source filter in assets page
- **WHEN** user views assets page
- **THEN** data source dropdown is available for filtering

#### Scenario: Filter persistence
- **WHEN** user applies data source filter
- **THEN** filter selection is maintained during navigation</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/specs/data-sources-frontend/spec.md