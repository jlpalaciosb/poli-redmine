#!/bin/bash

echo

echo "--- Vaciar la base de datos ..."
python3 manage.py flush --no-input

echo; echo

echo "--- Aplicar migrations ..."
python3 manage.py migrate

echo; echo

echo "--- Poblar la base de datos ..."
python3 manage.py shell < datos_de_prueba/poblar.py

echo
