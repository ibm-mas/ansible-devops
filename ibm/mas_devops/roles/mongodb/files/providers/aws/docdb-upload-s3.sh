#!/bin/bash
# =============================================================================
# AWS DocumentDB S3 Upload Script
# =============================================================================
# This script uploads backup files to AWS S3
#
# Required Environment Variables:
#   S3_BUCKET           - S3 bucket name
#   S3_PREFIX           - S3 prefix/folder path
#   AWS_REGION          - AWS region
#   SOURCE_FILE         - Path to file to upload
#   LOG_FILE            - Path to log file
#
# Optional Environment Variables:
#   S3_STORAGE_CLASS    - S3 storage class (default: STANDARD)
#   S3_ENCRYPTION       - Server-side encryption (default: AES256)
#
# Exit Codes:
#   0 - Success
#   1 - Missing required environment variables
#   2 - Source file not found
#   3 - AWS CLI upload failed
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
    
    [[ -z "${S3_BUCKET}" ]] && missing_vars+=("S3_BUCKET")
    [[ -z "${S3_PREFIX}" ]] && missing_vars+=("S3_PREFIX")
    [[ -z "${AWS_REGION}" ]] && missing_vars+=("AWS_REGION")
    [[ -z "${SOURCE_FILE}" ]] && missing_vars+=("SOURCE_FILE")
    [[ -z "${LOG_FILE}" ]] && missing_vars+=("LOG_FILE")
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Set defaults for optional variables
    S3_STORAGE_CLASS="${S3_STORAGE_CLASS:-STANDARD}"
    S3_ENCRYPTION="${S3_ENCRYPTION:-AES256}"
    
    log_info "Environment validation completed"
}

# Verify source file exists
verify_source_file() {
    if [[ ! -f "${SOURCE_FILE}" ]]; then
        log_error "Source file not found: ${SOURCE_FILE}"
        exit 2
    fi
    
    local file_size=$(stat -f%z "${SOURCE_FILE}" 2>/dev/null || stat -c%s "${SOURCE_FILE}" 2>/dev/null || echo "0")
    local file_size_human=$(du -sh "${SOURCE_FILE}" | cut -f1)
    
    log_info "Source file verified: ${SOURCE_FILE}"
    log_info "File size: ${file_size_human} (${file_size} bytes)"
}

# Upload file to S3
upload_to_s3() {
    local filename=$(basename "${SOURCE_FILE}")
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${filename}"
    
    log_info "Starting S3 upload..."
    log_info "Source: ${SOURCE_FILE}"
    log_info "Destination: ${s3_path}"
    log_info "Region: ${AWS_REGION}"
    log_info "Storage Class: ${S3_STORAGE_CLASS}"
    log_info "Encryption: ${S3_ENCRYPTION}"
    
    # Build AWS CLI command
    local aws_cmd="aws s3 cp \"${SOURCE_FILE}\" \"${s3_path}\" \
        --region ${AWS_REGION} \
        --storage-class ${S3_STORAGE_CLASS} \
        --server-side-encryption ${S3_ENCRYPTION}"
    
    # Add metadata if provided
    if [[ -n "${S3_METADATA}" ]]; then
        aws_cmd="${aws_cmd} --metadata ${S3_METADATA}"
    fi
    
    # Execute upload
    if eval "${aws_cmd}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_info "Upload completed successfully"
        log_info "S3 URI: ${s3_path}"
    else
        log_error "AWS CLI upload failed"
        exit 3
    fi
}

# Verify upload
verify_upload() {
    local filename=$(basename "${SOURCE_FILE}")
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${filename}"
    
    log_info "Verifying upload..."
    
    if aws s3 ls "${s3_path}" --region "${AWS_REGION}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_info "Upload verification successful"
        
        # Get S3 object details
        local s3_size=$(aws s3 ls "${s3_path}" --region "${AWS_REGION}" | awk '{print $3}')
        local local_size=$(stat -f%z "${SOURCE_FILE}" 2>/dev/null || stat -c%s "${SOURCE_FILE}" 2>/dev/null || echo "0")
        
        if [[ "${s3_size}" == "${local_size}" ]]; then
            log_info "File size matches: ${s3_size} bytes"
        else
            log_warn "File size mismatch - Local: ${local_size}, S3: ${s3_size}"
        fi
    else
        log_warn "Could not verify upload (file may still be uploaded successfully)"
    fi
}

# Generate S3 presigned URL (optional)
generate_presigned_url() {
    if [[ "${GENERATE_PRESIGNED_URL}" == "true" ]]; then
        local filename=$(basename "${SOURCE_FILE}")
        local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${filename}"
        local expiration="${PRESIGNED_URL_EXPIRATION:-3600}"
        
        log_info "Generating presigned URL (expires in ${expiration} seconds)..."
        
        if presigned_url=$(aws s3 presign "${s3_path}" --region "${AWS_REGION}" --expires-in "${expiration}" 2>&1); then
            log_info "Presigned URL: ${presigned_url}"
            echo "${presigned_url}" > "${SOURCE_FILE}.presigned-url"
        else
            log_warn "Failed to generate presigned URL"
        fi
    fi
}

# Main execution
main() {
    log_info "=========================================="
    log_info "AWS S3 Upload Script"
    log_info "=========================================="
    
    validate_env
    verify_source_file
    upload_to_s3
    verify_upload
    generate_presigned_url
    
    log_info "=========================================="
    log_info "S3 upload completed successfully"
    log_info "=========================================="
    
    exit 0
}

# Run main function
main "$@"

# Made with Bob
