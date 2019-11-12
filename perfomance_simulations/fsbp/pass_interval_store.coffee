fs       = require 'fs';
NgramProb = require '/home/bijeeta/cloudfare/pwmodels/src/ngram_cs/ngram-prob';
crypto = require 'crypto'

converter = require 'hex2dec'

bucket_size = 2**40
filename = 'res.json'
ngram_prob = new NgramProb(filename);
pass_prob = {}

get_range = (pw) ->
        prob_pw = ngram_prob.cal_prob(pw)
        pass_prob[password] = Math.log(prob_pw)
        prob_pq = ngram_prob.cal_prob_topq(1)
        prob_bucktes  = Math.ceil((bucket_size*prob_pw)/prob_pq)
        
        min_gamma = Math.min(bucket_size,prob_bucktes)
        
        hash = crypto.createHash('sha1')
        hash.update(pw)
        hex = hash.digest('hex')
        dec = converter.hexToDec(hex.substring(0,10)); 
       
        res = []
        res.push(dec %% bucket_size)
        res.push((dec %% bucket_size)+ min_gamma)
        
        return res
        
rawdata = fs.readFileSync('/hdd/c3s/data/aws_data/breach_compilation-withoutcount.json');  
passwords = JSON.parse(rawdata);  

pass_ran = {}

sum = 0
i = 0
for password in passwords
    if i%100000 == 0
        console.log i
        #clcconsole.log sum/i
    range = get_range(password)
    #sum = sum+(range[1]-range[0])
    pass_ran[password] = range
    
    i = i + 1

pw_json = JSON.stringify(pass_ran)
prob_json = JSON.stringify(pass_prob)
fs.writeFileSync('/hdd/c3s/data/aws_data/breach_compilation-pw_range_full.json', pw_json); 
#fs.writeFileSync('/hdd/c3s/data/aws_data/breach_compilation-pw_prob.json', prob_json); 