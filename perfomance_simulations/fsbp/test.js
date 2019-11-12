const Cloudworker = require('@dollarshaveclub/cloudworker')



const simpleScript = `addEventListener('fetch', async event => { 
   await get_passwords(1)
   event.respondWith(new Response('hello', {status: 200}))
})
 var IntervalTree, KeyValueStore, SortedList, Util, create_list, elem, endPointSearch, get_passwords, itree, kv, passwords, pointSearch, ref, startPointSearch, v;

  ({KeyValueStore} = require('../lib/kv'));
  const Cloudworker = require('../lib/cloudworker')

  Util = require('/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/util');

  SortedList = require('/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/sorted-list');

  kv = new KeyValueStore();

  IntervalTree = require('/home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/interval_tree/lib_js/interval-tree');

  itree = new IntervalTree(300);

  itree.add(22, 56, 'foo');

  itree.add(44, 199, 'bar');

  itree.add(1, 38, 'bar2');

  ref = itree.nodesByCenter;
  for (elem in ref) {
    v = ref[elem];
    kv.put(elem, v);
  }
  console.log(itree)
  startPointSearch = function(starts_sorted, val) {
    var index;
    index = starts_sorted.lastPositionOf({
      start: val
    });
    return starts_sorted.slice(0, index + 1);
  };

  endPointSearch = function(ends_sorted, val) {
    var index;
    index = ends_sorted.firstPositionOf({
      end: val
    });
    return ends_sorted.slice(index);
  };

  create_list = function(elems, val) {
    var i, len, nlist;
    nlist = new SortedList(val);
    for (i = 0, len = elems.length; i < len; i++) {
      elem = elems[i];
      nlist.insert(elem);
    }
    return nlist;
  };

  pointSearch = async function(val, center = this.center, results = []) {
    var ends_sorted, node, starts_sorted, word;
    word = (await kv.get(center.toString(), 'text'));
    node = JSON.parse(word);
    Util.assertNumber(val, '1st argument of IntervalTree#pointSearch()');
    if (val < node.center) {
      starts_sorted = create_list(node.starts, 'start');
      results = results.concat(startPointSearch(starts_sorted, val));
      if (node.left != null) {
        return pointSearch(val, node.left, results);
      } else {
        return results;
      }
    }
    if (val > node.center) {
      ends_sorted = create_list(node.ends, 'end');
      results = results.concat(endPointSearch(ends_sorted, val));
      if (node.right != null) {
        return pointSearch(val, node.right, results);
      } else {
        return results;
      }
    }
    
    // if val is node.center
    return results.concat(node.getAllIntervals());
  };

  get_passwords = async function(val) {
    console.log("here3")
    var i, interval, intervals, len, passwords;
    intervals = (await pointSearch(2, 300));
    
    passwords = [];
    for (i = 0, len = intervals.length; i < len; i++) {
      interval = intervals[i];
      passwords.push(interval.id);
    }
    return passwords;
  };
`

const req = new Cloudworker.Request('https://myfancywebsite.com/someurl')
const cw = new Cloudworker(simpleScript)
cw.dispatch(req).then((res) => {
  console.log("Response Status: ", res.status)
  res.text().then((body) =>{
    console.log("Response Body: ", body)
  })
})
