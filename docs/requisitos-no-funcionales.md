# Requisitos No Funcionales

[← Volver al índice](./README.md)

---

## 🔐 Seguridad

- Autenticación basada en JWT
- Manejo seguro de sesiones con opción "recordarme"
- Datos completamente privados por usuario
- Protección contra accesos no autorizados
- El administrador **no** tiene acceso a datos sensibles ni apuestas individuales

---

## 👤 Privacidad

- Cada usuario solo puede acceder a su propia información
- No existe compartición de datos entre usuarios
- Cumplimiento de principios básicos de privacidad

---

## ⚡ Rendimiento

- Respuestas rápidas del backend ante peticiones comunes
- Interfaz fluida y sin retrasos perceptibles
- Cargas y transiciones optimizadas para buena experiencia de usuario

---

## 📈 Escalabilidad

Arquitectura preparada para:

- Agregar modo avanzado
- Incluir más estadísticas
- Ampliar campos y funcionalidades
- No requerir rediseños completos al crecer

---

## 🧪 Calidad y Testing

- El sistema debe permitir pruebas automatizadas
- Testing de autenticación, apuestas y permisos
- Manejo adecuado de errores y mensajes claros al usuario

---

## 🎨 Usabilidad

- Interfaz clara, intuitiva y fácil de usar
- Soporte para modo claro y modo oscuro
- Información visual clara (verde / rojo / nulo)

---

## 💾 Persistencia y Confiabilidad

- Los datos deben guardarse correctamente y mantenerse consistentes
- Manejo de errores del sistema sin pérdida de información
- Backups no obligatorios en la primera versión
