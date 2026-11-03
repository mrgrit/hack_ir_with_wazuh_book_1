#!/bin/sh
printf "book09-payload user=%s host=%s\n" "$(id -un)" "$(hostname)"
