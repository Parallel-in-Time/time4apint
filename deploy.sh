#!/usr/bin/sh

VENV="web_env"

[ -d "$VENV" ] && echo " ===> Virtual environment exists already..."

if [ ! -d "$VENV" ]; then
    echo " ===> Creating new virtual environment in ${VENV}..."
    python -m venv $VENV
    echo " ===> Installing dependencies..."
    $VENV/bin/pip install -r requirements.txt
fi

echo " -------------------------------"
echo " "
echo " ===> Starting gunicorn server..."
$VENV/bin/gunicorn -w 4 -b 0.0.0.0 'web:deploy()'

