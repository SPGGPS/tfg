## Context

The CMDB system currently supports asset management with a single monolithic data source approach. To support multiple external data sources (cloud providers, on-premises databases, API endpoints), we need to introduce a DataSource entity that can manage connections, validation, and synchronization status. The existing DataSource and Asset models already include the necessary relationships, but we need to implement the full CRUD API, validation logic, and frontend components.

Current system uses FastAPI with SQLAlchemy ORM, React frontend with Vite, and SQLite database. The backend follows a modular structure with routers, models, and services.

## Goals / Non-Goals

**Goals:**
- Implement complete CRUD operations for data sources via REST API
- Provide connection validation and testing capabilities
- Enable filtering assets by data source
- Support sync status monitoring and management
- Create user-friendly frontend for data source management
- Maintain backward compatibility with existing asset source field

**Non-Goals:**
- Implement actual data synchronization logic (out of scope)
- Support real-time sync monitoring (basic status tracking only)
- Handle complex authentication schemes beyond basic credentials
- Provide data source-specific configuration UIs (generic JSON config)

## Decisions

**API Design:**
- Use RESTful endpoints under `/v1/data-sources` following existing patterns
- Include validation endpoint `/v1/data-sources/{id}/validate` for connection testing
- Add query parameter `data_source_id` to existing asset endpoints for filtering
- Return consistent error responses with proper HTTP status codes

**Data Model:**
- Leverage existing DataSource model with JSON connection_config for flexibility
- Support multiple data source types: api, database, file, agent, manual
- Use priority field for conflict resolution when assets exist in multiple sources
- Maintain sync_interval_minutes for future automated sync scheduling

**Validation Strategy:**
- Implement connection testing based on data source type
- For API sources: HTTP connectivity and optional authentication
- For database sources: connection string validation
- Return detailed validation results with error messages

**Frontend Integration:**
- Create dedicated DataSources page in React
- Use existing table/list patterns from Tags and Assets pages
- Include connection status indicators and validation buttons
- Add data source dropdown to asset filtering

**Database Migration:**
- Create data_sources table migration script
- Add sample data sources in init_db.py
- Ensure foreign key constraints are properly handled

## Risks / Trade-offs

**Security Risk:** Storing connection credentials in database → Mitigation: Use encrypted storage for sensitive fields, implement proper access controls

**Performance Risk:** Additional joins for data source filtering → Mitigation: Add database indexes on data_source_id, use efficient queries

**Complexity Risk:** Generic JSON config may lead to validation issues → Mitigation: Implement type-specific validation schemas, provide clear documentation

**Migration Risk:** Existing assets without data_source_id → Mitigation: Allow nullable foreign key, maintain legacy source field for backward compatibility</content>
<parameter name="filePath">/Users/sergio/TFG/tfg/openspec/changes/data-sources/design.md