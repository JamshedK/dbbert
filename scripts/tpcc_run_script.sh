#!/bin/bash

cd "$(dirname "$0")/.." || exit 1

mkdir -p logs/tpcc_logs

run_dbbert() {
    local run_num=$1
    local logfile="logs/tpcc_logs/run${run_num}.log"

    echo "Starting DB-BERT TPC-C run ${run_num} at $(date)" | tee "$logfile"

    PYTHONPATH=src python3.9 src/run/run_dbbert.py \
        demo_docs/postgres100 \
        32000000000 \
        300000000000 \
        4 \
        pg \
        tpcc_200 \
        postgres \
        123456 \
        "sudo systemctl restart postgresql" \
        --oltp_config=configs/benchbase_config.ini \
        --timeout_s=25000 \
        --result_path_prefix="dbbert_tpcc_test${run_num}_" \
        --recover_cmd="sudo rm /var/lib/postgresql/14/main/postgresql.auto.conf" \
        >> "$logfile" 2>&1
    local exit_code=$?

    echo "Finished run ${run_num}. Exit code: $exit_code" >> "$logfile"
    echo "Completed run ${run_num} with exit code $exit_code"
}

echo "Starting DB-BERT TPC-C runs..."

for i in 1 2 3; do
    echo "Recovering PostgreSQL and resetting all knobs..."
    bash "$(dirname "$0")/recover_postgres.sh"
    echo "PostgreSQL recovered. Proceeding with run ${i}..."
    run_dbbert $i
done

echo "All runs completed!"
echo "Results: dbbert_tpcc_test1__performance, dbbert_tpcc_test1__configure"
echo "Logs: logs/tpcc_logs/"
