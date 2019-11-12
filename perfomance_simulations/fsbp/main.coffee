range_tree = require './generate_tree'
#user_pass_dict = new createjson('input_10m.txt');
#user_pass_dict.save_key()

#user_pass_dict.store_json();

range_tree = new range_tree("/hdd/c3s/data/aws_data/breach_compilation-withoutcount.txt");
range_tree.store_json()