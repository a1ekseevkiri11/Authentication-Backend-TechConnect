#!/bin/sh


echo "Applying migrations..."

alembic upgrade head

echo "Migrations applied successfully."