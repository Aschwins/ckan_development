#!/usr/bin/env bash
data=""
for s in $(cat mirrors.csv); do
  t=$(time "%E" curl -q $s)
  echo "$s was $t"
  data="$data$t $s\n"
done

echo "===RESULTS==="

echo -e $data | sort
