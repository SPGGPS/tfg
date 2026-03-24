# Design: Unit Test Specs

## Context

Plan de pruebas para CMDB, RBAC, Audit Logs. Módulos: AUTH_&_RBAC, INVENTORY_&_COMPLIANCE, TAG_MANAGEMENT, AUDIT_&_PROFILE.

## Goals / Non-Goals

**Goals:** Especificaciones TS-01 a TS-11 como casos de prueba, Pytest backend, Vitest/RTL frontend, Playwright E2E.

**Non-Goals:** Implementar todos los tests en una sola iteración, coverage 100%.

## Decisions

| Decisión | Rationale |
|----------|-----------|
| Pytest + Vitest + Playwright | Backend, frontend y E2E con herramientas estándar |
| Assertions en formato legible | Facilitar mantenimiento y debugging |
