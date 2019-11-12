var request = require('request');

var crypto = require('crypto');
var argon2 = require('argon2');
var  ecc = require('elliptic');
var  EC = ecc.ec;
var fs = require('fs');
var  ec = new EC('secp256k1');
var readline = require('readline');

var trim= function(s) {
      return (s || '').replace(/^\s+|\s+$/g, '');
    }
var base64ToHex = function (data) {
  let buff = new Buffer.from(data, 'base64');  
  let text = buff.toString('hex');

    return text;
   }

var get_hash = async function(str) {
      const salt = Buffer.alloc(16, 'salt')
      let hash_a = await argon2.hash(str,{salt:salt});
      let hash_b = await argon2.hash(password,{salt:salt});
      hash_a_sp = trim(hash_a.toString()).split('$');
      return base64ToHex(hash_a_sp[5])
  }

var get_msg = async function(str) {
    let msg = await get_hash(str)
    return msg
}

var start = new Date().getTime();
var  prkey = "8e8f61c213e6ad81888bca3972a3adac6df6f1f40303b910dd3a6b04a2137175";
var  key = ec.keyFromPrivate(prkey, 'hex');
var inv_key = key.getPrivate().invm(ec.n)


var username = process.argv[2]
var password = process.argv[3]

var str = username.concat(password);
var msg;
var writer = fs.createWriteStream('/hdd/c3s/data/aws_data/idbp_netw.txt', {
        flags: 'w'
      });
get_msg(str).then(()=>{

msg = crypto.createHash("sha256").update(str).digest('hex');
var key_user = ec.keyFromPrivate(msg, 'hex');
var  public_key = key_user.getPublic().mul(key.getPrivate()).encode('hex');
pr_hash = hash_prefix = msg.slice(0, 4);
var end1 = new Date().getTime();
var myJSONObject = {"hash_prefix":pr_hash,"enc_userpass":public_key};
request({
    url: "https://bj6x7ryoqa.execute-api.us-east-2.amazonaws.com/prod/-passlistidbp",
    method: "POST",
    json: true,   // <--Very important!!!
    body: myJSONObject
}, function (error, response, body){
    var end2 = new Date().getTime();
    userpass = body.response.userpass;
    pass_list = body.response.leakedlist;
    console.log(pass_list.length)
    
    pub_userpass = ec.keyFromPublic(userpass,'hex'); 

    var res = pub_userpass.getPublic().mul(inv_key).encode('hex')
    var i
    var flag = 0
    
    for (i = 0, len = pass_list.length; i < len; i++) {
    elem = pass_list[i];
    writer.write(elem+"\n")
    if (res === elem) {
      flag = 1
          //console.log("Present in leak");
    }
    }
    if (flag == 0){
        //console.log("Not Present in leak");
    }
    var end = new Date().getTime();
    //console.log(end-start)
    //console.log(end2-end1)
    console.log(end-end2)

});
});


