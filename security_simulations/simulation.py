from collections import Counter
from collections import defaultdict
from itertools import islice
from math import ceil
from passwordtree import PasswordTree
from pwmodel.readpw import Passwords
from random import sample, randrange
import csv
import getopt
import hashlib
import itertools
import numpy as np
import pandas as pd
import pwmodel as pwm
import string
import sys

hexchars = string.hexdigits[:16]

# result strings
KNOWN_RESULT = 'KNOWN'
TARGET_RESULT = 'TARGET'
GENERAL_RESULT = 'GENERAL'
NOTFOUND_RESULT = 'NOT_FOUND'

# files containing leak password information
# password and counts
leak_pw_file = ''
# password, id, freq, n-gram prob, hash values
leak_pw_tsv_files = []

# files where test data is stored
comp_sample_file_format = ''
uncomp_sample_file_format = ''

corr_sample_file = ''
corr_sample_file_pw2 = ''

site_policy_sample_file_comp = ''
site_policy_sample_file_uncomp = ''

user_mul_pw_file = ''
corr_user_mul_pw_file = ''

site_policy_user_mul_pw_file = ''

# file that contains n-gram model generated passwords
add_pw_file = ''

# file with list of twitter banned passwords
twitter_banlist_file = ''

# files with predictions for tweaked passwords for targeted guessing
predictions_files = []
corr_predictions_files = []
site_policy_predictions_files = []

# where hash prefix buckets are stored
buckets_root = ''

num_trials = 10000

"""parameters for frequency-smoothing bucketization"""
# parameter \bar{q} for FSB
Q_C3S = 1
# number of buckets for FSB
NUM_BUCKETS_C3S = 1
# top N passwords included in every bucket
N = 1
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

passwords = Passwords(leak_pw_file)
ngmodel = pwm.NGramPw(n=3, pwfilename=leak_pw_file)


"""
Regular experiment with test cases from both previously compromised and uncompromised users. 
        hpb: True if doing hash prefix based bucketization, False if doing FSB
"""
def experiment(comp_sample_file, uncomp_sample_file, hpb=False):
    # read test samples from files
    comp_df, uncomp_df = sample_user_pws(comp_sample_file, uncomp_sample_file, num_trials, hpb)

    if comp_df != None:
        get_targeted_guesses(user_mul_pw_file, comp_df, predictions_files,hpb=hpb)

    if hpb:
        # add extra passwords from n-gram model
        if HIBP_PREFIX_LEN == 5:
            comp_df, uncomp_df = add_more_pws(comp_df, uncomp_df)
    else:
        # add passwords by bucket
        comp_df,uncomp_df = add_all_pws(comp_df, uncomp_df=uncomp_df)
        if Q_C3S == 1:
            comp_df, uncomp_df = add_more_pws(comp_df, uncomp_df, hpb=False)

    # get guess ranks of real_pw in guesses, else -1
    guess_ranks = []
    target_guess_ranks = []
    for index, row in uncomp_df.iterrows():
        if not hpb:
            hist_guesses = [w for (weight, w) in sorted(row['hist_guesses'], reverse=True)]
        else:
            hist_guesses = row['hist_guesses']
        guesslist = hist_guesses
        pw = row['pw']
        if pw in guesslist:
            guess_rank = guesslist.index(pw) + 1
        else:
            guess_rank = -1
        guess_ranks += [guess_rank]

    if comp_df != None:
        comp_results = []
        for index, row in comp_df.iterrows():
            if not hpb:
                hist_guesses = [w for (weight, w) in sorted(row['hist_guesses'], reverse=True)]
            else:
                hist_guesses = row['hist_guesses']
            target_guesses = row['target_guesses']
            guesslist = row['known'] + target_guesses + hist_guesses
            pw = row['pw']
            if pw in guesslist:
                guess_rank = guesslist.index(pw) + 1
                if pw in row['known']:
                    comp_results += [KNOWN_RESULT]
                elif pw in target_guesses:
                    comp_results += [TARGET_RESULT]
                else:
                    comp_results += [GENERAL_RESULT]
            else:
                guess_rank = -1
                comp_results += [NOTFOUND_RESULT]
            target_guess_ranks += [guess_rank]
        target_guess_ranks = sorted(target_guess_ranks)
    
    guess_ranks = sorted(guess_ranks)
    if 'bucket_size' in comp_df.columns:
        avg_size = (comp_df['bucket_size'].values.sum() + uncomp_df['bucket_size'].values.sum()) / num_trials
        max_size = max(comp_df['bucket_size'].max(), uncomp_df['bucket_size'].max()) 

    with open(write_fname, 'w+') as f:
        f.write(' '.join(map(str, guess_ranks)))
        f.write('\n')
        if comp_df != None:
            f.write(' '.join(map(str, target_guess_ranks)))
            f.write('\n')
            f.write(' '.join(comp_results))
            if 'bucket_size' in comp_df.columns:
                f.write('\n')
                f.write('avg bucket size: ' + str(avg_size) + ', max: ' + str(max_size))


