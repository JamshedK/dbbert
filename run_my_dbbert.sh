#!/bin/bash

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
    workloads/tpch_22.sql \
    --timeout_s=3000 \
    --recover_cmd="sudo rm /var/lib/postgresql/14/main/postgresql.auto.conf"
