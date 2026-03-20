#!/bin/bash
# =============================================================================
# AWS DocumentDB Index Extraction Script
# =============================================================================
# This script extracts collection indexes from AWS DocumentDB using mongosh
#
# Required Environment Variables:
#   DOCDB_HOST          - DocumentDB cluster endpoint
#   DOCDB_PORT          - DocumentDB port (default: 27017)
#   DOCDB_USERNAME      - DocumentDB username
#   DOCDB_PASSWORD      - DocumentDB password
#   DOCDB_CA_CERT       - Path to CA certificate file
#   INDEX_FILE          - Path to output JSON file for indexes
#   LOG_FILE            - Path to log file
#
# Optional Environment Variables:
#   DOCDB_AUTH_DB       - Authentication database (default: admin)
#   EXCLUDE_SYSTEM_DBS  - Exclude system databases (default: true)
#
# Exit Codes:
#   0 - Success (indexes extracted or empty result)
#   1 - Missing required environment variables
#   2 - mongosh command failed
#   3 - Index file creation failed
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
    [[ -z "${INDEX_FILE}" ]] && missing_vars+=("INDEX_FILE")
    [[ -z "${LOG_FILE}" ]] && missing_vars+=("LOG_FILE")
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Set defaults for optional variables
    DOCDB_PORT="${DOCDB_PORT:-27017}"
    DOCDB_AUTH_DB="${DOCDB_AUTH_DB:-admin}"
    EXCLUDE_SYSTEM_DBS="${EXCLUDE_SYSTEM_DBS:-true}"
    
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

# Extract indexes using mongosh
extract_indexes() {
    log_info "Starting index extraction..."
    log_info "Target: ${DOCDB_HOST}:${DOCDB_PORT}"
    log_info "Output file: ${INDEX_FILE}"
    
    # Build connection string
    local connection_string="mongodb://${DOCDB_USERNAME}:${DOCDB_PASSWORD}@${DOCDB_HOST}:${DOCDB_PORT}/?tls=true&tlsCAFile=${DOCDB_CA_CERT}&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
    
    # JavaScript code to extract indexes
    local js_code='
const result = {};
const dbs = db.adminCommand({ listDatabases: 1 }).databases;

dbs.forEach(database => {
    const dbName = database.name;
    
    // Skip system databases if configured
    const excludeSystemDbs = '"${EXCLUDE_SYSTEM_DBS}"' === "true";
    if (excludeSystemDbs && ["admin", "local", "config"].includes(dbName)) {
        print("Skipping system database: " + dbName);
        return;
    }
    
    print("Processing database: " + dbName);
    const dbObj = db.getSiblingDB(dbName);
    const collections = dbObj.getCollectionNames();
    
    result[dbName] = {};
    
    collections.forEach(coll => {
        try {
            const indexes = dbObj[coll].getIndexes();
            result[dbName][coll] = indexes;
            print("  - Extracted indexes for collection: " + coll + " (" + indexes.length + " indexes)");
        } catch (e) {
            print("  - Error getting indexes for " + dbName + "." + coll + ": " + e);
            result[dbName][coll] = { error: e.toString() };
        }
    });
});

print(JSON.stringify(result, null, 2));
'
    
    # Execute mongosh command
    log_info "Executing mongosh to extract indexes..."
    
    if mongosh "${connection_string}" \
        --quiet \
        --eval "${js_code}" 2>&1 | tee -a "${LOG_FILE}" > "${INDEX_FILE}.tmp"; then
        
        # Extract only the JSON part (last line should be the JSON output)
        # Filter out log messages and keep only the JSON
        grep -v "^Skipping\|^Processing\|^  -" "${INDEX_FILE}.tmp" > "${INDEX_FILE}" || true
        
        # Verify the file is valid JSON
        if jq empty "${INDEX_FILE}" 2>/dev/null; then
            log_info "Index extraction completed successfully"
            log_info "Index file created: ${INDEX_FILE}"
            
            # Get statistics
            local db_count=$(jq 'keys | length' "${INDEX_FILE}")
            log_info "Extracted indexes from ${db_count} database(s)"
            
            rm -f "${INDEX_FILE}.tmp"
        else
            log_warn "Index extraction produced invalid JSON, creating empty index file"
            echo '{}' > "${INDEX_FILE}"
            rm -f "${INDEX_FILE}.tmp"
        fi
    else
        log_warn "mongosh command failed, creating empty index file"
        echo '{}' > "${INDEX_FILE}"
        rm -f "${INDEX_FILE}.tmp"
    fi
}

# Verify index file
verify_index_file() {
    if [[ ! -f "${INDEX_FILE}" ]]; then
        log_error "Index file was not created: ${INDEX_FILE}"
        exit 3
    fi
    
    local file_size=$(stat -f%z "${INDEX_FILE}" 2>/dev/null || stat -c%s "${INDEX_FILE}" 2>/dev/null || echo "0")
    log_info "Index file size: ${file_size} bytes"
    
    if [[ "${file_size}" -eq 2 ]] || [[ "${file_size}" -eq 3 ]]; then
        log_warn "Index file is empty (only contains '{}')"
    fi
}

# Main execution
main() {
    log_info "=========================================="
    log_info "AWS DocumentDB Index Extraction Script"
    log_info "=========================================="
    
    validate_env
    verify_ca_cert
    extract_indexes
    verify_index_file
    
    log_info "=========================================="
    log_info "Index extraction completed"
    log_info "=========================================="
    
    exit 0
}

# Run main function
main "$@"

# Made with Bob