"""
Baseline guessing experiment
"""
def baseline_experiment(comp_sample_file, uncomp_sample_file):
    comp_df,uncomp_df = sample_baseline_pws(num_trials, comp_sample_file, uncomp_sample_file)

    if comp_df != None:
        get_targeted_guesses(user_mul_pw_file, comp_df, predictions_files,baseline=True)

    comp_df,uncomp_df = get_baseline_ranks(comp_df,uncomp_df)

    if comp_df != None:
        guess_ranks = sorted(comp_df['rank'].values)
        results = comp_df['result'].values
    target_guess_ranks = sorted(uncomp_df['rank'].values)

    with open(write_fname, 'w+') as f:
        if comp_df != None:
            f.write(' '.join(map(str, guess_ranks)))
            f.write('\n')
        f.write(' '.join(map(str, target_guess_ranks)))
        if comp_df != None:
            f.write('\n')
            f.write(' '.join(results))


"""
Baseline experiment for guessing site-policy restricted passwords
"""
def site_policy_baseline_experiment():
    comp_df, uncomp_df = sample_baseline_pws(num_trials, site_policy_sample_file_comp, site_policy_sample_file_uncomp)
    get_targeted_guesses(site_policy_user_mul_pw_file, comp_df, site_policy_predictions_files,baseline=True, site_policy=True)
    comp_df,uncomp_df = get_baseline_ranks(comp_df,uncomp_df, site_policy=True)

    guess_ranks = sorted(comp_df['rank'].values)
    target_guess_ranks = sorted(uncomp_df['rank'].values)
    results = comp_df['result'].values

    with open(write_fname, 'w+') as f:
        f.write(' '.join(map(str, guess_ranks)))
        f.write('\n')
        f.write(' '.join(map(str, target_guess_ranks)))
        f.write('\n')
        f.write(' '.join(results))


"""
General experiment for guessing site-policy restricted passwords
"""
def site_policy_experiment(hpb=False):
    comp_df, uncomp_df = sample_user_pws(\
        site_policy_sample_file_comp, site_policy_sample_file_uncomp, num_trials, hpb)

    get_targeted_guesses(site_policy_user_mul_pw_file, comp_df, site_policy_predictions_files,hpb=hpb)

    if not hpb:
        comp_df,uncomp_df = add_all_pws(comp_df, uncomp_df)

    guess_ranks = []
    target_guess_ranks = []
    banlist = open(twitter_banlist_file, 'r').read().splitlines()
    for index, row in uncomp_df.iterrows():
        if not hpb:
            hist_guesses = [w for (weight, w) in sorted(row['hist_guesses'], reverse=True)]
        else:
            hist_guesses = row['hist_guesses']
        guesslist = list(filter(lambda w: site_policy_filter(w, banlist), hist_guesses))
        pw = row['pw']
        if pw in guesslist:
            guess_rank = guesslist.index(pw) + 1
        else:
            guess_rank = -1
        guess_ranks += [guess_rank]

    comp_results = []
    for index, row in comp_df.iterrows():
        if not hpb:
            hist_guesses = [w for (weight, w) in sorted(row['hist_guesses'], reverse=True)]
        else:
            hist_guesses = row['hist_guesses']
        target_guesses = row['target_guesses']
        guesslist = row['known'] + target_guesses + hist_guesses
        guesslist = list(filter(lambda w: site_policy_filter(w, banlist), guesslist))
        pw = row['pw']
        if pw in guesslist:
            guess_rank = guesslist.index(pw) + 1
            if pw in row['known']:
                comp_results += [KNOWN_RESULT]
            elif pw in target_guesses:
                comp_results += [TARGET_RESULT]
            else:
                comp_results += [GENERAL_RESULT]
        else:
            guess_rank = -1
            comp_results += [NOTFOUND_RESULT]
        target_guess_ranks += [guess_rank]
 
    guess_ranks = sorted(guess_ranks)
    target_guess_ranks = sorted(target_guess_ranks)
    if 'bucket_size' in comp_df.columns:
        avg_size = (comp_df['bucket_size'].values.sum() + uncomp_df['bucket_size'].values.sum()) / num_trials
        max_size = max(comp_df['bucket_size'].max(), uncomp_df['bucket_size'].max()) 

    with open(write_fname, 'w+') as f:
        f.write(' '.join(map(str, guess_ranks)))
        f.write('\n')
        f.write(' '.join(map(str, target_guess_ranks)))
        f.write('\n')
        f.write(' '.join(comp_results))
        if 'bucket_size' in comp_df.columns:
            f.write('\n')
            f.write('avg bucket size: ' + str(avg_size) + ', max: ' + str(max_size))


