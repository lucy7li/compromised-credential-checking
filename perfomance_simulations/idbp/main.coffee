createjson = require './create_json'
save_amazon = require './save_amazon'
#user_pass_dict = new createjson('input_10m.txt');
#user_pass_dict.save_key()

#user_pass_dict.store_json();

save_data = new save_amazon("/hdd/c3s/data/c3s_leakedData_1.txt");
#save_data = new save_amazon("input_10.txt");
save_data.save_key()
save_data.store_json()
