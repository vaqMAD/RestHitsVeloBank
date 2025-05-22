#!/usr/bin/env bash
set -e

# A short delay to let Postgres up.
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Migrations
echo "Applying database migrations..."
python manage.py migrate --noinput
python manage.py seed_data

# Conditionally run tests
if [[ "$RUN_TESTS_ON_STARTUP" == "true" ]]; then
  echo "RUN_TESTS_ON_STARTUP is true. Running tests..."
  python manage.py test
else
  echo "RUN_TESTS_ON_STARTUP is not 'true' or not set. Skipping tests."
fi

echo "Starting server..."
exec "$@"