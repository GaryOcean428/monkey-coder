#!/bin/bash
# Build timing and performance monitoring
# Usage: ./scripts/time-build.sh [build-command]

set -e

BUILD_CMD=${1:-"yarn build"}
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="monitoring/build-times"
LOG_FILE="${LOG_DIR}/build-${TIMESTAMP}.log"

# Create monitoring directory
mkdir -p "${LOG_DIR}"

echo "🕐 Starting build timing..."
echo "Command: ${BUILD_CMD}"
echo "Log: ${LOG_FILE}"
echo ""

# Capture start time
START_TIME=$(date +%s)
START_TIME_HUMAN=$(date +"%Y-%m-%d %H:%M:%S")

# Run build and capture output
echo "Build started at: ${START_TIME_HUMAN}" > "${LOG_FILE}"
echo "Command: ${BUILD_CMD}" >> "${LOG_FILE}"
echo "----------------------------------------" >> "${LOG_FILE}"

if eval "${BUILD_CMD}" 2>&1 | tee -a "${LOG_FILE}"; then
    STATUS="SUCCESS"
    EXIT_CODE=0
else
    STATUS="FAILED"
    EXIT_CODE=1
fi

# Calculate duration
END_TIME=$(date +%s)
END_TIME_HUMAN=$(date +"%Y-%m-%d %H:%M:%S")
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Log results
echo "----------------------------------------" >> "${LOG_FILE}"
echo "Build finished at: ${END_TIME_HUMAN}" >> "${LOG_FILE}"
echo "Status: ${STATUS}" >> "${LOG_FILE}"
echo "Duration: ${MINUTES}m ${SECONDS}s" >> "${LOG_FILE}"

# Display summary
echo ""
echo "📊 Build Summary"
echo "----------------------------------------"
echo "Status:   ${STATUS}"
echo "Duration: ${MINUTES}m ${SECONDS}s"
echo "Log:      ${LOG_FILE}"

# Update build history
echo "${TIMESTAMP},${STATUS},${DURATION}" >> "${LOG_DIR}/build-history.csv"

# Generate performance report
./scripts/analyze-build-performance.sh

exit ${EXIT_CODE}
