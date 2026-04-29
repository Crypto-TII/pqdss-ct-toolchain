#!/bin/bash

# FAEST Dudect Measurement Collection Script
# Runs natively on remote machine (not in Docker)
# 1. Compiles test harnesses with --run no
# 2. Runs executables with taskset to collect 50k measurements

set -e

INSTANCES=(
    "faest_128f"
    "faest_128s"
    "faest_192f"
    "faest_192s"
    "faest_256f"
    "faest_256s"
    "faest_em_128f"
    "faest_em_128s"
    "faest_em_192f"
    "faest_em_192s"
    "faest_em_256f"
    "faest_em_256s"
)

TARGET=50000
# FAEST: ~3s per sign, dudect does 2 signs per measurement = ~6s per measurement
TIMEOUT=$((TARGET * 6))

echo "========================================"
echo "FAEST Dudect Measurement Script"
echo "Target: $TARGET measurements per instance"
echo "Timeout per instance: $((TIMEOUT / 3600))h $((TIMEOUT % 3600 / 60))m"
echo "========================================"
echo ""

# Step 1: Compile all instances (--run no)
echo "Step 1: Compiling all instances..."
for inst in "${INSTANCES[@]}"; do
    echo "--- Compiling $inst ---"
    python3 cttoolchain/ct_toolchain.py pqdss-ct-tests \
        --tools dudect --candidate faest --instances "$inst" --run no 2>&1 | tail -5
    
    # Verify executable exists
    exe="./candidates/symmetric/faest/dudect/$inst/faest_sign/dude_crypto_sign"
    if [ -x "$exe" ]; then
        echo "[$inst] OK: executable ready"
    else
        echo "[$inst] ERROR: executable not found!"
        exit 1
    fi
    echo ""
done

# Step 2: Run all instances to collect measurements
echo "Step 2: Running measurements (pinned to CPU 4)..."
for inst in "${INSTANCES[@]}"; do
    echo "----------------------------------------"
    echo "Running: $inst (target: $TARGET measurements)"
    echo "Timeout: ${TIMEOUT}s (~$((TIMEOUT / 3600))h)"
    echo "----------------------------------------"
    
    exe="./candidates/symmetric/faest/dudect/$inst/faest_sign/dude_crypto_sign"
    outdir="./candidates/symmetric/faest/dudect/$inst/faest_sign/"
    
    # Run with taskset (pin to CPU 4) and timeout
    taskset --cpu-list 4 timeout ${TIMEOUT}s "$exe"
    
    # Check progress
    mfile="${outdir}/measurements.txt"
    if [ -f "$mfile" ]; then
        count=$(wc -l < "$mfile")
        echo "[$inst] Completed: $count measurements"
    fi
    echo ""
done

# Final status
echo "========================================"
echo "Final Status:"
echo "========================================"
for inst in "${INSTANCES[@]}"; do
    mfile="./candidates/symmetric/faest/dudect/$inst/faest_sign/measurements.txt"
    if [ -f "$mfile" ]; then
        count=$(wc -l < "$mfile")
        printf "%-20s %6d/%d\n" "$inst" "$count" "$TARGET"
    else
        printf "%-20s %s\n" "$inst" "NOT STARTED"
    fi
done

echo ""
echo "Results location: candidates/symmetric/faest/dudect/"
echo ""
echo "To analyze results:"
echo "  for f in candidates/symmetric/faest/dudect/*/faest_sign/measurements.txt; do"
echo "    echo \"\$f: \$(wc -l < \$f) lines\""
echo "  done"
