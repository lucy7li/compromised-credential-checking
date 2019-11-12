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
        
        @lineReader = readline.createInterface({
            input: fs.createReadStream(@filename)
            });
    
  
    save_key: () ->
        fs.writeFileSync('key.txt', @key.getPrivate('hex'))
        
    trim : (s) -> 
        ( s || '' ).replace( /^\s+|\s+$/g, '' ); 


    get_hash_enc: (username,password) =>
        str = username.concat(password)
        msg = crypto.createHash("sha256").update(str).digest('hex'); 
        key_user = ec.keyFromPrivate(msg,'hex'); 
        public_key = key_user.getPublic().mul(@key.getPrivate()).encode('hex')
        hash_prefix = msg[0..3]
        if (! @userpassdict[hash_prefix])
            pass_list = [public_key] 
            @userpassdict[hash_prefix] = pass_list;
        else
            pass_set = new Set(@userpassdict[hash_prefix])
            if ! pass_set.has(public_key)
                @userpassdict[hash_prefix].push(public_key);
            
          
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
          @get_hash_enc(words[0],words[1])
          i = i + 1
          
        @lineReader.on 'close', () => 
          endTime = new Date();
          timeDiff = endTime - startTime; 
 
          timeDiff /= 1000;
          console.log(timeDiff)
          res = JSON.stringify(@userpassdict)
          console.log "json created"
          fs.writeFileSync('username_pass_10m.json', res);          
          console.log "stored"
    
   
    print_ngram: =>
        console.log "here"
        console.log @ngrams[123]
        console.log "done"
 
module.exports = UserpassJson