"""
Experiment for correlated passwords
"""
def corr_experiment(hpb=False):
    from c3s_corr_attack import cal_max
    df = sample_corr_user_pws(corr_sample_file, num_trials, hpb)

    get_targeted_guesses(corr_user_mul_pw_file, df, corr_predictions_files, corr=True, hpb=hpb)

    if not hpb:
        df = add_all_pws_corr(df)

    guess_ranks = []
    for index, row in df.iterrows(): 
        if not hpb:
            hist1 = [w for (weight, w) in sorted(row['hist1'], reverse=True)] 
            hist2 = [w for (weight, w) in sorted(row['hist2'], reverse=True)] 
        else:
            hist1 = row['hist1']
            hist2 = row['hist2']
        L1 = row['target1'] + hist1[:5000] 
        L2 = row['known2'] + row['target2'] + hist2[:5000]
        if len(row['known1']) > 0:
            P1 = np.array([0.4/len(row['known1'])]*len(row['known1']) + list(map(get_prob, L1)))
        else:
            P1 = np.array(list(map(get_prob, L1)))
        L1 = row['known1'] + L1
        if hpb:
            P2 = np.array([1]*len(L2))
        else:
            P2 = np.array(list(map(get_prob, L2)))

        if len(L1) > 0 and len(L2) > 0:
            guesslist = list(cal_max(L1,L2,P1,P2))
        else:
            guesslist = L2

        pw2 = row['pw2']
        if pw2 in guesslist:
            guess_rank = guesslist.index(pw2) + 1
        else:
            guess_rank = -1
        guess_ranks += [guess_rank]

    guess_ranks = sorted(guess_ranks)
    with open(write_fname, 'w+') as f:
        f.write(' '.join(map(str, guess_ranks)))


"""
Gets guess ranks for baseline guessing of passwords
"""
def get_baseline_ranks(comp_df,uncomp_df, site_policy=False):
    if site_policy:
        banlist = open(twitter_banlist_file, 'r').read().splitlines()
    with open(leak_pw_file, 'r') as leak_file:
        rank = 0
        pws = []
        for line in leak_file:
            pw = line.rstrip('\n').split('\t',1)[1]
            if (not site_policy) or (site_policy and site_policy_filter(pw, banlist)):
                rank += 1
                pws += [pw]

        if comp_df != None:
            for index,row in comp_df.iterrows():
                if row['rank'] == -1:
                    try:
                        comp_df.at[index, 'rank'] = pws.index(row['pw']) + row['target_size']  + 1
                        comp_df.at[index, 'result'] = GENERAL_RESULT
                    except:
                        pass
        for index,row in uncomp_df.iterrows():
            try:
                uncomp_df.at[index, 'rank'] = pws.index(row['pw']) + 1
            except:
                pass
    return comp_df,uncomp_df


