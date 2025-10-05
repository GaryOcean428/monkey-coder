#!/bin/bash
# Analyze build performance trends
# Reads build-history.csv and generates statistics

LOG_DIR="monitoring/build-times"
HISTORY_FILE="${LOG_DIR}/build-history.csv"
REPORT_FILE="${LOG_DIR}/performance-report.txt"

if [ ! -f "${HISTORY_FILE}" ]; then
    echo "No build history found at ${HISTORY_FILE}"
    exit 1
fi

# Create header if needed
if [ ! -s "${HISTORY_FILE}" ]; then
    echo "timestamp,status,duration_seconds" > "${HISTORY_FILE}"
fi

# Calculate statistics
TOTAL_BUILDS=$(wc -l < "${HISTORY_FILE}")
SUCCESS_BUILDS=$(grep -c "SUCCESS" "${HISTORY_FILE}" || true)
FAILED_BUILDS=$(grep -c "FAILED" "${HISTORY_FILE}" || true)

# Get average duration (last 10 builds)
AVG_DURATION=$(tail -10 "${HISTORY_FILE}" | awk -F',' '{sum+=$3; count++} END {if(count>0) print sum/count; else print 0}')
AVG_MINUTES=$(echo "${AVG_DURATION}" | awk '{print int($1/60)}')
AVG_SECONDS=$(echo "${AVG_DURATION}" | awk '{print int($1%60)}')

# Get fastest and slowest builds
FASTEST=$(awk -F',' 'NR>1 && $2=="SUCCESS" {print $3}' "${HISTORY_FILE}" | sort -n | head -1)
SLOWEST=$(awk -F',' 'NR>1 && $2=="SUCCESS" {print $3}' "${HISTORY_FILE}" | sort -rn | head -1)

# Generate report
cat > "${REPORT_FILE}" << EOF
Build Performance Report
Generated: $(date)
========================================

Summary:
  Total Builds: ${TOTAL_BUILDS}
  Successful:   ${SUCCESS_BUILDS}
  Failed:       ${FAILED_BUILDS}

Performance (Last 10 Builds):
  Average Time: ${AVG_MINUTES}m ${AVG_SECONDS}s
  Fastest:      ${FASTEST}s
  Slowest:      ${SLOWEST}s

Recent Builds:
$(tail -5 "${HISTORY_FILE}" | awk -F',' '{print "  " $1 " - " $2 " (" $3 "s)"}')

========================================
EOF

# Display report
cat "${REPORT_FILE}"
