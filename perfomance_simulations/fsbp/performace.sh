#!/usr/bin/bash
ts=$(date +%s%N)

while IFS=$'\t' read -r -a words
do
node /home/bijeeta/cloudfare/code_c3s/cloudworker/c3s/client_fsbp.js "${words[0]}" "${words[1]}"
done < 'test_range.txt'
wait
tt=$((($(date +%s%N) - $ts)/1000000))
echo "It takes $tt seconds to complete this task..."