"""
Convert samples of passwords to dataframe format for baseline guessing simulations
"""
def sample_baseline_pws(num_trials, comp_sample_file, uncomp_sample_file):
    num_trials = int(num_trials / 2)

    if comp_sample_file != '':
        comp_sample_lines = open(comp_sample_file, 'r').read().splitlines()
        pws = []
        users = []
        for line in comp_sample_lines:
            user,pw = line.split('\t',1)
            pws += [pw]
            users += [user]
        comp_df = pd.DataFrame(data={'user':users, 'pw':pws, 'rank':[-1]*num_trials, 'target_size':[0]*num_trials, \
            'known':[[]]*num_trials, 'result':[NOTFOUND_RESULT]*num_trials})
    else:
        comp_df = None

    uncomp_sample_lines = open(uncomp_sample_file, 'r').read().splitlines()
    pws = []
    for line in uncomp_sample_lines:
        user,pw = line.split('\t',1)
        pws += [pw]
    uncomp_df = pd.DataFrame(data={'pw':pws, 'rank':[-1]*num_trials})

    return comp_df, uncomp_df


"""
Convert samples of passwords to dataframe format for general simulation
"""
def sample_user_pws(comp_sample_file, uncomp_sample_file, num_trials, hpb):
    num_trials = int(num_trials / 2)

    if comp_sample_file != '':
        comp_sample_lines = open(comp_sample_file, 'r').read().splitlines()
        users, pws, buckets, sizes = [], [], [], []
        hist_guesses = []
        for line in comp_sample_lines:
            user,pw = line.split('\t',1)
            users += [user]
            pws += [pw]
            if hpb:
                bucket = get_bucket_hibp(pw)
                buckets += [bucket]
                hist_guesses += [read_bucket(bucket)]
                sizes += [len(hist_guesses[-1])]
            else:
                buckets += [get_random_bucket(pw)]
                hist_guesses += [[]]
                sizes += [0]
        comp_df = pd.DataFrame(data={'bucket':buckets, 'user':users, 'pw':pws, 'known':[[]]*num_trials,\
            'target_guesses':[[]]*num_trials, 'hist_guesses':hist_guesses, 'bucket_size':sizes})
        if not hpb:
            comp_df = comp_df.set_index('bucket')
    else:
        comp_df = None

    uncomp_sample_lines = open(uncomp_sample_file, 'r').read().splitlines()
    users, pws, buckets, sizes = [], [], [], []
    hist_guesses = []
    for line in uncomp_sample_lines:
        user,pw = line.split('\t',1)
        users += [user]
        pws += [pw]
        if hpb:
            bucket = get_bucket_hibp(pw)
            buckets += [bucket]
            hist_guesses += [read_bucket(bucket)]
            sizes += [len(hist_guesses[-1])]
        else:
            buckets += [get_random_bucket(pw)]
            hist_guesses += [[]]
            sizes += [0]
    uncomp_df = pd.DataFrame(data={'bucket':buckets, 'user':users, 'pw':pws, \
        'hist_guesses':hist_guesses, 'bucket_size':sizes})
    if not hpb:
        uncomp_df = uncomp_df.set_index('bucket')

    return comp_df, uncomp_df


"""
Convert samples of passwords to dataframe format for correlated password simulation
"""
def sample_corr_user_pws(corr_sample_file, num_trials, hpb):
    lines = open(corr_sample_file, 'r').read().splitlines()
    num_trials = len(lines)
    sample_lines = lines[:num_trials]
    users, pw1s, pw2s, b1s, b2s = [], [], [], [], []
    hist1, hist2 = [], []
    for line in sample_lines:
        user, pw1, pw2 = line.split('\t')
        users += [user]
        pw1s += [pw1]
        pw2s += [pw2]
        if hpb: 
            b1,b2 = get_bucket_hibp(pw1), get_bucket_hibp(pw2)
            b1s += [b1]
            b2s += [b2]
            hist1 += [read_bucket(b1)]
            hist2 += [read_bucket(b2)]
        else:
            b1s += [get_random_bucket(pw1)]
            b2s += [get_random_bucket(pw2)]
            hist1 += [[]]
            hist2 += [[]]
    df = pd.DataFrame(data={'user':users, 'pw1':pw1s, 'pw2':pw2s, 'b1':b1s, 'b2':b2s, 'known1':[[]]*num_trials,\
        'known2':[[]]*num_trials, 'target1':[[]]*num_trials, 'target2':[[]]*num_trials, 'hist1':hist1, 'hist2':hist2})
    return df


