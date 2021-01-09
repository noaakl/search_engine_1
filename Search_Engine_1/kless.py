from configuration import ConfigClass
import pandas as pd

# PUT THE SEARCH ENGINE YOU WANT TO TEST
from search_engine_best import SearchEngine

PATH_TO_BENCHMARK_DATASET_PARQUET = r"data\benchmark_data_train.snappy.parquet"

config = ConfigClass()
se = SearchEngine(config)
se.build_index_from_parquet(PATH_TO_BENCHMARK_DATASET_PARQUET)
query1 = 'Dr. Anthony Fauci wrote in a 2005 paper published in Virology Journal that hydroxychloroquine was effective in treating SARS.	fauci paper hydroxychloroquine sars'
query2 = 'The seasonal flu kills more people every year in the U.S. than COVID-19 has to date. 	flu kills more than covid'
query4 = 'The coronavirus pandemic is a cover for a plan to implant trackable microchips and that the Microsoft co-founder Bill Gates is behind it	gates implant microchips'
query7 = 'Herd immunity has been reached.	Herd immunity reached'
query8 = 'Children are “almost immune from this disease.”	children immune to coronavirus'
n_res, res = se.search(query1)
df = pd.read_parquet(PATH_TO_BENCHMARK_DATASET_PARQUET,
                     engine="pyarrow")

to_return = pd.DataFrame(columns=["query", "tweet_id"])
num = 0
for doc in res:
    if num == 5: break
    print(doc)
    print([w for w in df[df.tweet_id == doc].full_text.tolist()])
    num += 1

