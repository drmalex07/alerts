#!/bin/bash

now=$(date +"%s")

let t0=now-3600
let t=t0+5

# Define a datasourse (DS) of type 'GAUGE' at a heartbeat of 60s and a step of 30s
# Define the following archives (RRAs):
#  - an AVERAGE of the last 1 steps (that is the last value!), keep 75 such consolidated data points (CDPs)
#  - an AVERAGE of the last 10 steps (=5min), keep 25 such consolidated data points (CDPs)
#  - an AVERAGE of the last 30 steps (=15min), keep 20 such consolidated data points (CDPs)
rrdtool create t1.rrd --step 30 --start ${t0} DS:value:GAUGE:60:U:U \
   RRA:AVERAGE:0.5:1:75 \
   RRA:AVERAGE:0.5:10:25 \
   RRA:AVERAGE:0.5:30:20

for i in $(seq 1 120)
do
    v=$(echo "0.1 * ${i} * ${i} - 0.5 * ${i}"| bc -l)
    rrdtool update t1.rrd ${t}:${v}
    # simulate a step of 30s +/- 5s 
    r=$RANDOM
    let step=30+r%10-5
    let t=t+step
    #echo "Update at t=${t} with v=${v} step=${step}"
done

rrdtool graph t1.png --step 30 --start ${t0} --end ${t} --vertical-label "Test 1" --width 500 --height 200  \
  DEF:x=t1.rrd:value:AVERAGE \
  AREA:x#e7c1c1 \
  LINE1:x#ff0000 

#cp -vr t1.png /var/www/images/

