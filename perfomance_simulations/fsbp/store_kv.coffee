{ KeyValueStore } = require '../lib/kv'
fs       = require 'fs';
pickle = require './lib/pickle';
Util       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/util'
SortedList = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/sorted-list'
kv = new KeyValueStore()

IntervalTree       = require '/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/interval-tree'
itree = new IntervalTree(2**40);

rawdata = fs.readFileSync('/hdd/c3s/data/aws_data/breach_compilation-pw_range.json');  
pw_range = JSON.parse(rawdata);  

for elem,val of pw_range
    if val[0] == val[1]
        continue
    itree.add(val[0], val[1],  elem); 
total = 0
for elem,v of itree.nodesByCenter
    total = total+1
    kv.put(elem,v)
console.log len(itree.nodesByCenter)
pw_tree = JSON.stringify(itree.nodesByCenter)
pickle.dumps(itree.nodesByCenter, function(pickled))
fs.writeFileSync('/hdd/c3s/data/aws_data/breach_compilation-pw_tree_1000000.json', pw_tree); 
###*
    get intervals whose start position is less than or equal to the given value

    @method startPointSearch
    @param {Number} val
    @return {Array(Interval)}
###
startPointSearch= (starts_sorted,val) ->
        
    index = starts_sorted.lastPositionOf(start: val)
    return starts_sorted.slice(0, index + 1)


    ###*
    get intervals whose end position is more than or equal to the given value

    @method endPointSearch
    @param {Number} val
    @return {Array(Interval)}
    ###
endPointSearch= (ends_sorted,val) ->

    index = ends_sorted.firstPositionOf(end: val)

    return ends_sorted.slice(index)

create_list= (elems, val) ->
        nlist = new SortedList(val)
        for elem in elems    
            nlist.insert(elem)
         return nlist   
    
pointSearch= (val, center = @center, results = []) ->
        word = await kv.get("#{center}",'text')
        
        node = JSON.parse(word)
        
        Util.assertNumber(val, '1st argument of IntervalTree#pointSearch()')

        if val < node.center
 
            starts_sorted = create_list(node.starts,'start')
           
            results = results.concat startPointSearch(starts_sorted,val)
            
            if node.left?
                return pointSearch(val, node.left, results)

            else
                return results


        if val > node.center

            ends_sorted = create_list(node.ends,'end')
            results = results.concat endPointSearch(ends_sorted,val)
            
            if node.right?
                return pointSearch(val, node.right, results)

            else
                return results
        
        # if val is node.center
        return results.concat node.getAllIntervals()
onlyUnique = (value, index, self) -> 
    return self.indexOf(value) == index;


get_passwords = (val) ->
    intervals = await pointSearch(val,2**40)
    passwords = []
    passwords.push(interval.id) for interval in intervals
    
    intervals = await pointSearch(val+2**40,2**41)
    passwords.push(interval.id) for interval in intervals
    console.log passwords
    passwords.filter(onlyUnique)    
        
#passwords = get_passwords(943328285131)

