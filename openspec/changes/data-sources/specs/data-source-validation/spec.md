## ADDED Requirements

### Requirement: Data Source Validation Endpoint
The system SHALL provide a validation endpoint at `/v1/data-sources/{id}/validate` to test data source connections.

#### Scenario: Validate API data source
- **WHEN** client sends POST request to `/v1/data-sources/{id}/validate` for an API type data source
- **THEN** system attempts to connect to the configured URL and returns validation result

#### Scenario: Validate database data source
- **WHEN** client sends POST request to `/v1/data-sources/{id}/validate` for a database type data source
- **THEN** system attempts to connect using the connection string and returns validation result

#### Scenario: Validation success response
- **WHEN** data source connection test succeeds
- **THEN** system returns success status with connection details

#### Scenario: Validation failure response
- **WHEN** data source connection test fails
- **THEN** system returns failure status with error message and details

### Requirement: Validation Result Format
The validation endpoint SHALL return a consistent JSON response with success status, message, and optional error details.

#### Scenario: Successful validation format
- **WHEN** validation succeeds
- **THEN** response includes success: true, message, and timestamp

#### Scenario: Failed validation format
- **WHEN** validation fails
- **THEN** response includes success: false, message, error details, and timestamp

### Requirement: Validation Without Persistence
The validation endpoint SHALL NOT modify the data source record or update sync status.

#### Scenario: Validation is read-only
- **WHEN** client calls validation endpoint
- **THEN** data source record remains unchanged in database</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/specs/data-source-validation/spec.md