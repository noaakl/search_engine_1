import os
from os import listdir
from os.path import isfile, join

import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.index = 0
        self.files = []
        self.__read_all_files()

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

    def __read_all_files(self):
        if os.path.isfile(self.corpus_path):
            self.files.append(self.corpus_path)

        else:
            for files in os.walk(self.corpus_path, topdown=False):
                for file in files[2]:
                    try:
                        if(file.endswith(".parquet")):
                            rel_dir = os.path.relpath(files[0],self.corpus_path)
                            rel_file = os.path.join(rel_dir,file)
                            self.files.append(rel_file)
                    except:
                        continue
        self.index = len(self.files)-1
        if(self.index < 0 ): self.index = 0

    def get_next_file(self):
        if(self.index < 0 ): return None
        else:
            file = self.files[self.index]
            self.index -= 1
            return self.read_file(file)
