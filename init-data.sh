#!/bin/bash
set -e

# Create the non-root user and database for n8n (with error handling if user exists)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_NON_ROOT_USER:-n8n}') THEN
            CREATE USER ${POSTGRES_NON_ROOT_USER:-n8n} WITH PASSWORD '${POSTGRES_NON_ROOT_PASSWORD:-REDACTED_PASSWORD}';
            GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB:-n8n} TO ${POSTGRES_NON_ROOT_USER:-n8n};
            GRANT ALL PRIVILEGES ON SCHEMA public TO ${POSTGRES_NON_ROOT_USER:-n8n};
            ALTER USER ${POSTGRES_NON_ROOT_USER:-n8n} CREATEDB;
            RAISE NOTICE 'User ${POSTGRES_NON_ROOT_USER:-n8n} created successfully';
        ELSE
            RAISE NOTICE 'User ${POSTGRES_NON_ROOT_USER:-n8n} already exists';
        END IF;
    END
    \$\$;
EOSQL

echo "PostgreSQL user setup completed for ${POSTGRES_NON_ROOT_USER:-n8n}"