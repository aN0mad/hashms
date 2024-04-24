# hashms

hashms runs during a hashcat cracking session and checks the given outfile (-o/--outfile parameter in hashcat) at specified intervals. If the outfile has additional lines (i.e. additional hashes have been cracked) hashms sends a notification via SMS and/or Slack and/or Teams. The intent is to reduce the delay between cracking a hash and follow-on operations, as well as the manual effort involved in checking and re-checking ongoing cracking sessions.

hashms uses [Textbelt](https://textbelt.com/) for SMS. An API key is required for SMS, and a [Slack webhook URL](https://api.slack.com/incoming-webhooks) is required for Slack messages, a 
[Teams webhook URL](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=newteams%2Cdotnet).

## Installation

Clone the repositoriy and install with `pipx`:
```
pipx install .
```

## Config file
```conf
[Textbelt]
# This is an example and is NOT a valid API key.
TextbeltAPI = ddYPuc5sKyfbw7kGGD86eZu2ps336dJ33oPjbzEnjfFUHVR000CKJEI0XmpHGN22fg
PhoneNumber = 1234567890

[Slack]
# This is an example and is NOT a valid Slack webhook.
SlackURL = https://hooks.slack.com/services/ABCDEFGHI/JKLMNOPQR/STUVWXYZ1234567890ABCDEF
SlackUser = Steve                     

[Teams]
# This is an example and is NOT a valid Teams webhook.
TeamsURL = https://outlook.office.com/webhook/ABCDEFGHI/JKLMNOPQR/STUVWXYZ1234567890ABCDEF
TeamsUser = Steve
```

## Usage

Run hashms in a screen, tmux, or other terminal session while hashcat is running and provide it the name of your hashcat outfile to monitor. If you are running on a shared machine, or the user running hashms is different than the user running hashcat, make sure hashms has permissions to read the outfile. 

```bash
(hashms-py3.11) root@0339621bd5bc:/workspaces/hashms# hashms 
usage: hashms [-h] [-o HASHCAT_OUTFILE] [-i CHECK_INTERVAL] [-n NOTIFICATION_COUNT] [--test] [-c CONFIG] [-p PHONE_NUMBER] [-s] [-t] [--procname PROCNAME]

Periodically check hashcat cracking progress and notify of success.

options:
  -h, --help            show this help message and exit
  -o HASHCAT_OUTFILE, --outfile HASHCAT_OUTFILE
                        hashcat outfile to monitor.
  -i CHECK_INTERVAL, --interval CHECK_INTERVAL
                        Interval in minutes between checks. Default 15.
  -n NOTIFICATION_COUNT, --notification-count NOTIFICATION_COUNT
                        Cease operation after N notifications. Default 5.
  --test                Send test message via SMS and/or Slack.Does not count against notifications.
  -c CONFIG, --config CONFIG
                        Use a configuration file instead of command-line arguments.
  -p PHONE_NUMBER, --phone PHONE_NUMBER
                        Phone numer to send SMS to. Format 5551234567.
  -s, --slack           Send notification to slack channel.
  -t, --teams           Send notification to teams channel.
  --procname PROCNAME   Change the binary name of the process to monitor. Default is "hashcat".
```

## Examples
### Config file with 15 minute monitoring
```bash
hashms -c ./hashms.conf -o /home/pentester/ntlm2-cracked -i 15
```

# Kudos
Code taken from [WJDigby - hashms project](https://github.com/WJDigby/hashms)