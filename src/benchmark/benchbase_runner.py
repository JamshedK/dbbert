import os
import logging
import time
import json
import shutil

class BenchBaseRunner:
    def __init__(self, args, logger=None):
        self.benchmark_config = args['benchmark_config']
        self.database_config = args['database_config']
        self.logger = logger or logging.getLogger(__name__)
    
    def run_benchmark(self, workload_path, log_file):
        benchmark_name = self.benchmark_config.get('benchmark', 'tpcc')
        workload_name = os.path.splitext(os.path.basename(workload_path))[0]
        
        results_base = "stress_test_results"
        workload_base_dir = os.path.join(results_base, f"{benchmark_name}_results")
        workload_results_dir = os.path.join(workload_base_dir, workload_name)
        os.makedirs(workload_results_dir, exist_ok=True)
        workload_results_dir = os.path.abspath(workload_results_dir)
        
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scripts', 'run_benchmark.sh')
        timestamp = int(time.time())
        config_filename = os.path.basename(workload_path)
        command = f'bash {script_path} {benchmark_name.lower()} {timestamp} {workload_results_dir} {workload_results_dir} {config_filename}'
        
        print(f'Running BenchBase: {benchmark_name}, config: {config_filename}')
        state = os.system(command)
        
        if state != 0:
            print(f'BenchBase error - exit code: {state}')
            return 0.0

        time.sleep(3)
        
        summary_path = self.clean_and_find_summary(workload_results_dir)
        if not summary_path:
            print('No summary.json found')
            return 0.0
        
        throughput = self.parse_summary_json(summary_path)
        print(f'BenchBase {benchmark_name} throughput: {throughput}')
        return throughput
    
    def clean_and_find_summary(self, results_dir):
        summary_path = None
        summary_archive_dir = os.path.join(results_dir, 'summary')
        os.makedirs(summary_archive_dir, exist_ok=True)
        
        # First pass: find and process the new .summary.json
        for file in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file)
            if file.endswith('.summary.json'):
                archived_path = os.path.join(summary_archive_dir, file)
                shutil.copy2(file_path, archived_path)
                final_summary_path = os.path.join(results_dir, 'summary.json')
                shutil.move(file_path, final_summary_path)
                summary_path = final_summary_path

        # Second pass: clean up everything except summary.json and the summary/ dir
        for file in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file)
            if file != 'summary.json' and os.path.isfile(file_path):
                os.remove(file_path)

        return summary_path
    
    def parse_summary_json(self, summary_path):
        try:
            with open(summary_path, 'r') as f:
                data = json.load(f)
            return data["Throughput (requests/second)"]
        except Exception as e:
            print(f'Error parsing summary.json: {e}')
            return 0.0
    