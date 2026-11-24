# Redundancia y comunicación industrial con OPC UA en Ignition

Trabajo de promoción — Sistemas Distribuidos (UNPSJB) — Facundo Vidal

Demostración de **alta disponibilidad** en un SCADA Ignition 8.3 aplicado a una
**unidad LACT** (medición fiscal de crudo): par redundante Master/Backup,
failover automático de clientes Perspective y Store & Forward del historian.

## Arquitectura

| Componente | Detalle |
|---|---|
| Gateway Master | Ignition 8.3.9 en Windows — `http://localhost:8088` |
| Gateway Backup | Ignition 8.3.9 en Docker — `http://127.0.0.1:9088` |
| Gateway Network | Backup → Master por `host.docker.internal:8060` (TLS, certificados aprobados en ambos nodos) |
| Dispositivo | Programmable Device Simulator `SimLACT` expuesto por el OPC UA Server de Ignition |
| Base de datos | SQL Server — `Historico_LACT` vía `host.docker.internal:1433` |
| HMI | Perspective, vista `Operador` |

## Contenido del repo

- `proyecto/` — export del proyecto Ignition (vistas, scripts, eventos)
- `tags/` — UDT `Unidad_LACT` e instancia `LACT_Bateria_1`
- `simulador/` — programa del dispositivo simulado
- `scripts/` — gateway scripts (totalizador de volumen y balance del tanque)
- `docs/capturas/` — evidencia de las pruebas

## Cómo reproducirlo

1. Instalar Ignition 8.3.9 (Master) e importar `proyecto/practica.zip`.
2. Importar `tags/*.json` en el provider `default`.
3. Crear el device `SimLACT` (Programmable Device Simulator) e importar `simulador/SimLACT.csv`.
4. Crear la conexión `Historico_LACT` a SQL Server usando `host.docker.internal`
   (agregar `127.0.0.1 host.docker.internal` al archivo hosts de Windows).
5. Levantar el Backup en Docker con puertos `9088:8088` y `9060:8060`.
6. **Antes de conectar:** dejar el Backup en *Independent*, restaurarle un `.gwbk`
   del Master y recién después pasarlo a rol *Backup*.
7. Igualar módulos en ambos nodos y aprobar certificados de Gateway Network en los dos.
8. Configurar la *Public HTTP Address* de cada nodo para que Perspective pueda redirigir.

## Pruebas realizadas

| Prueba | Resultado |
|---|---|
| Failover (Master detenido) | Backup pasa a Active; Perspective se redirige sola ("Failed over to Backup") |
| Failback | Master retoma el control; Backup vuelve a Warm |
| Configuración en Backup | Designer rechazado (nodo INACTIVE) |
| Store & Forward (SQL Server detenido ~9 min) | Pending 497 → 0, Dropped 0, sin huecos en la historia |

## Lecciones aprendidas

- **Redundancia ≠ backup.** Un Backup con configuración propia provocó que el Master
  sincronizara tags vacíos. Se recuperó desde una instantánea de Windows.
- `localhost` en conexiones de base de datos rompe el failover del historian.
- Ambos nodos deben tener exactamente los mismos módulos (OpcCom es solo Windows).
- Una conexión manual de Gateway Network entre los mismos nodos genera *Duplicate connection*.