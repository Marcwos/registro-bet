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
        uuid sport_id FK
        uuid status_id FK
        uuid category_id FK
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
| `SPORT` → `BET`           | 1 a N  | Un deporte clasifica muchas apuestas     |
| `BET_STATUS` → `BET`      | 1 a N  | Un estado define muchas apuestas         |
| `BET_CATEGORY` → `BET`    | 1 a N  | Una categoría agrupa muchas apuestas     |
