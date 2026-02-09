# Stack Tecnológico y Arquitectura

[← Volver al índice](./README.md)

---

## Stack Tecnológico

| Capa               | Tecnología                          |
| ------------------ | ----------------------------------- |
| **Backend**        | Django + Django REST Framework      |
| **Base de datos**  | PostgreSQL                          |
| **Auth**           | JWT + Refresh Token (tabla session) |
| **Arquitectura**   | Clean Architecture por módulos      |

---

## Arquitectura

### Clean Architecture por Features

Cada módulo/feature se organiza de forma independiente siguiendo las capas de Clean Architecture.

---

## Patrones de Diseño

| Patrón                    | Uso                                |
| ------------------------- | ---------------------------------- |
| **Repository Pattern**    | Acceso a datos                     |
| **Service Layer**         | Lógica de negocio                  |
| **DTO / Serializer**      | Comunicación API                   |
| **Dependency Inversion**  | Para testing y desacoplamiento     |
| **Value Objects simples** | Dinero, estado                     |
