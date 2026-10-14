# IRC-scan

> me scanning for IRC servers for fun

## Repository

| Path               | Description                                                          |
| :----------------- | :------------------------------------------------------------------- |
| primitive-probe.sh | IGNORE; ncat based probe; technically works, but effectively useless |
| probe.py           | proper probe; see --help                                             |
| Makefile           | Remove intermediate files                                            |

## Operation

1. Fetch an IP range you fancy. (Preferable one owned by a VPS.)

2. Masscan it for open IRC ports:
```
s masscan 194.238.28.34/32 -p6697,7000,6660-6669 --rate=1000 -oL masscan.out
```

3. Convert it into a list file of IPs.

4. Run `probe.py` on the list.
