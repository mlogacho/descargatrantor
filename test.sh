#!/bin/bash
echo "Preparando el entorno..."
source venv/bin/activate
echo "Ejecutando script de prueba..."
python test_download.py
