#!/bin/bash
# =============================================================================
# AWS DocumentDB Backup Script
# =============================================================================
# This script performs a backup of AWS DocumentDB using mongodump
#
# Required Environment Variables:
#   DOCDB_HOST          - DocumentDB cluster endpoint
#   DOCDB_PORT          - DocumentDB port (default: 27017)
#   DOCDB_USERNAME      - DocumentDB username
#   DOCDB_PASSWORD      - DocumentDB password
#   DOCDB_CA_CERT       - Path to CA certificate file
#   BACKUP_DIR          - Directory to store backup files
#   LOG_FILE            - Path to log file
#
# Optional Environment Variables:
#   DOCDB_AUTH_DB       - Authentication database (default: admin)
#   BACKUP_DATABASES    - Comma-separated list of databases to backup (default: all)
#
# Exit Codes:
#   0 - Success
#   1 - Missing required environment variables
#   2 - mongodump command failed
#   3 - Backup directory creation failed
# =============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

# Validate required environment variables
validate_env() {
    local missing_vars=()
    
    [[ -z "${DOCDB_HOST}" ]] && missing_vars+=("DOCDB_HOST")
    [[ -z "${DOCDB_USERNAME}" ]] && missing_vars+=("DOCDB_USERNAME")
    [[ -z "${DOCDB_PASSWORD}" ]] && missing_vars+=("DOCDB_PASSWORD")
    [[ -z "${DOCDB_CA_CERT}" ]] && missing_vars+=("DOCDB_CA_CERT")
    [[ -z "${BACKUP_DIR}" ]] && missing_vars+=("BACKUP_DIR")
    [[ -z "${LOG_FILE}" ]] && missing_vars+=("LOG_FILE")
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Set defaults for optional variables
    DOCDB_PORT="${DOCDB_PORT:-27017}"
    DOCDB_AUTH_DB="${DOCDB_AUTH_DB:-admin}"
    
    log_info "Environment validation completed"
}

# Verify CA certificate exists
verify_ca_cert() {
    if [[ ! -f "${DOCDB_CA_CERT}" ]]; then
        log_error "CA certificate not found at: ${DOCDB_CA_CERT}"
        exit 1
    fi
    log_info "CA certificate verified: ${DOCDB_CA_CERT}"
}

# Create backup directory
create_backup_dir() {
    if ! mkdir -p "${BACKUP_DIR}"; then
        log_error "Failed to create backup directory: ${BACKUP_DIR}"
        exit 3
    fi
    log_info "Backup directory created: ${BACKUP_DIR}"
}

# Execute mongodump
execute_mongodump() {
    log_info "Starting mongodump backup..."
    log_info "Target: ${DOCDB_HOST}:${DOCDB_PORT}"
    log_info "Output directory: ${BACKUP_DIR}"
    
    local mongodump_cmd="mongodump \
        --host=\"${DOCDB_HOST}:${DOCDB_PORT}\" \
        --username=\"${DOCDB_USERNAME}\" \
        --password=\"${DOCDB_PASSWORD}\" \
        --authenticationDatabase=${DOCDB_AUTH_DB} \
        --ssl \
        --sslCAFile=\"${DOCDB_CA_CERT}\" \
        --out=\"${BACKUP_DIR}\""
    
    # Add specific databases if provided
    if [[ -n "${BACKUP_DATABASES}" ]]; then
        log_info "Backing up specific databases: ${BACKUP_DATABASES}"
        # Convert comma-separated list to array
        IFS=',' read -ra DBS <<< "${BACKUP_DATABASES}"
        for db in "${DBS[@]}"; do
            db=$(echo "$db" | xargs) # trim whitespace
            log_info "Backing up database: ${db}"
            if ! mongodump \
                --host="${DOCDB_HOST}:${DOCDB_PORT}" \
                --username="${DOCDB_USERNAME}" \
                --password="${DOCDB_PASSWORD}" \
                --authenticationDatabase=${DOCDB_AUTH_DB} \
                --ssl \
                --sslCAFile="${DOCDB_CA_CERT}" \
                --db="${db}" \
                --out="${BACKUP_DIR}" 2>&1 | tee -a "${LOG_FILE}"; then
                log_error "Failed to backup database: ${db}"
                exit 2
            fi
        done
    else
        log_info "Backing up all databases"
        if ! eval "${mongodump_cmd}" 2>&1 | tee -a "${LOG_FILE}"; then
            log_error "mongodump command failed"
            exit 2
        fi
    fi
    
    log_info "mongodump completed successfully"
}

# Get backup statistics
get_backup_stats() {
    log_info "Collecting backup statistics..."
    
    # Count databases
    local db_count=$(find "${BACKUP_DIR}" -maxdepth 1 -type d | wc -l)
    db_count=$((db_count - 1)) # Exclude the backup dir itself
    
    # Get total size
    local total_size=$(du -sh "${BACKUP_DIR}" | cut -f1)
    
    # List backed up databases
    log_info "Backup Statistics:"
    log_info "  - Total databases: ${db_count}"
    log_info "  - Total size: ${total_size}"
    log_info "  - Backed up databases:"
    
    for db_dir in "${BACKUP_DIR}"/*; do
        if [[ -d "${db_dir}" ]]; then
            local db_name=$(basename "${db_dir}")
            local db_size=$(du -sh "${db_dir}" | cut -f1)
            log_info "    * ${db_name} (${db_size})"
        fi
    done
}

# Main execution
main() {
    log_info "=========================================="
    log_info "AWS DocumentDB Backup Script"
    log_info "=========================================="
    
    validate_env
    verify_ca_cert
    create_backup_dir
    execute_mongodump
    get_backup_stats
    
    log_info "=========================================="
    log_info "Backup completed successfully"
    log_info "=========================================="
    
    exit 0
}

# Run main function
main "$@"

# Made with Bob