"""
Convert samples of passwords to dataframe format for correlated password baseline guessing simulation
"""
def sample_corr_baseline_user_pws(corr_sample_file):
    sample_lines = open(corr_sample_file, 'r').read().splitlines()
    num_trials = len(sample_lines)
    users, pw1s, pw2s = [], [], []
    for line in sample_lines:
        user, pw1, pw2 = line.split('\t')
        users += [user]
        pw1s += [pw1]
        pw2s += [pw2]
    df = pd.DataFrame(data={'user':users, 'pw1':pw1s, 'pw2':pw2s, 'known':[[]]*num_trials,\
        'target':[[]]*num_trials, 'rank':[-1]*num_trials, 'target_size':[0]*num_trials})
    return df


"""
Gets targeted guesses for user-pw pairs using generated guesses
"""
def get_targeted_guesses(user_pw_file, df, pw_files, corr=False, hpb=False, baseline=False, site_policy=False):
    if site_policy:
        banlist = open(twitter_banlist_file, 'r').read().splitlines()
    targets = defaultdict(list)
    with open(user_pw_file, 'r') as readfile: 
        for line in readfile:
            temp = line.rstrip('\n').split('\t')
            user = temp[0]
            pw_list = temp[1:]
            counts = Counter(pw_list)
            pws = sorted(pd.Series(pw_list).drop_duplicates().tolist(), key=lambda word : (-counts[word],-get_prob(word)) )
            for index, row in df[df['user'] == user].iterrows():
                if corr and hpb:
                    df.at[index, 'known1'] = pd.Series(list(get_predictions_hibp(pws, row['b1']))).drop_duplicates().tolist()
                    df.at[index, 'known2'] = pd.Series(list(get_predictions_hibp(pws, row['b2']))).drop_duplicates().tolist()
                elif corr:
                    df.at[index, 'known1'] = pd.Series(list(get_predictions(pws, row['b1']))).drop_duplicates().tolist()
                    df.at[index, 'known2'] = pd.Series(list(get_predictions(pws, row['b2']))).drop_duplicates().tolist()
                elif hpb:
                    df.at[index, 'known'] = pd.Series(list(get_predictions_hibp(pws, row['bucket']))).drop_duplicates().tolist()
                elif baseline:
                    pws = pd.Series(pws).drop_duplicates().tolist()
                    if site_policy:
                        pws = list(filter(lambda w: site_policy_filter(w, banlist), pws))
                    if row['pw'] in pws:
                        df.at[index, 'rank'] = pws.index(row['pw']) + 1
                        df.at[index, 'result'] = KNOWN_RESULT
                    df.at[index, 'target_size'] = len(pws)
                else:
                    df.at[index, 'known'] = pd.Series(list(get_predictions(pws, row.name))).drop_duplicates().tolist()
                for pw in pws:
                    targets[pw].append(row)
    if baseline:
        read_predictions_baseline(df, targets, pw_files, site_policy=site_policy)
    else:
        read_predictions(df, targets, pw_files, corr=corr, hpb=hpb)

"""
Return all passwords in pred_passwords that fit into FSB bucket
"""
def get_predictions(pred_passwords, bucket):
    return filter(lambda w: bucket_contains(bucket, w), pred_passwords)


"""
Return all passwords in pred_passwords that fit into HPB bucket
"""
def get_predictions_hibp(pred_passwords, bucket):
    return filter(lambda w: bucket_contains_hpb(bucket, w), pred_passwords)


"""
Adds all FSB passwords to buckets for general simulation
"""
def add_all_pws(comp_df, uncomp_df, corr=False):
    for leak_tsv_file in leak_pw_tsv_files:
        tree = PasswordTree(NUM_BUCKETS_C3S, Q_C3S, leak_tsv_file, normalized=True)
        if comp_df != None:
            comp_df['hist_guesses'] += comp_df.index.map(lambda x: tree.get_random_bucket(x,limit=5000))
            comp_df['bucket_size'] += comp_df.index.map(tree.get_bucket_size)
        uncomp_df['hist_guesses'] += uncomp_df.index.map(lambda x: tree.get_random_bucket(x,limit=5000))
        uncomp_df['bucket_size'] += uncomp_df.index.map(tree.get_bucket_size)
    return comp_df,uncomp_df


