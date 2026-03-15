"""
Script para inicializar la base de datos y crear datos de prueba.
"""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models.asset import Asset
from app.models.data_source import DataSource
from app.models.tag import Tag


async def init_db():
    """Inicializa la base de datos y crea tablas."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Base de datos inicializada")


async def create_sample_data():
    """Crea datos de ejemplo para testing."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Limpiar datos existentes
        print("🧹 Limpiando datos existentes...")
        from app.models.asset_tag import asset_tag_table
        await session.execute(asset_tag_table.delete())
        await session.execute(delete(Asset))
        await session.execute(delete(Tag))
        await session.execute(delete(DataSource))
        await session.commit()

        # Crear tags de sistema
        system_tags = [
            Tag(name="VMware", color_code="#0066CC", origin="system", created_by="system"),
            Tag(name="Physical", color_code="#FF6600", origin="system", created_by="system"),
            Tag(name="Network", color_code="#009933", origin="system", created_by="system"),
            Tag(name="Critical", color_code="#CC0000", origin="system", created_by="system"),
        ]

        for tag in system_tags:
            session.add(tag)

        # Crear tags manuales
        manual_tags = [
            Tag(name="Production", color_code="#FF0000", origin="manual", created_by="admin"),
            Tag(name="Development", color_code="#00FF00", origin="manual", created_by="admin"),
            Tag(name="Testing", color_code="#FFFF00", origin="manual", created_by="admin"),
        ]

        for tag in manual_tags:
            session.add(tag)

        await session.commit()

        # Crear data sources de ejemplo
        data_sources = [
            DataSource(
                id="vmware-vcenter",
                name="VMware vCenter",
                type="api",
                description="Primary VMware vCenter server for virtual infrastructure",
                connection_config={
                    "url": "https://vcenter.company.com/sdk",
                    "username": "cmdb_user",
                    "password": "encrypted_password",
                    "verify_ssl": True
                },
                is_active=True,
                sync_interval_minutes=30,
                priority=1
            ),
            DataSource(
                id="servicenow-cmdb",
                name="ServiceNow CMDB",
                type="api",
                description="ServiceNow Configuration Management Database",
                connection_config={
                    "url": "https://company.servicenow.com/api/now/table/cmdb_ci",
                    "username": "cmdb_integration",
                    "password": "encrypted_password",
                    "client_id": "client_id_here",
                    "client_secret": "client_secret_here"
                },
                is_active=True,
                sync_interval_minutes=60,
                priority=2
            ),
            DataSource(
                id="veeam-backup",
                name="Veeam Backup Server",
                type="api",
                description="Veeam backup and replication server",
                connection_config={
                    "url": "https://veeam.company.com:9398/api",
                    "username": "cmdb_user",
                    "password": "encrypted_password"
                },
                is_active=True,
                sync_interval_minutes=120,
                priority=3
            ),
            DataSource(
                id="crowdstrike-edr",
                name="CrowdStrike EDR",
                type="api",
                description="CrowdStrike Falcon endpoint detection and response",
                connection_config={
                    "url": "https://api.crowdstrike.com",
                    "client_id": "client_id_here",
                    "client_secret": "client_secret_here"
                },
                is_active=True,
                sync_interval_minutes=15,
                priority=1
            ),
            DataSource(
                id="zabbix-monitoring",
                name="Zabbix Monitoring",
                type="api",
                description="Zabbix network monitoring system",
                connection_config={
                    "url": "https://zabbix.company.com/api_jsonrpc.php",
                    "username": "cmdb_user",
                    "password": "encrypted_password"
                },
                is_active=True,
                sync_interval_minutes=5,
                priority=2
            ),
            DataSource(
                id="manual-entry",
                name="Manual Entry",
                type="manual",
                description="Manually entered assets for systems not covered by automated sources",
                connection_config={},
                is_active=True,
                sync_interval_minutes=0,
                priority=10
            )
        ]

        for ds in data_sources:
            session.add(ds)

        await session.commit()

        # Crear assets de ejemplo
        assets = [
            Asset(
                id="srv-web-001",
                name="Web Server 01",
                type="server_virtual",
                ips=["192.168.1.10", "10.0.0.10"],
                vendor="VMware",
                data_source_id="vmware-vcenter",
                source="VMware",
                edr_installed=True,
                last_backup=datetime.utcnow() - timedelta(hours=2),
                monitored=True,
                logs_enabled=True,
                last_sync=datetime.utcnow(),
                ram_gb=8,
                total_disk_gb=100,
                cpu_count=4,
                os="Ubuntu 22.04",
            ),
            Asset(
                id="srv-db-001",
                name="Database Server",
                type="server_physical",
                ips=["192.168.1.20"],
                vendor="Dell",
                data_source_id="servicenow-cmdb",
                source="ServiceNow",
                edr_installed=True,
                last_backup=datetime.utcnow() - timedelta(hours=1),
                monitored=True,
                logs_enabled=True,
                last_sync=datetime.utcnow(),
                ram_gb=32,
                total_disk_gb=500,
                cpu_count=8,
                os="Red Hat Enterprise Linux 8",
            ),
            Asset(
                id="sw-core-001",
                name="Core Switch",
                type="switch",
                ips=["192.168.1.1"],
                vendor="Cisco",
                data_source_id="crowdstrike-edr",
                source="EDR",
                edr_installed=False,
                monitored=True,
                logs_enabled=True,
                last_sync=datetime.utcnow(),
                model="Catalyst 9300",
                port_count=48,
                max_speed="10Gbps",
            ),
            Asset(
                id="rt-border-001",
                name="Border Router",
                type="router",
                ips=["203.0.113.1"],
                vendor="Juniper",
                data_source_id="zabbix-monitoring",
                source="Monitorización",
                monitored=True,
                logs_enabled=True,
                last_sync=datetime.utcnow(),
                model="MX480",
                port_count=8,
                firmware_version="20.2R1",
            ),
            Asset(
                id="ap-office-001",
                name="Office Access Point",
                type="ap",
                ips=["192.168.1.50"],
                vendor="Ubiquiti",
                data_source_id="zabbix-monitoring",
                source="Monitorización",
                monitored=True,
                logs_enabled=False,
                last_sync=datetime.utcnow(),
                model="UniFi AP-AC-Pro",
                coverage_area="500m²",
                connected_clients=23,
            ),
        ]

        for asset in assets:
            session.add(asset)

        await session.commit()

        # Asignar tags a assets
        vmware_tag = await session.scalar(select(Tag).where(Tag.name == "VMware"))
        physical_tag = await session.scalar(select(Tag).where(Tag.name == "Physical"))
        network_tag = await session.scalar(select(Tag).where(Tag.name == "Network"))
        critical_tag = await session.scalar(select(Tag).where(Tag.name == "Critical"))
        prod_tag = await session.scalar(select(Tag).where(Tag.name == "Production"))

        if vmware_tag and physical_tag and network_tag and critical_tag and prod_tag:
            # Asignar tags usando la tabla de asociación
            from app.models.asset_tag import asset_tag_table

            # Web server: VMware, Production, Critical
            await session.execute(asset_tag_table.insert().values([
                {"asset_id": "srv-web-001", "tag_id": vmware_tag.id, "assigned_by": "admin"},
                {"asset_id": "srv-web-001", "tag_id": prod_tag.id, "assigned_by": "admin"},
                {"asset_id": "srv-web-001", "tag_id": critical_tag.id, "assigned_by": "admin"},
            ]))

            # DB server: Physical, Production, Critical
            await session.execute(asset_tag_table.insert().values([
                {"asset_id": "srv-db-001", "tag_id": physical_tag.id, "assigned_by": "admin"},
                {"asset_id": "srv-db-001", "tag_id": prod_tag.id, "assigned_by": "admin"},
                {"asset_id": "srv-db-001", "tag_id": critical_tag.id, "assigned_by": "admin"},
            ]))

            # Switch: Network, Production
            await session.execute(asset_tag_table.insert().values([
                {"asset_id": "sw-core-001", "tag_id": network_tag.id, "assigned_by": "admin"},
                {"asset_id": "sw-core-001", "tag_id": prod_tag.id, "assigned_by": "admin"},
            ]))

            # Router: Network, Critical
            await session.execute(asset_tag_table.insert().values([
                {"asset_id": "rt-border-001", "tag_id": network_tag.id, "assigned_by": "admin"},
                {"asset_id": "rt-border-001", "tag_id": critical_tag.id, "assigned_by": "admin"},
            ]))

            await session.commit()

        print("✅ Datos de ejemplo creados")


async def main():
    """Función principal."""
    print("🚀 Inicializando base de datos...")
    await init_db()
    print("📝 Creando datos de ejemplo...")
    await create_sample_data()
    print("🎉 ¡Base de datos lista para testing!")


if __name__ == "__main__":
    asyncio.run(main())