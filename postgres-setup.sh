#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER"; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is up - executing setup"

# Check if user exists and create if not
USER_EXISTS=$(psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$POSTGRES_NON_ROOT_USER'" || echo "")

if [ "$USER_EXISTS" = "1" ]; then
    echo "User $POSTGRES_NON_ROOT_USER already exists"
else
    echo "Creating user $POSTGRES_NON_ROOT_USER"
    psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
        CREATE USER $POSTGRES_NON_ROOT_USER WITH PASSWORD '$POSTGRES_NON_ROOT_PASSWORD';
        GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_NON_ROOT_USER;
        GRANT ALL PRIVILEGES ON SCHEMA public TO $POSTGRES_NON_ROOT_USER;
        ALTER USER $POSTGRES_NON_ROOT_USER CREATEDB;
EOSQL
    echo "User $POSTGRES_NON_ROOT_USER created successfully"
fi

echo "PostgreSQL setup completed"