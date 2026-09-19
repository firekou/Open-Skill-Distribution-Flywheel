#!/bin/sh
# a runner that spawns its own worker, the way a CLI agent does
sh -c 'while true; do sleep 0.2; done' &
echo "$!" > "$1"
while true; do sleep 0.2; done
