readline = require('readline');

lineReader = readline.createInterface({
        input: fs.createReadStream(this.filename)
      });
