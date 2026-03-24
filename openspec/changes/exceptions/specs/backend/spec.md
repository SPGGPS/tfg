# Backend Spec — Compliance Exceptions

## models/exception.py

```python
class ComplianceException(Base):
    __tablename__ = "compliance_exceptions"
    id              = Column(String, PK)
    asset_id        = Column(String, FK assets.id CASCADE, INDEX)
    indicator       = Column(Enum(ComplianceIndicator), INDEX)
    reason_code     = Column(Enum(ExceptionReasonCode))
    reason          = Column(Text)          # label + ": " + descripción libre
    created_by      = Column(String(255))   # sub JWT
    created_by_name = Column(String(255))
    created_at      = Column(DateTime TZ)
    expires_at      = Column(DateTime TZ, nullable=True, INDEX)
    revoked_by      = Column(String(255), nullable=True)
    revoked_by_name = Column(String(255), nullable=True)
    revoked_at      = Column(DateTime TZ, nullable=True, INDEX)
```

## Serialización crítica de enums
```python
def to_dict(self):
    return {
        "reason_code": str(self.reason_code).split(".")[-1] if self.reason_code else None,
        "indicator":   str(self.indicator).split(".")[-1] if self.indicator else None,
        # ...resto de campos
    }
```

## routers/exceptions.py — orden de declaración
```python
@router.get("/v1/exceptions/reason-codes/list")  # primero — ruta específica
@router.get("/v1/exceptions/{exception_id}")      # después — con parámetro
```

## Invalidación de assets tras crear/revocar excepción
Los assets incluyen sus excepciones activas en to_dict(). El frontend debe invalidar:
```js
queryClient.invalidateQueries({ queryKey: ["assets"], exact: false })
```
