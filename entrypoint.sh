#!/bin/bash

# Wait for the PostgreSQL database to be ready
while ! pg_isready -h $HOST -p $PORT -U $USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Check if the database exists
if psql -h $HOST -p $PORT -U $USER -lqt | cut -d \| -f 1 | grep -qw $DATABASE; then
  echo "Database $DATABASE already exists"
else
  echo "Database $DATABASE does not exist, initializing..."
  # Initialize the database
  odoo -i base --database=$DATABASE --without-demo=all --stop-after-init
fi

# Install or update the specified modules
echo "Installing or updating modules..."
odoo -i unityplan,unityplan_website,unityplan_country_manager,unityplan_website_forum,unityplan_website_courses --database=$DATABASE --stop-after-init

# Start Odoo
exec "$@"