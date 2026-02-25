#!/usr/bin/env bash
set -euo pipefail

# Database backup script for Gym Platform
# Usage: ./scripts/backup_db.sh [output_dir]
#
# Environment variables:
#   DATABASE_URL - PostgreSQL connection string
#   GCS_BUCKET   - (optional) GCS bucket for remote backup upload

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${OUTPUT_DIR}/gym_db_${TIMESTAMP}.sql.gz"

mkdir -p "${OUTPUT_DIR}"

echo "Starting database backup..."

# Extract connection details from DATABASE_URL
if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

# pg_dump with compression
pg_dump "${DATABASE_URL}" --no-owner --no-privileges | gzip > "${BACKUP_FILE}"

echo "Backup saved: ${BACKUP_FILE}"
echo "Size: $(du -h "${BACKUP_FILE}" | cut -f1)"

# Upload to GCS if bucket is configured
if [ -n "${GCS_BUCKET:-}" ]; then
    echo "Uploading to gs://${GCS_BUCKET}/backups/..."
    gsutil cp "${BACKUP_FILE}" "gs://${GCS_BUCKET}/backups/"
    echo "Remote backup complete"
fi

# Retention: keep last 30 local backups
BACKUP_COUNT=$(ls -1 "${OUTPUT_DIR}"/gym_db_*.sql.gz 2>/dev/null | wc -l)
if [ "${BACKUP_COUNT}" -gt 30 ]; then
    ls -1t "${OUTPUT_DIR}"/gym_db_*.sql.gz | tail -n +31 | xargs rm -f
    echo "Cleaned old backups (kept last 30)"
fi

echo "Backup complete: ${BACKUP_FILE}"
