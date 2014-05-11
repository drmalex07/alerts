#!/bin/bash

now=$(date +"%s")

let t0=now-1800
let t=t0

# Create a datasourse (DS) at a heartbeat of 60s and a step of 30s

rrdtool create t2.rrd --step 30 --start ${t0} DS:value:COUNTER:60:U:U RRA:AVERAGE:0.5:1:150 RRA:AVERAGE:0.5:10:25

let v=0
for i in $(seq 1 120)
do
    let v+=i
    rrdtool update t2.rrd ${t}:${v}
    # simulate a step of 30s +/- 5s 
    step=$RANDOM
    let step=30+step%10-5
    let t=t+step
    #echo "Update at t=${t} with v=${v} step=${step}"
done

rrdtool graph t2.png --step 60 --start ${t0} --end ${t} DEF:x=t2.rrd:value:AVERAGE LINE1:x#FF0000

cp -vr t2.png /var/www/images/

