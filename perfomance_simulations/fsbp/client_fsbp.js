var request = require('request');
fs = require('fs');
var password = process.argv[2]
var bucket = process.argv[3]
var crypto = require('crypto');
var s = new Date().getTime();
var msg = crypto.createHash("sha256").update(password).digest('hex');
var e = new Date().getTime();
var writer = fs.createWriteStream('/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/res_passlist.txt', {
        flags: 'w'
      });
var myJSONObject = {"bucketId":parseInt(bucket)};
request({
    url: "https://bj6x7ryoqa.execute-api.us-east-2.amazonaws.com/prod/getdata",
    method: "POST",
    json: true,   // <--Very important!!!
    body: myJSONObject
}, function (error, response, body){
    var e1 = new Date().getTime();
    pass_list = (body.response)
    res_pass = []
    console.log(pass_list.length)
    
    for (i = 0, len = pass_list.length; i < len; i++) {
    elem = pass_list[i];
   
    msg = crypto.createHash("sha256").update(elem).digest('hex');
    writer.write(msg+"\n")
    if (elem == password){
        flag = 1
    }
    
    }
    var e2 = new Date().getTime();
    //console.log(e2-e1)
    //console.log(e1-e)
    //console.log(e-s)
    //console.log(e2-s)
});

