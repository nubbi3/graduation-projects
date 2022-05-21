#!/bin/bash  

while true;
do
n=`ip route show default | wc -l`
#echo "$n"

if [ $n -gt 1 ]
then 
for ((i=0; i<$n; i++))
do 
echo "del $i"
route delete default
done
route add default gw 183.173.16.1

echo "Set the Wifi gateway as 183.173.16.1"
fi

done
