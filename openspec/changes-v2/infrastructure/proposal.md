id: infrastructure

context: |
  Despliegue: Docker Compose (desarrollo) / k3s + Helm (producción)
  Namespace: inventory-ssreyes

proposal: |
  1. docker-compose.yml con PostgreSQL (puerto 5433), backend y frontend
  2. Helm chart completo con Deployments, Services, Ingress, HPA, NetworkPolicies
  3. CronJobs: snapshot horario, purga audit_logs (180d), purga history (1 año)
  4. Cilium NetworkPolicies deny-all con allows explícitos

status: Implementado al 100%.
