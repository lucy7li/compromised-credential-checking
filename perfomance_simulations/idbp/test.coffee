crypto = require 'crypto';
ecc = require 'elliptic';
fs       = require 'fs';
EC = ecc.ec;
BN = require 'bn.js';
ec = new EC('secp256k1');
console.log(ec.n)
console.log("here")
user_pass = "042611d8bbdefaf509fa4775dad17af0cb10e51f935092d246818479f70037d7e64cbb8fdfe2c17e3d8ea38001057b81340f80420718e2ca22793f5647b48cf0d2"

pub = ec.keyFromPublic(user_pass,'hex'); 

prkey = "8e8f61c213e6ad81888bca3972a3adac6df6f1f40303b910dd3a6b04a2137175"
key = ec.keyFromPrivate(prkey,'hex')
console.log(key.getPublic().getX().toString('hex'))
str = "Password456"
msg = crypto.createHash("sha256").update(str).digest('hex');
console.log(msg)
