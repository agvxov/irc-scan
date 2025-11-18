#!/bin/sh

ip=$1
port=$2

printf 'NICK test\r\nUSER test 0 * :test\r\n' | nc -w5 "$ip" "$port" | grep -q '^:' &&
  echo "IRC responded" || echo "no IRC response"
