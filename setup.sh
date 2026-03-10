#!/bin/bash

echo "Setting up MIT ADT Mess Management System..."
echo ""

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Running database migrations..."
python manage.py migrate

echo ""
echo "Step 3: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "Setup complete!"
echo ""
echo "To start the server, run: ./start_server.sh"
echo "Or manually run: python manage.py runserver"
echo ""
echo "API Documentation will be available at: http://127.0.0.1:8000/api/docs/"
