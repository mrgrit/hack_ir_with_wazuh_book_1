#!/bin/sh
printf "book09-cron user=%s host=%s\n" "$(id -un)" "$(hostname)" >> /tmp/book09-cron-result
