"""
Interceptor de auditoría automática.
Registra eventos en audit_logs antes del commit de la transacción.
"""
import json
from typing import Any, Dict, Optional

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditInterceptor:
    """Interceptor que registra cambios en audit_logs automáticamente."""

    def __init__(self):
        self._changes = {}

    def register_events(self):
        """Registra los event listeners de SQLAlchemy."""
        # Evento antes del flush (cuando se detectan cambios)
        event.listen(Session, 'before_flush', self._before_flush)

        # Evento después del commit (para guardar audit logs)
        event.listen(Session, 'after_commit', self._after_commit)

        # Evento antes del rollback (limpiar cambios)
        event.listen(Session, 'after_rollback', self._after_rollback)

    def _before_flush(self, session: Session, flush_context, instances):
        """Captura los cambios antes del flush."""
        self._changes = {}

        # Procesar objetos nuevos
        for obj in session.new:
            if hasattr(obj, '__tablename__') and obj.__tablename__ != 'audit_logs':
                self._changes[obj] = {
                    'action': 'CREATE',
                    'old_values': {},
                    'new_values': self._get_object_values(obj)
                }

        # Procesar objetos modificados
        for obj in session.dirty:
            if hasattr(obj, '__tablename__') and obj.__tablename__ != 'audit_logs':
                old_values = {}
                new_values = {}

                # Obtener cambios usando SQLAlchemy inspection
                for attr in obj.__mapper__.attrs:
                    if hasattr(obj, attr.key):
                        new_val = getattr(obj, attr.key)
                        if attr.key in session.dirty_intersection(obj):
                            # Este campo fue modificado
                            old_val = session.get_attribute_history(obj, attr.key)[2]  # Valor anterior
                            old_values[attr.key] = old_val[0] if old_val else None
                            new_values[attr.key] = new_val

                if old_values or new_values:
                    self._changes[obj] = {
                        'action': 'UPDATE',
                        'old_values': old_values,
                        'new_values': new_values
                    }

        # Procesar objetos eliminados
        for obj in session.deleted:
            if hasattr(obj, '__tablename__') and obj.__tablename__ != 'audit_logs':
                self._changes[obj] = {
                    'action': 'DELETE',
                    'old_values': self._get_object_values(obj),
                    'new_values': {}
                }

    def _after_commit(self, session: Session):
        """Guarda los audit logs después del commit exitoso."""
        for obj, change_data in self._changes.items():
            # Crear registro de auditoría
            audit_log = AuditLog(
                user_id=getattr(session, '_current_user_id', 'system'),  # Placeholder
                activity_type=change_data['action'],
                resource_type=obj.__tablename__,
                resource_id=getattr(obj, 'id', None),
                details={
                    'changes': {
                        'old': change_data['old_values'],
                        'new': change_data['new_values']
                    },
                    'table': obj.__tablename__
                }
            )
            session.add(audit_log)

        self._changes.clear()

    def _after_rollback(self, session: Session):
        """Limpia los cambios en caso de rollback."""
        self._changes.clear()

    def _get_object_values(self, obj) -> Dict[str, Any]:
        """Obtiene todos los valores serializables del objeto."""
        values = {}
        for attr in obj.__mapper__.attrs:
            if hasattr(obj, attr.key):
                value = getattr(obj, attr.key)
                # Serializar valores para JSON
                if hasattr(value, 'isoformat'):  # datetime
                    values[attr.key] = value.isoformat()
                elif isinstance(value, (list, dict)):
                    values[attr.key] = value
                else:
                    values[attr.key] = str(value) if value is not None else None
        return values


# Instancia global del interceptor
audit_interceptor = AuditInterceptor()