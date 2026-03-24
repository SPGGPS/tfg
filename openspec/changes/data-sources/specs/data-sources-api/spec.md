## ADDED Requirements

### Requirement: Data Sources API Endpoints
The system SHALL provide REST API endpoints for complete CRUD operations on data sources at `/v1/data-sources`.

#### Scenario: List data sources
- **WHEN** client sends GET request to `/v1/data-sources`
- **THEN** system returns paginated list of all data sources with their details

#### Scenario: Get specific data source
- **WHEN** client sends GET request to `/v1/data-sources/{id}`
- **THEN** system returns the data source details for the specified ID

#### Scenario: Create new data source
- **WHEN** client sends POST request to `/v1/data-sources` with valid data source data
- **THEN** system creates the data source and returns its details with 201 status

#### Scenario: Update existing data source
- **WHEN** client sends PUT request to `/v1/data-sources/{id}` with valid update data
- **THEN** system updates the data source and returns the updated details

#### Scenario: Delete data source
- **WHEN** client sends DELETE request to `/v1/data-sources/{id}`
- **THEN** system deletes the data source and returns 204 status

### Requirement: Data Source Response Format
The API SHALL return data sources in a consistent JSON format including id, name, type, description, connection_config, is_active, last_sync, sync_interval_minutes, priority, created_at, and updated_at fields.

#### Scenario: Standard response structure
- **WHEN** client requests data source information
- **THEN** response includes all required fields in the specified format

### Requirement: Data Source Input Validation
The API SHALL validate input data for data source creation and updates, ensuring required fields are present and data types are correct.

#### Scenario: Invalid data source creation
- **WHEN** client sends POST with missing required fields
- **THEN** system returns 422 status with validation error details

#### Scenario: Duplicate name validation
- **WHEN** client attempts to create data source with existing name
- **THEN** system returns 409 status with conflict error</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/specs/data-sources-api/spec.md