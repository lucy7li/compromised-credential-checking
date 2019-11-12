fs       = require 'fs';
zlib     = require 'zlib';
readline = require 'readline';
crypto = require 'crypto';
ecc = require 'elliptic';
EC = ecc.ec;
ec = new EC('secp256k1');

class UserpassJson
    constructor: (@filename) ->
        @userpassdict = {}  
        @key = ec.genKeyPair();
        @prkey = "5358f9d3079978e39e169c92208482926a469d934d97e0a84486ca01e86f142e"
        @key = ec.keyFromPrivate(@prkey,'hex');
        @lineReader = readline.createInterface({
            input: fs.createReadStream(@filename)
            });
        @writer = fs.createWriteStream('/hdd/c3s/data/userpass_1.txt', { flags: 'a' })
  
    save_key: () ->
        fs.writeFileSync('key_pr.txt', @key.getPrivate('hex'))
        
    trim : (s) -> 
        ( s || '' ).replace( /^\s+|\s+$/g, '' ); 


    get_hash_enc: (username,password) =>
        str = username.concat(password)
        msg = crypto.createHash("sha256").update(str).digest('hex'); 
        key_user = ec.keyFromPrivate(msg,'hex'); 
        public_key = key_user.getPublic().mul(@key.getPrivate()).encode('hex')
        hash_prefix = msg[0..3]
        return [hash_prefix,public_key]
            
          
    store_json: =>
        i = 0
        startTime = new Date();
        @lineReader.on 'line', (line) => 
        
          if(i%1000000 == 0)
              endTime = new Date();
              timeDiff = endTime - startTime; 
 
              timeDiff /= 1000;
              console.log(timeDiff)
              console.log(i)
          words = @trim(line.toString()).split('\t')
          data = @get_hash_enc(words[0],words[1])
          data_toWrite = data[0].concat("\t").concat(data[1]).concat("\n")
          @writer.write(data_toWrite)  
          i = i + 1
          
        @lineReader.on 'close', () => 
          endTime = new Date();
          timeDiff = endTime - startTime; 
 
          timeDiff /= 1000;
          console.log(timeDiff)
          console.log("done")
    
   
    print_ngram: =>
        console.log "here"
        console.log @ngrams[123]
        console.log "done"
 
module.exports = UserpassJson