"""
Adds all FSB passwords to buckets for correlated password simulation
"""
def add_all_pws_corr(df):
    for leak_tsv_file in leak_pw_tsv_files:
        tree = PasswordTree(NUM_BUCKETS_C3S, Q_C3S, leak_tsv_file, normalized=True)
        df['hist1'] += df['b1'].map(lambda x: tree.get_random_bucket(x,limit=5000))
        df['hist2'] += df['b2'].map(lambda x: tree.get_random_bucket(x,limit=5000))
    return df


"""
Check if HPB bucket contains pw
"""
def bucket_contains_hpb(bucket, pw):
    return bucket == get_bucket_hibp(pw)


"""
Check if FSB bucket contains pw
"""
def bucket_contains(bucket, pw):
    start = get_start_bucket(pw)
    size = get_interval_size(get_prob(pw))
    end = (start + size - 1) % NUM_BUCKETS_C3S
    if end < start:
        return bucket <= end or bucket >= start
    else:
        return bucket >= start and bucket <= end


"""
Read password predictions from file for general simulation
"""
def read_predictions(df, targets, pw_files, corr=False, hpb=False):
    for f in pw_files:
        f = open(f,'r')
        for line in f:
            l = line.strip()
            words = line.split('\t')
            target_password = words[0]
            if target_password in targets:
                pred_passwords = [pw for [pw,prob] in eval(words[1])[1:]]
                for row in targets[target_password]:
                    if corr: 
                        b1, b2 = row['b1'], row['b2']
                        if hpb:
                            df.at[row.name, 'target1'] = pd.Series(\
                                df.at[row.name, 'target1'] + list(get_predictions_hibp(pred_passwords, b1))).drop_duplicates().tolist()
                            df.at[row.name, 'target2'] = pd.Series(\
                                df.at[row.name, 'target2'] + list(get_predictions_hibp(pred_passwords, b2))).drop_duplicates().tolist()
                        else:
                            df.at[row.name, 'target1'] = pd.Series(\
                                df.at[row.name, 'target1'] + list(get_predictions(pred_passwords, b1))).drop_duplicates().tolist()
                            df.at[row.name, 'target2'] = pd.Series(\
                                df.at[row.name, 'target2'] + list(get_predictions(pred_passwords, b2))).drop_duplicates().tolist()
                    elif hpb:
                        bucket = row['bucket']
                        _id = row['user']
                        predictions = list(get_predictions_hibp(pred_passwords, bucket))
                        target_guesses = row['target_guesses']
                        df.at[row.name, 'target_guesses'] = target_guesses + predictions
                    else:
                        bucket = row.name
                        df.at[bucket, 'target_guesses'] = pd.Series(\
                            df.at[bucket, 'target_guesses'] + list(get_predictions(pred_passwords, bucket))).drop_duplicates().tolist()


"""
Read password predictions from file for baseline simulation
"""
def read_predictions_baseline(df, targets, predictions_files, site_policy=False):
    if site_policy:
        banlist = open(twitter_banlist_file, 'r').read().splitlines()
    for f in predictions_files:
        f = open(f,'r')
        for line in f:
            l = line.strip()
            words = line.split('\t')
            target_password = words[0]
            if target_password in targets:
                pred_passwords = [pw for [pw,prob] in eval(words[1])[1:]]
                for row in targets[target_password]:
                    if row['pw'] in pred_passwords and row['rank'] == -1:
                        if site_policy:
                            pred_passwords = list(filter(lambda w: site_policy_filter(w, banlist), pred_passwords))
                        df.at[row.name,'rank'] = row['target_size'] + pred_passwords.index(row['pw']) + 1
                        df.at[row.name, 'result'] = TARGET_RESULT
                    df.at[row.name,'target_size'] = row['target_size'] + len(pred_passwords)


"""
Get random FSB bucket for a password
"""
def get_random_bucket(pw):
    start = get_start_bucket(pw)
    size = get_interval_size(get_prob(pw))
    return randrange(start, start + size) % NUM_BUCKETS_C3S


def get_bucket_hibp(pw):
    return get_hash(pw)[:HIBP_PREFIX_LEN]


def get_hash(pw):
    return hashlib.sha256((pw + '1').encode('utf-8')).hexdigest()


