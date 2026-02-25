#!/usr/bin/env bash
set -euo pipefail

# Database restore script for Gym Platform
# Usage: ./scripts/restore_db.sh <backup_file>
#
# Environment variables:
#   DATABASE_URL - PostgreSQL connection string

BACKUP_FILE="${1:-}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

echo "WARNING: This will overwrite the current database."
echo "Restoring from: ${BACKUP_FILE}"
read -rp "Continue? [y/N] " confirm

if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo "Restoring database..."
gunzip -c "${BACKUP_FILE}" | psql "${DATABASE_URL}" --quiet

echo "Restore complete from: ${BACKUP_FILE}"
