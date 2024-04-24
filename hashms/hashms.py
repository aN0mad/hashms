import argparse
import configparser
import time
from os import path, environ
import pymsteams
from subprocess import Popen, PIPE
import requests

PROCESS_NAME = "hashcat"
TEXTBELT_API_KEY = environ.get("TEXTBELT_API_KEY")
SLACK_URL = environ.get("SLACK_URL")
TEAMS_URL = environ.get("TEAMS_URL")


def check_pid(process_name):
    """Return pid of hashcat process."""
    stdout = Popen("pidof " + process_name, shell=True, stdout=PIPE).stdout
    if stdout == None:
        print("Error: stdout for {0} is None".format(process_name))
        return False
    output = stdout.read().rstrip()
    output = output.decode("utf-8")
    if output:
        return output
    return False


def check_file(hashcat_outfile):
    """Check number of lines in designated outfile."""
    if not path.isfile(hashcat_outfile):
        return False
    with open(hashcat_outfile) as file:
        i = 0
        for i, lines in enumerate(file):
            pass
    return i + 1


def send_text(textbelt_api_key, phone_number, message):
    """Send an SMS using the Textbelt API."""
    response = requests.post(
        "https://textbelt.com/text",
        {"phone": str(phone_number), "message": message, "key": textbelt_api_key},
    )
    response_json = response.json()
    if "textId" in response_json:
        output = "[*] SMS sent with ID {}\n[*] Quota remaining: {}".format(
            response_json["textId"], str(response_json["quotaRemaining"])
        )
    elif "error" in response_json:
        output = "[-] Received erorr message from textbelt: {}".format(
            response_json["error"]
        )
    return output


def send_slack(slack_url, message, user=None):
    """Send a notification to Slack."""
    if user != None:
        message = "<@{}> : {}".format(user, message)
        response = requests.post(slack_url, json={"text": message})
        status_code, content = response.status_code, response.content.decode("utf-8")
        output = '[*] Posted message "{}" to Slack.'.format(message)
    else:
        response = requests.post(slack_url, json={"text": message})
        status_code, content = response.status_code, response.content.decode("utf-8")
        output = (
            '[*] Sent message "{}" to Slack.\n[*] Received status code "{}"" and'
            'response "{}"'.format(message, status_code, content)
        )
    return output


def send_teams(teams_url, message, user=None):
    """Send a notification to Teams."""
    myTeamsMessage = pymsteams.connectorcard(teams_url)
    if user != None:
        message = "@{} : {}".format(user, message)
        myTeamsMessage.text(message)
        myTeamsMessage.send()
        output = '[*] Posted message "{}" to Teams.'.format(message)
    else:
        myTeamsMessage.text(message)
        myTeamsMessage.send()
        output = '[*] Sent message "{}" to Teams.'.format(message)
    return output


def parse_config(config):
    """Parse configuration file."""
    configuration = configparser.ConfigParser()
    configuration.read(config)
    try:
        textbelt_api_key = configuration["Textbelt"]["TextbeltAPI"]
        phone_number = configuration["Textbelt"]["PhoneNumber"]
    except KeyError:
        textbelt_api_key = None
        phone_number = None
    try:
        slack_url = configuration["Slack"]["SlackURL"]
        slack_user = configuration["Slack"]["SlackUser"]
    except KeyError:
        slack_url = None
        slack_user = None
    try:
        teams_url = configuration["Teams"]["TeamsURL"]
        teams_user = configuration["Teams"]["TeamsUser"]
    except KeyError:
        teams_url = None
        teams_user = None
    return textbelt_api_key, phone_number, slack_url, slack_user, teams_url, teams_user


