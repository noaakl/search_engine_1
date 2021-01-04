if __name__ == '__main__':
    import os
    import sys
    import re
    from datetime import datetime
    import pandas as pd
    import pyarrow.parquet as pq
    import timeit
    import importlib
    import logging
    logging.basicConfig(filename='part_c_tests.log', level=logging.DEBUG,
                        filemode='w', format='%(levelname)s %(asctime)s: %(message)s')
    import metrics

    def test_file_exists(fn):
        if os.path.exists(fn):
            return True
        logging.error(f'{fn} does not exist.')
        return False

    tid_ptrn = re.compile('\d+')
    def invalid_tweet_id(tid):
        if not isinstance(tid, str):
            tid = str(tid)
        if tid_ptrn.fullmatch(tid) is None:
            return True
        return False

    bench_data_path = os.path.join('data', 'benchmark_data_train.snappy.parquet')
    bench_lbls_path = os.path.join('data', 'benchmark_lbls_train.csv')
    queries_path    = os.path.join('data', 'queries_train.tsv')

    start = datetime.now()
    try:
        # is the report there?
        test_file_exists('report_part_c.docx')
        # is benchmark data under 'data' folder?
        bench_lbls = None
        if not test_file_exists(bench_data_path) or \
            not test_file_exists(bench_lbls_path):
            logging.error("Benchmark data does exist under the 'data' folder.")
            sys.exit(-1)
        else:
            bench_lbls = pd.read_csv(bench_lbls_path, 
                dtype={'query': int, 'tweet': str, 'y_true': int})

        # is queries file under data?
        queries = None
        if not test_file_exists(queries_path):
            logging.error("Queries data not found ~> skipping some tests.")
        else:
            queries = pd.read_csv(os.path.join('data', 'queries_train.tsv'), sep='\t')

        # test for each search engine module
        engine_modules = ['search_engine_' + name for name in ['1','2','best']]
        for engine_module in engine_modules:
            try:
                # does the module file exist?
                if not test_file_exists(engine_module+'.py'):
                    continue
                # try importing the module
                se = importlib.import_module(engine_module)
                engine = se.SearchEngine()
                
                # test building an index and doing so in <1 minute
                build_idx_time = timeit.timeit(
                    "engine.build_index_from_parquet(bench_data_path)",
                    globals=globals(), number=1
                )
                if build_idx_time > 60:
                    logging.error('Parsing and index our *small* benchmark dataset took over a minute!')
                # test loading precomputed model
                engine.load_precomputed_model()

                # test that we can run one query and get results in the format we expect
                n_res, res = engine.search('bioweapon')
                if n_res is None or res is None or n_res < 1 or len(res) < 1:
                    logging.error('basic query for the word bioweapon returned no results')
                else:
                    invalid_tweet_ids = [doc_id for doc_id in res if invalid_tweet_id(doc_id)]
                    if len(invalid_tweet_ids)>0:
                        logging.error("the query 'bioweapon' returned results that are not valid tweet ids: "+str(invalid_tweet_ids[:10]))

                # run multiple queries and test that no query takes > 10 seconds
                queries_results = []
                if queries is not None:
                    for i, row in queries.iterrows():
                        q_id = row['query_id']
                        q_keywords = row['keywords']
                        q_n_res, q_res = None, None
                        q_time = timeit.timeit(
                            "q_n_res, q_res = engine.search(bench_data_path)",
                            globals=globals(), number=1
                        )
                        if q_n_res is None or q_res is None or q_n_res < 1 or len(q_res) < 1:
                            logging.error(f"Query {q_id} with keywords '{q_keywords}' returned no results.")
                        else:
                            invalid_tweet_ids = [doc_id for doc_id in q_res if invalid_tweet_id(doc_id)]
                            if len(invalid_tweet_ids)>0:
                                logging.error(f"Query  {q_id} returned results that are not valid tweet ids: "+str(invalid_tweet_ids[:10]))
                            queries_results.extend([(q_id, str(doc_id)) for doc_id in q_res if not invalid_tweet_ids(doc_id)])
                        if q_time > 10:
                            logging.error(f"Query {q_id} with keywords '{q_keywords}' took more than 10 seconds.")
                queries_results = pd.DataFrame(queries_results, columns=['query', 'tweet'])

                # merge query results with labels benchmark
                q_results_labeled = None
                if bench_lbls is not None and len(queries_results)>0:
                    q_results_labeled = pd.merge(queries_results, bench_lbls,
                        on=['query','tweet'], how='left', suffixes=None)
                    q_results_labeled.rename(columns={'y_true': 'label'})
                
                # test that MAP > 0
                if q_results_labeled is not None:
                    results_map = metrics.map(q_results_labeled)
                    if results_map <= 0 or results_map > 1:
                        logging.error(f'Search results MAP value out of range: {results_map}.')
                
                # test that the average across queries of precision, 
                # precision@5, precision@10, precision@50, and recall 
                # is in (0,1).
                
                if engine_module == 'search_engine_best' and \
                    test_file_exists('idx_bench.pkl'):
                    logging.debug('idx_bench.pkl found!')
                    engine.load_index('idx_bench.pkl')

            except Exception as e:
                logging.error(f'The following error occured while testing the module {engine_module}.')
                logging.error(e, exc_info=True)

    except Exception as e:
        logging.error(e, exc_info=True)

    run_time = datetime.now() - start
    logging.debug(f'Total runtime was: {run_time}')
