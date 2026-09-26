#!/usr/bin/env bash
# Rehearsal driver: runs README command lines one by one and logs UTC time, cwd, command, exit, output.
# Usage: drive.sh <workdir> <logfile> <commands-file>
W="$1"; LOG="$2"; CMDS="$3"
mkdir -p "$W"; cd "$W"
: > "$LOG"
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  case "$line" in \#*) echo "$line" >> "$LOG"; continue;; esac
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  {
    echo "\$ $line"
    echo "  [utc=$ts cwd=${PWD/#$W/<W>}]"
  } >> "$LOG"
  eval "$line" > "$LOG.out" 2>&1 < /dev/null; rc=$?
  cat "$LOG.out" | sed "s#$W#<W>#g" | tail -n 25 | sed 's/^/  | /' >> "$LOG"
  echo "  exit=$rc" >> "$LOG"
done < "$CMDS"
rm -f "$LOG.out"