def main():
    """Take user input to setup notifications. Print status updates to terminal."""
    parser = argparse.ArgumentParser(
        description="Periodically check hashcat cracking progress and notify of success."
    )
    parser.add_argument(
        "-o",
        "--outfile",
        dest="hashcat_outfile",
        required=False,
        help="hashcat outfile to monitor.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        dest="check_interval",
        required=False,
        type=float,
        default=15,
        help="Interval in minutes between checks. Default 15.",
    )
    parser.add_argument(
        "-n",
        "--notification-count",
        dest="notification_count",
        required=False,
        type=int,
        default=5,
        help="Cease operation after N notifications. Default 5.",
    )
    parser.add_argument(
        "--test",
        dest="test",
        required=False,
        action="store_true",
        help="Send test message via SMS and/or Slack."
        "Does not count against notifications.",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        required=False,
        help="Use a configuration file instead of command-line arguments.",
    )
    parser.add_argument(
        "-p",
        "--phone",
        dest="phone_number",
        required=False,
        help="Phone numer to send SMS to. Format 5551234567.",
    )
    parser.add_argument(
        "-s",
        "--slack",
        dest="slack",
        required=False,
        default=False,
        action="store_true",
        help="Send notification to slack channel.",
    )
    parser.add_argument(
        "-t",
        "--teams",
        dest="teams",
        required=False,
        default=False,
        action="store_true",
        help="Send notification to teams channel.",
    )
    parser.add_argument(
        "--procname",
        dest="procname",
        required=False,
        default="hashcat",
        help='Change the binary name of the process to monitor. Default is "hashcat".',
    )
    args = parser.parse_args()

    hashcat_outfile = args.hashcat_outfile
    check_interval = args.check_interval
    notification_count = args.notification_count
    test = args.test
    phone_number = args.phone_number
    slack = args.slack
    teams = args.teams
    config = args.config
    PROCESS_NAME = args.procname

    parameters = (phone_number, slack, teams)
    if config and any(parameters):
        print(
            "[-] Configuration file (-c/--config) and command-line parameters"
            "(-p/--phone, -s/--slack, -t/--teams) are mutually exclusive."
        )
        exit()

    if config:
        slack = False
        textbelt_api_key, phone_number, slack_url, slack_user, teams_url, teams_user = (
            parse_config(config)
        )
        if slack_url:
            slack = True
        if teams_url:
            teams = True
        print("[*] Parsing configuration file {}".format(config.rstrip()))
    else:
        textbelt_api_key = TEXTBELT_API_KEY
        slack_url = SLACK_URL
        teams_url = TEAMS_URL

    if not phone_number and not slack and not teams and not config:
        parser.print_help()
        exit()

    if test:
        print("[*] Conducting test. This does not count against notifications.")
        message = "hashms test message."
        if phone_number:
            output = send_text(textbelt_api_key, phone_number, message)
            print(output)
        if slack and not slack_user:
            output = send_slack(slack_url, message)
            print(output)
        if slack and slack_user:
            output = send_slack(slack_url, message, slack_user)
            print(output)
        if teams and not teams_user:
            output = send_teams(teams_url, message)
            print(output)
        if teams and teams_user:
            output = send_teams(teams_url, message, teams_user)
            print(output)
        print("[*] Test complete.")
        exit()

    if phone_number and not textbelt_api_key:
        print(
            "[-] No textbelt API key - check environmental variable or configuration file."
        )
        exit()
    if slack and not slack_url:
        print("[-] No slack URL - check environmental variable or configuration file.")
        exit()
    if teams and not teams_url:
        print("[-] No teams URL - check environmental variable or configuration file.")
        exit()

    starting_pid = check_pid(PROCESS_NAME)
    if not starting_pid:
        message = "hashcat is no longer running"
        print("[-] {0}. Exiting.".format(message))
        if phone_number:
            output = send_text(textbelt_api_key, phone_number, message)
            print(output)
        if slack:
            output = send_slack(slack_url, message, slack_user)
            print(output)
        if teams:
            output = send_teams(teams_url, message, teams_user)
            print(output)
        exit()
    print("[*] hashcat PID: {}".format(starting_pid))

    starting_outfile = check_file(hashcat_outfile)
    if starting_outfile:
        print("[*] Outfile exists and is {} lines long.".format(starting_outfile))

    i = 1
    try:
        while i < notification_count + 1:
            current_pid = check_pid(PROCESS_NAME)
            current_outfile = check_file(hashcat_outfile)
            current_time = time.strftime("%A %d %B %Y at %H:%M")
            if starting_pid != current_pid:
                print("[-] Original hashcat process stopped. Exiting.")
                exit()
            elif not current_outfile:
                print(
                    "[-] File does not exist. Monitoring for file creation."
                    "Checked on {}".format(current_time)
                )
            elif starting_outfile == current_outfile:
                print(
                    "[-] No more hashes cracked yet. Checked on {}".format(current_time)
                )
            elif starting_outfile != current_outfile:
                print(
                    "[+] Additional hashes cracked! Checked on {}".format(current_time)
                )
                message = (
                    "{} hashes have been cracked."
                    "Notification {} of {}.".format(
                        current_outfile, i, notification_count
                    )
                )
                if phone_number:
                    output = send_text(textbelt_api_key, phone_number, message)
                    print(output)
                if slack:
                    output = send_slack(slack_url, message, slack_user)
                    print(output)
                if teams:
                    output = send_teams(teams_url, message, teams_user)
                    print(output)
                i += 1
                if i == notification_count + 1:
                    print("[*] Notification limit reached. Happy hunting.")
                    # exit()
                starting_outfile = current_outfile
                print(
                    "[*] Sent {} out of {} notifications.".format(
                        i - 1, notification_count
                    )
                )
            print("[*] Sleeping for {} minutes...".format(check_interval))
            time.sleep(float(check_interval) * 60)
    except KeyboardInterrupt:
        print("[-] Ctrl+C detected. Exiting.")
        exit()


if __name__ == "__main__":
    main()
