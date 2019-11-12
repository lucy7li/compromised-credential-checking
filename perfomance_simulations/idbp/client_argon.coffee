crypto = require 'crypto';
ecc = require 'elliptic';
fs       = require 'fs';
argon2 = require 'argon2';
EC = ecc.ec;
ec = new EC('secp256k1');

get_hash = (str) =>
    hash = await argon2.hash(str);
    return hash

start = new Date().getTime();
prkey = "8e8f61c213e6ad81888bca3972a3adac6df6f1f40303b910dd3a6b04a2137175"
key = ec.keyFromPrivate(prkey,'hex');;

username = "V11@email.cz"    
password = "slovensko1"
str = username.concat(password)
start = new Date().getTime();
msg = crypto.createHash("sha256").update(str).digest('hex'); 
msg = crypto.createHash("sha256").update(str).digest('hex'); 
msg = crypto.createHash("sha256").update(str).digest('hex'); 
elapsed = new Date().getTime() - start;
console.log elapsed
key_user = ec.keyFromPrivate(msg,'hex'); 
public_key = key_user.getPublic().mul(key.getPrivate()).encode('hex')
console.log public_key
console.log msg





prkey = "8e8f61c213e6ad81888bca3972a3adac6df6f1f40303b910dd3a6b04a2137175"
key = ec.keyFromPrivate(prkey,'hex');;

username = "V11@email.cz"    
password = "slovensko1"
str = username.concat(password)
start = new Date().getTime();
hash = get_hash(str)
hash = get_hash(str)
hash = get_hash(str)
elapsed = new Date().getTime() - start;
#msg = crypto.createHash("sha256").update(str).digest('hex'); 
key_user = ec.keyFromPrivate(msg,'hex'); 
public_key = key_user.getPublic().mul(key.getPrivate()).encode('hex')
console.log public_key
console.log hash

console.log elapsed