# Configuración del Plan de Suscripción

## ✅ Ya configurado: LUKI FULL

El plan **LUKI FULL** (ID: `plan-lukiplay`) ya está configurado por defecto.

## ¿Por qué usar ID en lugar del nombre?

Cuando usas el **ID del plan** en lugar del nombre:
- ✅ Los cambios en el nombre del plan se reflejan automáticamente
- ✅ Los cambios en características del plan se aplican a todos los usuarios
- ✅ No hay problemas si renombras el plan en el CMS

## Planes disponibles en tu CMS

```
ID: plan-lukiplay          → LUKI FULL (configurado por defecto)
ID: 2d37c13d-b0c3-...      → FIFAS
ID: fb3d2072-8127-...      → LUKIPLAY GO
```

## Cambiar de plan

Si quieres usar un plan diferente, edita `.env`:

```bash
# Para usar LUKI FULL (por defecto)
SUBSCRIPTION_PLAN_ID=plan-lukiplay

# Para usar FIFAS
SUBSCRIPTION_PLAN_ID=2d37c13d-b0c3-48b0-a115-9fd3c9d33713

# Para usar LUKIPLAY GO
SUBSCRIPTION_PLAN_ID=fb3d2072-8127-448d-9d84-cb4a62669da5
```

## Verificar planes actualizados

Si agregas nuevos planes en el CMS, conéctate al EC2 y ejecuta:

```bash
ssh -i /ruta/a/tu/clave.pem admin@98.93.25.166
PGPASSWORD='dev_password_2026' psql -h localhost -U lukiplay_admin -d lukiplay_prod \
  -c 'SELECT id, nombre, precio, "duracionDias", activo FROM plans ORDER BY nombre;'
```
