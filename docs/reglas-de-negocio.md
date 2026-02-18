# Reglas de Negocio

[← Volver al índice](./README.md)

---

## 🔐 Propiedad y Privacidad

1. Cada usuario solo puede ver y modificar **sus propias apuestas**.
2. El admin **NO** puede ver apuestas individuales ni datos sensibles.
3. El admin solo accede a **métricas agregadas** del sistema.
4. Las apuestas eliminadas:
   - Desaparecen para el usuario.
   - Se registra el evento en auditoría (no se borra el rastro).

---

## ⏱️ Ciclo de Vida de una Apuesta

**Estados válidos:** `pendiente` → `ganada` | `perdida` | `nula`

5. Una apuesta inicia siempre en `pendiente`.
6. Solo apuestas `pendientes` pueden editarse libremente.
7. Una apuesta puede cambiar de estado **en cualquier momento** (por si el usuario se equivoca).
8. Cambiar el estado **recalcula balances automáticamente**.
9. La fecha se asigna por sistema pero puede editarse solo para registrar apuestas pasadas.

---

## 💰 Impacto en el Balance

| Estado      | Impacto en Balance             |
| ----------- | ------------------------------ |
| `pendiente` | No afecta balance              |
| `ganada`    | Suma ganancia neta             |
| `perdida`   | Resta monto apostado           |
| `nula`      | Impacto 0                      |

10. El usuario introduce la **ganancia real** manualmente.

**Balances visibles:**

11. Balance diario.
12. Balance histórico total.
13. Resumen por rango de fechas.

---

## 🧮 Integridad de Datos

14. Monto apostado **> 0**
15. Cuota **> 1.00**
16. Valores monetarios en **USD con 2 decimales**.
17. Toda apuesta debe tener **estado válido**.

---

## 📅 Historial y Edición

18. El resumen diario se calcula desde **datos reales** (no cache).
19. El usuario puede editar apuestas pasadas, pero **con confirmación**.
20. Zona horaria del sistema = **la del usuario**.

---

## 🔐 Sesiones y Seguridad

21. "Recordarme" mantiene sesión válida hasta **7 días**.
22. Cambiar contraseña **invalida todas las sesiones activas**.
    > Si alguien roba un token y el usuario cambia contraseña, ese token deja de funcionar.

---

## ✉️ Verificación de Email

23. Al registrarse, el sistema envía un **correo con enlace único** de verificación.
24. Solo usuarios con **correo verificado** pueden iniciar sesión.
    > Si el usuario no verifica su correo, no puede hacer login.
25. El enlace de verificación marca `is_email_verified = true`.
26. Si el correo ya está verificado, no se puede volver a verificar.

---

## 🔑 Recuperación de Contraseña

27. El código de recuperación expira en **10 minutos**.
28. El código de recuperación es de **un solo uso**.
29. Solo el **último código generado** es válido (los anteriores se invalidan).
30. Existe un **límite de intentos** para introducir el código.
31. Solicitar recuperación **no revela si el correo existe** en el sistema.
    > Siempre se responde "si el email está registrado, recibirás un código" — por seguridad.
32. Al cambiar la contraseña (ya sea por recuperación o cambio manual), se **invalidan todas las sesiones activas** (regla 22).

---

## 📊 Admin y Auditoría

**Admin puede ver:**

- Número de usuarios
- Número de apuestas registradas
- Métricas agregadas

**Auditoría registra:**

- Registro de usuario
- Login
- Cambio de contraseña
- Eliminación de apuesta

---

## 🎛️ UX que Impacta Dominio

- Categorías de deporte existen desde **v1**.
- Las categorías las crea **el admin**.
- Tema claro/oscuro se guarda en **perfil del usuario**.

---

## 📐 Decisiones Técnicas

| Decisión                       | Resolución                                                                 |
| ------------------------------ | -------------------------------------------------------------------------- |
| Editar apuestas cerradas       | Permitido cambiar estado siempre. Los usuarios cometen errores.            |
| Fecha editable                 | Permitido solo si el usuario está registrando apuestas antiguas.           |
| Guardar al final del día       | No. Cada cambio se guarda automáticamente (más moderno, menos errores).    |

---

## 🧮 Cálculos del Sistema

> Motor matemático de la aplicación.

### Por cada apuesta cerrada

```
ganada  → balance += ganancia_real
perdida → balance -= monto_apostado
nula    → balance += 0
```

### Para reportes

| Métrica                       | Cálculo                                    |
| ----------------------------- | ------------------------------------------ |
| Suma de ganancias             | Σ `profit_final` de apuestas ganadas       |
| Suma de pérdidas              | Σ `stake_amount` de apuestas perdidas      |
| Profit neto                   | Ganancias − Pérdidas                       |
| Conteo por estado             | COUNT agrupado por `status`                |
