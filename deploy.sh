#!/usr/bin/sh

VENV="web_env"

rm -rf $VENV
echo " ===> Creating new virtual environment in ${VENV}..."
python -m venv $VENV
echo " ===> Installing dependencies..."
$VENV/bin/pip install -r requirements.txt

echo " -------------------------------"
echo " "
echo " ===> Starting gunicorn server..."
$VENV/bin/gunicorn -w 4 -b 0.0.0.0:2024 'web:deploy()'

