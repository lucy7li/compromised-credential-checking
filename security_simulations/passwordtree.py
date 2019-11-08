from math import ceil
from ncls import NCLS64
from pwmodel.readpw import Passwords
from random import randrange
import csv
import numpy as np
import os
import pandas as pd
import pwmodel as pwm

"""
CONSTANTS; actual numbers have been replaced by 0
"""
# file containing list of passwords and counts
leak_pw_fname = ''

# total count of passwords in data
TOTAL_F = 0

# 1 - histogram proportion of top N passwords
REM_HIST = 0

# 1 - n-gram proportion of top N passwords
REM_NGRAM = 0

# frequency of top \bar{q}th password
NTH_FREQ = 0

NORM_FACTOR = REM_HIST / REM_NGRAM

# probabilities of top x passwords, for x=1, 10, 100, 1000
q_probs = {1:0, 10:0, 100:0, 1000:0}

"""
Stores bucket ranges for passwords
"""
class PasswordTree:
    # map from _id: (start, size) interval information
    _interval_data = {}

    """
    params: num_buckets: total num of buckets 
            q: security parameter (estimated guessing budget)
            passwords: data structure (contains pw and freq info)
            tsv_path: path to file that contains password frequency, n-gram probability, hash values
    result: interval tree is created using pw and frequency info from passwords dist
    """
    def __init__(self, num_buckets, q, tsv_path):
        self._q = q
        self._num_buckets = num_buckets

        # search for file stored to load data from 
        self.__get_fnames__(tsv_path)

        self._ngmodel = pwm.NGramPw(n=3, pwfilename=leak_pw_fname)

        self._count_n = NTH_FREQ
        self._freq_q = q_probs[self._q]
        self._norm_factor = NORM_FACTOR
        self._bucket_factor = self._num_buckets / self._freq_q

        if os.path.exists(self._file_intervals) and os.path.exists(self._file_interval_sizes):
            self.__load_data__()
        else: 
            self.pw_data = pd.read_csv(tsv_path, sep='\t',header=None, names=['id','pw','freq','ng-prob','hash'], engine='python', error_bad_lines=False, quoting=csv.QUOTE_NONE).set_index('id')
            self.__create_new_tree__()

    """
    get file names where data is stored / will be stored
    """
    def __get_fnames__(self, tsv_path):
        tsv_path_base = os.path.basename(tsv_path).split('.',1)[0] 
        # directory to store files in
        storage_dir = ''

        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        self._fbasename = str(self._q)+'_'+str(self._num_buckets)+'_'+tsv_path_base
        self._file_intervals = os.path.join(storage_dir, self._fbasename + '_intervals.csv')
        self._file_interval_sizes = os.path.join(storage_dir, self._fbasename + '_interval_sizes.csv')

    """
    load data from files
    """
    def __load_data__(self):
        interval_df = pd.read_csv(self._file_intervals)
        self._interval_size_df = pd.read_csv(self._file_interval_sizes, dtype={'pw':'str'}).set_index('id')
        self._tree = NCLS64(interval_df['start'].values, interval_df['end'].values, interval_df['id'].values)

    """ 
    create tree from scratch
    """
    def __create_new_tree__(self):
        interval_sizes = []
        interval_tuples = []
        pws = []
        ids_arr = []
        weights = []

        for index, row in self.pw_data.iterrows():
            _id, pw, freq, ngprob, sha1 = row['id'], row['pw'], row['freq'], row['ng-prob'], row['hash']

            interval_start = (int(sha1[:8],16) & int('fffffffc',16)) >> 2
            norm_prob = self.get_norm_prob(pw, freq, ngprob=ngprob)
            interval_size = min(self._num_buckets, max(ceil(self._bucket_factor*norm_prob), 1))

            pws += [pw]
            ids_arr += [_id]
            weights += [norm_prob / interval_size]
            interval_sizes += [interval_size]
            interval_tuples += self.__get_tuple__(interval_start, interval_size, _id)

        [starts, ends, ids] = list(zip(*interval_tuples))

        self._tree = NCLS64(np.array(starts),np.array(ends),np.array(ids))

        interval_df = pd.DataFrame(data={'id':ids, 'start':starts,'end':ends})
        interval_df.to_csv(self._file_intervals)

        self._interval_size_df = pd.DataFrame(data={'id':ids_arr, 'pw':pws,'size':interval_sizes, 'weight':weights})
        self._interval_size_df.to_csv(self._file_interval_sizes)


    def get_ngram_prob(self, pw):
        return self._ngmodel.prob(pw)


    def __get_tuple__(self, start, size, _id):
        if size > self._num_buckets:
            size = self._num_buckets
            start = 0
        end = (start + size - 1) % self._num_buckets # last bucket
        if end < start:
            return [[start, self._num_buckets, _id], [0, end+1, _id]]
        else:
            return [[start, end+1, _id]]
 
    """
    param: bucket number
    return: all passwords (ids) in that bucket, up to limit
    """
    def get_bucket(self, bucket_num, limit=None):
        print('Getting bucket {}...'.format(bucket_num))
        starts,ends = np.array([bucket_num]), np.array([bucket_num+1])
        bucket_list = []
        for index in self._tree.all_overlaps_both(starts,ends,np.array([0]))[1]:
            bucket_list += [(float(self._interval_size_df.loc[index, 'weight']), str(self._interval_size_df.loc[index, 'pw']))]
        if limit == None:
            limit = len(bucket_list)
        return sorted(bucket_list,reverse=True)[:limit]


    def get_bucket_size(self, bucket_num):
        starts, ends = np.array([bucket_num]), np.array([bucket_num+1])
        return len(self._tree.all_overlaps_both(starts,ends,np.array([0]))[1])


    """
    retrieve interval information for a pw id
    (start, size)
    """
    def get_interval(self, _id):
        if _id not in self._interval_data:
            interval_start = (int(sha1[:8],16) & int('fffffffc',16)) >> 2
            freq = self.get_norm_prob(self._passwords.id2pw(_id), self._passwords.id2freq(_id))
            interval_size = min(self._num_buckets, max(ceil(self._num_buckets*freq/self._freq_q), 1))
            self._interval_data[_id] = (interval_start, interval_size)
        elif self._interval_data[_id][1] > self._num_buckets:
            self._interval_data[_id][1] = self._num_buckets
        return self._interval_data[_id]


    def get_random_bucket(self, w):
        _id = self._passwords.pw2id(w)
        (start, size) = self.get_interval(_id)
        return (randrange(start, start+size) % self._num_buckets)


    def get_norm_prob(self, w, w_count, ngprob=None):
        if w_count >= self._count_n:
            return w_count / TOTAL_F
        else:
            try:
                if ngprob == None:
                    return self._ngmodel.prob(w) * self._norm_factor
                else:
                    return ngprob * self._norm_factor
            except:
                return 0

