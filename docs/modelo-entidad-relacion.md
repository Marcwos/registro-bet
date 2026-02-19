# Modelo Entidad-Relación

[← Volver al índice](./README.md)

---

## Diagrama ER

```mermaid
erDiagram

    USER {
        uuid id PK
        string email
        string password_hash
        boolean is_email_verified
        uuid role_id FK
        timestamp created_at
        timestamp updated_at
    }

    ROLE {
        uuid id PK
        string name
    }

    BET {
        uuid id PK
        uuid user_id FK
        uuid sport_id FK "nullable - modo pro"
        uuid status_id FK
        uuid category_id FK "nullable - modo pro"
        string title
        string description
        decimal stake_amount
        decimal odds
        decimal profit_expected
        decimal profit_final
        timestamp placed_at
        timestamp settled_at
        timestamp created_at
        timestamp updated_at
    }

    SPORT {
        uuid id PK
        string name
        boolean is_active
    }

    BET_STATUS {
        uuid id PK
        string name
        string code
        boolean is_final
    }

    BET_CATEGORY {
        uuid id PK
        string name
        string description
    }

    AUTH_SESSION {
        uuid id PK
        uuid user_id FK
        string refresh_token_hash
        timestamp expires_at
        timestamp created_at
        timestamp revoked_at
        string user_agent
        string ip_address
    }

    AUDIT_LOG {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        jsonb metadata
        timestamp created_at
    }

    ROLE ||--o{ USER : tiene
    USER ||--o{ BET : crea
    USER ||--o{ AUTH_SESSION : inicia
    USER ||--o{ AUDIT_LOG : genera

    SPORT ||--o{ BET : clasifica
    BET_STATUS ||--o{ BET : define_estado
    BET_CATEGORY ||--o{ BET : categoriza
```

---

## Relaciones

| Relación                  | Tipo   | Descripción                              |
| ------------------------- | ------ | ---------------------------------------- |
| `ROLE` → `USER`           | 1 a N  | Un rol tiene muchos usuarios             |
| `USER` → `BET`            | 1 a N  | Un usuario crea muchas apuestas          |
| `USER` → `AUTH_SESSION`   | 1 a N  | Un usuario inicia muchas sesiones        |
| `USER` → `AUDIT_LOG`      | 1 a N  | Un usuario genera muchos logs            |
| `SPORT` → `BET`           | 1 a N  | Un deporte clasifica muchas apuestas (nullable, modo pro)    |
| `BET_STATUS` → `BET`      | 1 a N  | Un estado define muchas apuestas         |
| `BET_CATEGORY` → `BET`    | 1 a N  | Una categoría/tipo agrupa muchas apuestas (nullable, modo pro) |

---

## Catálogos de Apuestas

> Los campos `sport_id` y `category_id` en `BET` son **nullable** porque solo se usan en **modo pro**.
> En modo normal, el usuario no los ve ni los completa.

| Catálogo       | Representa             | Ejemplos                                              |
| -------------- | ---------------------- | ----------------------------------------------------- |
| `SPORT`        | El deporte             | Fútbol, Tenis, MMA, Basketball, eSports               |
| `BET_CATEGORY` | Tipo/formato de apuesta | Simple, Combinada (2), Combinada (3-5), Combinada (6+) |

Estas dos dimensiones permiten estadísticas cruzadas en modo pro:
*"Ganás más en apuestas simples de fútbol que en combinadas de tenis"*.
