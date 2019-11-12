fs       = require 'fs';
zlib     = require 'zlib';
readline = require 'readline';
fs       = require 'fs';

Util       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/util'
SortedList = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/sorted-list'

IntervalTree       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/interval-tree'


class RangeTree
    constructor: (@index) ->
        
        @itree = new IntervalTree(2**30);
        @lineReader = readline.createInterface({
            input: fs.createReadStream('/hdd/c3s/data/aws_data/interval_64_0.txt')
            });
        @writer = fs.createWriteStream('/hdd/c3s/data/aws_data/splits/intr_tree_lucy_0.txt', { flags: 'w' })  
        
    trim : (s) -> 
        ( s || '' ).replace( /^\s+|\s+$/g, '' );      
          
    store_json: =>
        i = 0
        startTime = new Date();
        @lineReader.on 'line', (line) => 
        
          if(i%100000 == 0)
              endTime = new Date();
              timeDiff = endTime - startTime; 
 
              timeDiff /= 1000;
              console.log(timeDiff)
              console.log(i)
          word = @trim(line.toString()).split('\t')
          
          if (word[1]!= word[2])   
              @itree.add(parseInt(word[1]), parseInt(word[2]),  word[0]);   
          i = i + 1
          
        @lineReader.on 'close', () => 
            endTime = new Date();
            timeDiff = endTime - startTime; 
            for elem,v of @itree.nodesByCenter
                data_toWrite = elem.concat("\t").concat(v).concat("\n");
                @writer.write(data_toWrite)

 
module.exports = RangeTree