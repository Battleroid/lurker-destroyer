# lurker-destroyer

Make your own discord bot for this. Pretty simple. Goes through channels, gets last message, either applies a role or kicks them depending on the supplied args. Use at your own discretion.

## usage

```
usage: lurker.py [-h] [--limit-role LIMIT_ROLE] [--day-cutoff DAY_CUTOFF]
                 [--for-real]
                 TOKEN SERVER_ID ROLE_ID

positional arguments:
  TOKEN
  SERVER_ID
  ROLE_ID               Role to apply

optional arguments:
  -h, --help            show this help message and exit
  --limit-role LIMIT_ROLE
                        Role to target
  --day-cutoff DAY_CUTOFF
                        Day delta cutoff
  --for-real            Really kick or add roles
```
