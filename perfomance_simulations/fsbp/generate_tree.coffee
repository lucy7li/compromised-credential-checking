fs       = require 'fs';
zlib     = require 'zlib';
readline = require 'readline';

NgramProb = require('/home/bijeeta/cloudfare/pwmodels/src/ngram_cs/ngram-prob');
ngram_prob = new NgramProb(filename);
pickle = require './lib/pickle';
Util       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/util'
SortedList = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/sorted-list'

IntervalTree       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/interval-tree'

class RangeTree
    constructor: (@filename) ->
        @itree = new IntervalTree(2**40); 
        @lineReader = readline.createInterface({
            input: fs.createReadStream(@filename)
            });
        @bucket_
        @writer = fs.createWriteStream('/hdd/c3s/data/aws_data/range_tree.txt', { flags: 'a' })
  
        
    trim : (s) -> 
        ( s || '' ).replace( /^\s+|\s+$/g, '' ); 


    get_range : (pw) ->
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
            
          
    store_json: =>
        i = 0
        startTime = new Date();
        @lineReader.on 'line', (line) => 
        
          if(i%10000 == 0)
              endTime = new Date();
              timeDiff = endTime - startTime; 
 
              timeDiff /= 1000;
              console.log(timeDiff)
              console.log(i)
          word = @trim(line.toString())
          data = @get_range(word)
          data_toWrite = word.concat("\t").concat(data[0]).concat("\t").concat(data[1]).concat("\n")
          @writer.write(data_toWrite)  
          #if (data[0]== data[1]):
              continue
          #@itree.add(data[0], data[1],  word);
          i = i + 1
          
        @lineReader.on 'close', () => 
          endTime = new Date();
          timeDiff = endTime - startTime; 
          #pw_tree = JSON.stringify(@itree.nodesByCenter)
          #fs.writeFileSync('/hdd/c3s/data/aws_data/tree_toStore.txt', pw_tree); 
          timeDiff /= 1000;
          console.log(timeDiff)
          console.log("done")
 
module.exports = RangeTree