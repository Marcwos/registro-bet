# Diagramas de Flujo — Registro Bet

[← Volver al índice](./README.md)

---

## 1. Flujo Actual del Usuario (Backend implementado)

> Muestra el flujo completo que soporta el backend actualmente con todos los endpoints.

```mermaid
flowchart TD
    A[Usuario nuevo] --> B[POST /register/]
    B --> C[Recibe código de verificación por email]
    C --> D[POST /verify-email/]
    D --> E[Email verificado ✅]
    E --> F[POST /login/]
    F --> G[Recibe access_token + refresh_token]

    G --> H{¿Qué quiere hacer?}

    H --> I[Crear apuesta]
    I --> I1[POST /api/bets/]
    I1 --> I2["Envía: stake_amount, odds, profit_expected"]
    I2 --> I3["Título autogenerado: 'Apuesta N'"]
    I3 --> I4[Estado: pendiente por defecto]
    I4 --> I5[Fecha: automática del sistema]

    H --> J[Ver sus apuestas]
    J --> J1[GET /api/bets/]
    J1 --> J2[Lista todas sus apuestas]

    H --> K[Editar apuesta]
    K --> K1[PATCH /api/bets/id/]
    K1 --> K2{¿Es pendiente?}
    K2 -->|Sí| K3[Se edita libremente]
    K2 -->|No| K4{¿Envió confirm=true?}
    K4 -->|Sí| K3
    K4 -->|No| K5[Error 409: requiere confirmación]

    H --> L[Cambiar estado]
    L --> L1[PATCH /api/bets/id/status/]
    L1 --> L2{Estado nuevo}
    L2 --> L3[ganada → suma profit_final al balance]
    L2 --> L4[perdida → resta stake_amount del balance]
    L2 --> L5[nula → sin efecto]
    L2 --> L6[pendiente → sin efecto]

    H --> M[Ver estadísticas]
    M --> M1[GET /balance/daily/]
    M --> M2[GET /balance/total/]
    M --> M3[GET /history/]

    H --> N[Eliminar apuesta]
    N --> N1[DELETE /api/bets/id/]

    G --> O[POST /refresh/ cuando expira token]
    G --> P[POST /logout/ para cerrar sesión]
```

---

## 2. Flujo del Usuario en el Frontend (Versión final esperada)

> Muestra cómo interactuará el usuario con la aplicación a través del frontend.
> Solo los campos visibles y las acciones disponibles para el usuario final.

```mermaid
flowchart TD
    A[Página de inicio] --> B{¿Tiene cuenta?}
    B -->|No| C[Pantalla de Registro]
    C --> C1[Ingresa email y contraseña]
    C1 --> C2[Recibe email con enlace de verificación]
    C2 --> C3[Verifica email]
    C3 --> D

    B -->|Sí| D[Pantalla de Login]
    D --> D1[Ingresa email y contraseña]
    D1 --> D2{¿Email verificado?}
    D2 -->|No| D3[Mensaje: verifica tu email primero]
    D2 -->|Sí| E[Dashboard Principal]

    E --> F{Acciones disponibles}

    F --> G[➕ Crear Apuesta]
    G --> G1["Formulario con 3 campos:"]
    G1 --> G2["1. Monto apostado (stake_amount)"]
    G1 --> G3["2. Cuota (odds)"]
    G1 --> G4["3. Ganancia esperada (profit_expected)"]
    G2 & G3 & G4 --> G5[Se crea con estado PENDIENTE]
    G5 --> G6["Título auto: 'Apuesta N'"]
    G6 --> G7[Fecha: automática del día actual]

    F --> H[📋 Ver Apuestas]
    H --> H1[Lista de apuestas del día]
    H1 --> H2[Cada apuesta muestra:]
    H2 --> H3[Título, Monto, Cuota, Ganancia, Estado]

    F --> I[🔄 Cambiar Estado de Apuesta]
    I --> I1{Seleccionar nuevo estado}
    I1 --> I2[✅ Ganada]
    I1 --> I3[❌ Perdida]
    I1 --> I4[⬜ Nula]
    I1 --> I5[⏳ Pendiente]
    I2 & I3 & I4 & I5 --> I6[Se puede cambiar en cualquier momento]

    F --> J[📊 Ver Balance]
    J --> J1[Balance del día]
    J --> J2[Balance total acumulado]
    J --> J3[Historial por rango de fechas]

    F --> K[🗑️ Eliminar Apuesta]
    K --> K1[Confirmación antes de eliminar]

    F --> L[🔒 Cerrar Sesión]

    style G1 fill:#e8f5e9
    style G2 fill:#e8f5e9
    style G3 fill:#e8f5e9
    style G4 fill:#e8f5e9
```

