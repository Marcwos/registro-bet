# Requisitos Funcionales

[← Volver al índice](./README.md)

---

## 🔐 Autenticación

- Crear cuenta
- Verificar correo electrónico
- Iniciar sesión
- Cerrar sesión
- Recuperar contraseña vía correo con código

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

## 🧾 Datos de la Apuesta (Modo Fácil)

| Campo      | Detalle                                              |
| ---------- | ---------------------------------------------------- |
| Título     | Automático (`Apuesta 1`, `Apuesta 2`, etc. por día)  |
| Monto      | Monto apostado                                       |
| Cuota      | Cuota de la apuesta                                  |
| Ganancia   | Campo único editable (ganancia real)                  |
| Estado     | Pendiente / Ganada / Perdida / Nula                  |
| Fecha      | Interna, no visible al usuario                       |

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
