#!/bin/bash

# Navigate to project root (one level up from scripts/)
cd "$(dirname "$0")/.." || exit 1

mkdir -p logs/tpch_logs

run_dbbert() {
    local run_num=$1
    local logfile="logs/tpch_logs/run${run_num}.log"

    echo "Starting DB-BERT run ${run_num} at $(date)" | tee "$logfile"
    echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$logfile"
    echo "Start time (Unix): $(date +%s)" >> "$logfile"

    PYTHONPATH=src python3.9 src/run/run_dbbert.py \
        demo_docs/postgres100 \
        32000000000 \
        300000000000 \
        4 \
        pg \
        tpch_1_template \
        postgres \
        123456 \
        "sudo systemctl restart postgresql" \
        workloads/tpch_220.sql \
        --timeout_s=34000 \
        --result_path_prefix="dbbert_results_test${run_num}_" \
        --recover_cmd="sudo rm /var/lib/postgresql/14/main/postgresql.auto.conf" \
        >> "$logfile" 2>&1
    local exit_code=$?

    echo "End time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$logfile"
    echo "End time (Unix): $(date +%s)" >> "$logfile"
    echo "Finished DB-BERT run ${run_num} at $(date). Exit code: $exit_code" >> "$logfile"
    echo "Completed run ${run_num} with exit code $exit_code"
}

echo "Starting sequential DB-BERT TPC-H runs..."

for i in 1; do
    run_dbbert $i
done

echo "All runs completed!"
echo "Results: dbbert_results_test1__performance, dbbert_results_test1__configure, ..."
echo "Logs: logs/tpch_logs/"
