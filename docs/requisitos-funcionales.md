# Requisitos Funcionales

[← Volver al índice](./README.md)

---

## 🔐 Autenticación

- Crear cuenta
- Verificar correo electrónico (enlace único → marca `is_email_verified`)
- Iniciar sesión (**solo si el correo está verificado**)
- Cerrar sesión
- Recuperar contraseña vía correo con código (expira en 10 min, un solo uso)
- Cambiar contraseña (invalida todas las sesiones activas)

---

## 👤 Usuario

- Acceso exclusivo a su información
- Información privada y no compartida
- Preferencia de modo claro / modo oscuro

---

## 📊 Apuestas

El usuario puede:

- Crear una apuesta
- Editar una apuesta
- Eliminar una apuesta (con confirmación)
- Cambiar el estado de una apuesta

**Estados posibles:**

| Estado      | Descripción              |
| ----------- | ------------------------ |
| `pendiente` | Estado por defecto       |
| `ganada`    | La apuesta fue acertada  |
| `perdida`   | La apuesta fue fallida   |
| `nula`      | Sin efecto en el balance |

---

## 🧾 Datos de la Apuesta (Modo Normal)

| Campo      | Detalle                                              |
| ---------- | ---------------------------------------------------- |
| Título     | Automático (`Apuesta 1`, `Apuesta 2`, etc. por día)  |
| Monto      | Monto apostado                                       |
| Cuota      | Cuota de la apuesta                                  |
| Ganancia   | Campo único editable (ganancia real)                  |
| Estado     | Pendiente / Ganada / Perdida / Nula                  |
| Fecha      | Interna, no visible al usuario                       |

---

## 🚀 Datos de la Apuesta (Modo Pro — futuro)

> Escalado previsto: cuando el modo normal funcione completo, se implementa modo pro.
> Los campos adicionales son **opcionales** (nullable en BD).

| Campo         | Detalle                                                  |
| ------------- | -------------------------------------------------------- |
| Deporte       | Selección de catálogo (`Sport`: Fútbol, Tenis, MMA...)   |
| Tipo apuesta  | Selección de catálogo (`BetCategory`: Simple, Combinada) |
| Descripción   | Texto libre opcional                                     |

**Beneficio:** estadísticas enriquecidas por deporte y tipo de apuesta.
Ejemplo: *"Tu mejor rendimiento es en apuestas simples de fútbol"*.

---

## 📅 Historial

- Vista diaria de apuestas
- Resumen diario (apostado, ganado, perdido)
- Filtro por rango de fechas

---

## 💰 Estadísticas

- Balance diario
- Balance total acumulado
- Ganancias y pérdidas claras

---

## 🎨 Interfaz

- Modo claro
- Modo oscuro

---

## 👑 Admin

- Ver usuarios registrados
- Ver estadísticas globales agregadas
- Auditoría básica del sistema (eventos técnicos)
- **Sin acceso** a apuestas individuales ni datos sensibles
