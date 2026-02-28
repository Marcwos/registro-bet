#!/usr/bin/env bash
# Script de build para Render
# Se ejecuta cada vez que se despliega el backend

set -o errexit  # Salir si cualquier comando falla

# Instalar dependencias con pip (Render usa pip por defecto)
pip install --upgrade pip
pip install -r requirements.txt

# Recopilar archivos estaticos (admin, DRF browsable API, etc.)
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Cargar estados de apuesta por defecto
python manage.py seed_bet_statuses