---

## 3. Flujo de Creación de Apuesta — Detalle técnico

> Cómo fluye la data desde el frontend hasta la base de datos.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant FE as Frontend
    participant API as Django API
    participant UC as CreateBet UseCase
    participant VO as Value Objects
    participant DB as PostgreSQL

    U->>FE: Llena formulario (monto, cuota, ganancia)
    FE->>API: POST /api/bets/ {stake_amount, odds, profit_expected}
    API->>API: Serializer valida tipos y rangos

    API->>UC: execute(user_id, stake_amount, odds, profit_expected)
    UC->>VO: Money(amount=stake_amount)
    VO-->>UC: ✅ Monto válido (> 0, 2 decimales)

    UC->>VO: Odds(value=odds)
    VO-->>UC: ✅ Cuota válida (> 1.00, 2 decimales)

    UC->>UC: Validar profit_expected >= 0
    UC->>DB: Obtener estado "pendiente"
    UC->>DB: Contar apuestas del usuario hoy
    UC->>UC: Generar título "Apuesta N"
    UC->>DB: Guardar apuesta

    DB-->>API: Apuesta creada
    API-->>FE: 201 Created + datos de la apuesta
    FE-->>U: Muestra apuesta en la lista
```

---

## 4. Flujo de Cambio de Estado

> Cómo funciona el cambio de estado y su impacto en el balance.

```mermaid
stateDiagram-v2
    [*] --> Pendiente: Apuesta creada

    Pendiente --> Ganada: Usuario marca como ganada
    Pendiente --> Perdida: Usuario marca como perdida
    Pendiente --> Nula: Usuario marca como nula

    Ganada --> Pendiente: Corrige error
    Ganada --> Perdida: Corrige error
    Ganada --> Nula: Corrige error

    Perdida --> Pendiente: Corrige error
    Perdida --> Ganada: Corrige error
    Perdida --> Nula: Corrige error

    Nula --> Pendiente: Corrige error
    Nula --> Ganada: Corrige error
    Nula --> Perdida: Corrige error

    note right of Pendiente: Sin efecto en balance
    note right of Ganada: Balance += profit_final
    note right of Perdida: Balance -= stake_amount
    note right of Nula: Balance += 0
```

---

## Campos visibles por contexto

| Campo | Frontend (usuario) | Backend (API) | Base de datos |
|---|---|---|---|
| Monto apostado | ✅ Ingresa | ✅ Requerido | `stake_amount` |
| Cuota | ✅ Ingresa | ✅ Requerido | `odds` |
| Ganancia esperada | ✅ Ingresa | ✅ Requerido | `profit_expected` |
| Estado | ✅ Cambia | ✅ Requerido | `status_id` |
| Título | ❌ Autogenerado | ✅ Autogenerado | `title` |
| Fecha | ❌ Automática | ✅ Automática | `placed_at` |
| Descripción | ❌ No visible (v1) | ✅ Opcional | `description` |
| Deporte | ❌ No visible (v1) | ✅ Opcional | `sport_id` |
| Categoría | ❌ No visible (v1) | ✅ Opcional | `category_id` |
| Ganancia real | ❌ No visible (v1) | ✅ Opcional | `profit_final` |
