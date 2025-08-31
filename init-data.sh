#!/bin/bash
set -e

# Create the non-root user and database for n8n
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ${POSTGRES_NON_ROOT_USER:-n8n} WITH PASSWORD '${POSTGRES_NON_ROOT_PASSWORD:-REDACTED_PASSWORD}';
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB:-n8n} TO ${POSTGRES_NON_ROOT_USER:-n8n};
    GRANT ALL PRIVILEGES ON SCHEMA public TO ${POSTGRES_NON_ROOT_USER:-n8n};
    ALTER USER ${POSTGRES_NON_ROOT_USER:-n8n} CREATEDB;
EOSQL

echo "PostgreSQL user ${POSTGRES_NON_ROOT_USER:-n8n} created successfully with access to database ${POSTGRES_DB:-n8n}"