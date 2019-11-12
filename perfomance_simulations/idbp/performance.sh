#!/usr/bin/bash
ts=$(date +%s%N)

while IFS=$'\t' read -r -a words
do
node /home/bijeeta/cloudfare/idbp/post_client.js "${words[0]}" "${words[1]}"
done < 'input.txt'
wait
tt=$((($(date +%s%N) - $ts)/1000000))
echo "It takes $tt seconds to complete this task..."
