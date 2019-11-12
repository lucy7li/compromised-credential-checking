crypto = require 'crypto';
ecc = require 'elliptic';

EC = ecc.ec;
ec = new EC('secp256k1');

keyA = ec.genKeyPair();
str = "Password456"
msg = crypto.createHash("sha256").update(str).digest('hex');

key = ec.keyFromPrivate(msg,'hex'); 

console.log(keyA.getPublic().mul(key.getPrivate()).encode('hex'))

#console.log(key.derive(keyA.getPublic()))

pk = key.derive(keyA.getPublic()).toString(16)
key1 = ec.keyFromPrivate(pk,'hex');

console.log(key1.getPublic())

key2 = ec.keyFromPublic(key1.getPublic().encode('hex'),'hex');

console.log(key2.getPublic())