"""
Get estimated probability of a password
"""
def get_prob(pw, freq=None, ngprob=None):
    if freq == None:
        freq = passwords.pw2freq(pw)
    if freq >= NTH_FREQ:
        return freq / TOTAL_F
    else:
        try:
            if ngprob == None:
                ngprob = ngmodel.prob(pw)
            return ngprob * NORM_FACTOR
        except:
            return 0


"""
Get start bucket for FSB of password
"""
def get_start_bucket(pw, sha=None):
    if sha == None:
        sha = get_hash(pw)
        return (int(sha[:8],16) & int('fffffffc',16)) >> 2
    else:
        return (int(sha[:8],16) & int('fffffffc',16)) >> 2


"""
Get interval sizes for FSB of password
"""
def get_interval_size(prob):
    return min(NUM_BUCKETS_C3S, max(1, ceil(BUCKET_FACTOR * prob)))


"""
Add additional passwords to guesses
"""
def add_more_pws(comp_df, uncomp_df, hpb=True):
    read_pws = open(add_pw_file, 'r')
    for line in read_pws:
        pw, sha1, ng = line.rstrip('\n').split('\t')
        if hpb:
            bucket = sha1[:HIBP_PREFIX_LEN]
            if bucket in comp_df['bucket'].values:
                comp_df.loc[comp_df['bucket'] == bucket, 'hist_guesses'] += [pw]
            if bucket in uncomp_df['bucket'].values:
                uncomp_df.loc[uncomp_df['bucket'] == bucket, 'hist_guesses'] += [pw]
        else:
            start = get_start_bucket(pw, sha1=sha1)
            size = get_interval_size(get_prob(pw, ngprob=ng))
            for index in range(start, start + size):
                if index in comp_df.index.values:
                    comp_df.at[index, 'hist_guesses'] += [(0,pw)]
                if index in uncomp_df.index.values:
                    uncomp_df.at[index, 'hist_guesses'] += [(0,pw)]
    return comp_df, uncomp_df


def site_policy_filter(pw, banlist):
    if len(pw) < 8 or pw.lower() in banlist: 
        return False
    return True


"""
Read a HPB bucket from file
"""
def read_bucket(bucket):
    bucket_map = {}
    if len(bucket) < 5:
        remaining_paths = [hexchars] * (5- len(bucket))
        for h in itertools.product(*remaining_paths):
            bucket_file = open(buckets_root + '/'.join(bucket) + '/' + '/'.join(h), 'r')
            for line in bucket_file:
                _, count, pw = line.rstrip().split(':',2)
                bucket_map[pw] = int(count)
    else:
        bucket_file = open(buckets_root + '/'.join(bucket[:HIBP_PREFIX_LEN]), 'r')
        for line in bucket_file:
            _, count, pw = line.rstrip().split(':',2)
            bucket_map[pw] = int(count)
    return sorted(bucket_map, key=bucket_map.get, reverse=True)[:5000]


def main(argv):
    global Q_C3S
    global HIBP_PREFIX_LEN
    global write_fname
    global BUCKET_FACTOR
    try:
        opts, args = getopt.getopt(argv,"t:shbp:q:w:")
    except getopt.GetoptError: 
        print('option error')
        sys.exit(2)
    sp_exp, baseline_exp, hpb = False, False, False
    for opt, arg in opts:
        if opt == '-t':
            test_num = arg
        elif opt == '-s':
            sp_exp = True
        elif opt == '-b':
            baseline_exp = True
        elif opt == '-h':
            hpb = True
        elif opt == '-p':
            HIBP_PREFIX_LEN = int(arg)
        elif opt == '-q':
            Q_C3S = int(arg)
        elif opt == '-w':
            write_fname = arg
    BUCKET_FACTOR = NUM_BUCKETS_C3S / q_probs[Q_C3S]
    if sp_exp:
        if baseline_exp:
            site_policy_baseline_experiment()
        else:
            site_policy_experiment(hpb)
    else: # regular
        comp_sample_file = comp_sample_file_format.format(test_num)
        uncomp_sample_file = uncomp_sample_file_format.format(test_num)
        if baseline_exp:
            baseline_experiment(comp_sample_file, uncomp_sample_file)
        else:
            experiment(comp_sample_file, uncomp_sample_file, hpb=hpb)


if __name__ == '__main__':
    main(sys.argv[1:])
    
