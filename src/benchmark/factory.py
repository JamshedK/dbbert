'''
Created on May 12, 2021

@author: immanueltrummer
'''
import configparser
import benchmark.evaluate
import search.objectives


def from_file(config, dbms):
    """ Generate benchmark object from configuration file. 
    
    Args:
        config: describes the benchmark to generate
        dbms: benchmark executed on this DBMS
        
    Returns:
        object representing configured benchmark
    """
    bench_type = config['BENCHMARK']['type']
    if bench_type == 'olap':
        path_to_queries = config['BENCHMARK']['queries']
        bench = benchmark.evaluate.OLAP(dbms, path_to_queries)
    elif bench_type == 'oltp':
        bench = benchmark.evaluate.BenchBase(config, dbms)
    else:
        template_db = config['DATABASE']['template_db']
        target_db = config['DATABASE']['target_db']
        oltp_home = config['BENCHMARK']['oltp_home']
        oltp_config = config['BENCHMARK']['oltp_config']
        oltp_result = config['BENCHMARK']['oltp_result']
        reset_every = int(config['BENCHMARK']['reset_every'])
        bench = benchmark.evaluate.TpcC(
            oltp_home, oltp_config, oltp_result, 
            dbms, template_db, target_db, reset_every)
    return bench


def from_args(args, dbms):
    """ Generate benchmark object from command line arguments.
    
    Args:
        args: dictionary containing command line arguments.
        dbms: represents database system executing benchmark.
    
    Returns:
        tuple of optimization objective and benchmark.
    """
    if hasattr(args, 'oltp_config') and args.oltp_config:
        config = configparser.ConfigParser()
        config.read(args.oltp_config)
        objective = search.objectives.Objective.THROUGHPUT
        bench = benchmark.evaluate.BenchBase(config, dbms)
        return objective, bench
    elif args.query_path is not None:
        objective = search.objectives.Objective.TIME
        bench = benchmark.evaluate.OLAP(dbms, args.query_path)
        return objective, bench
    else:
        raise ValueError('Must provide either --oltp_config or query_path!')