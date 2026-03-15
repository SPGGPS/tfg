## ADDED Requirements

### Requirement: Asset Filtering by Data Source
The system SHALL support filtering assets by data source ID in the assets API.

#### Scenario: Filter assets by data source
- **WHEN** client sends GET request to `/v1/assets` with `data_source_id` parameter
- **THEN** system returns only assets associated with the specified data source

#### Scenario: Multiple data source filtering
- **WHEN** client provides multiple data_source_id values
- **THEN** system returns assets from any of the specified data sources

### Requirement: Data Source Information in Asset Responses
The system SHALL include data source information in asset API responses.

#### Scenario: Asset response includes data source
- **WHEN** client requests asset details
- **THEN** response includes data_source object with id, name, and type

#### Scenario: Asset list includes data source summary
- **WHEN** client requests asset list
- **THEN** each asset includes basic data source information

### Requirement: Backward Compatibility with Source Field
The system SHALL maintain the legacy source field for backward compatibility while supporting the new data_source relationship.

#### Scenario: Legacy source field preserved
- **WHEN** asset has legacy source value
- **THEN** source field remains available in API responses

#### Scenario: Data source takes precedence
- **WHEN** asset has both source and data_source_id
- **THEN** data_source relationship provides authoritative source information

### Requirement: Orphaned Asset Handling
The system SHALL handle assets that reference deleted data sources gracefully.

#### Scenario: Asset with deleted data source
- **WHEN** client requests asset that references non-existent data source
- **THEN** system returns asset with null data_source but preserves data_source_id

#### Scenario: Data source deletion warning
- **WHEN** attempting to delete data source with associated assets
- **THEN** system provides warning about affected assets</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/specs/asset-data-source-filtering/spec.md