import requests
import json
import datetime
import smtplib
import config
import ConfigParser


# First thing when the script runs is to check if the config exists
configfile = ConfigParser.RawConfigParser()
configfile.read('config.cfg')

if configfile.get('FirstRun', 'is_first') == 'True':
    has_run = 'First Time'
else:
    has_run = "NOT First Time"


################
### SETTINGS ###
################

# Show all downloaded shows for the day?
download_report = True

# Show all failed shows for the day?
failed_report = True

# Should I send an email if nothing downloaded at all?
always_email = True

### END OF SETTINGS ###

### Variables
# Getting the time for later use
date = datetime.datetime.now() - datetime.timedelta(days=1)
failed_message = 'The following shows failed to download.\n'
downloaded_message = 'The following shows were downloaded today.\n'
failed_body = ''
downloaded_body = ''
body = ''

### TESTING? ###
# 2 must be true to get something
# testing = False
# testing_failed_only = False
# testing_download_only = False
# testing_both_failed_download = False
# testing_nothing = True

# TEST DATA:
# if testing:
#     today = datetime.datetime.strptime('2014-02-20 01:01', '%Y-%m-%d %H:%M')
#     if testing_failed_only:
#         # all shows should show as BAD
#         show_data = [{u'status': u'Snatched', u'resource': u'The.Following.S02E04', u'tvdbid': 258744, u'season': 2, u'show_name': u'The Following', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 4, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Intelligence.US.S01E06', u'tvdbid': 267260, u'season': 1, u'show_name': u'Intelligence (2014)', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 6, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Almost.Human.S01E10', u'tvdbid': 267702, u'season': 1, u'show_name': u'Almost Human', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 10, u'quality': u'HD TV'}]
#     elif testing_download_only:
#         # all shows should show as GOOD
#         show_data = [{u'status': u'Downloaded', u'resource': u'The.Following.S02E04.mkv', u'tvdbid': 258744, u'season': 2, u'show_name': u'The Following', u'resource_path': u'D:\\The.Following.S02E04', u'provider': u'DIMENSION', u'date': u'2014-02-20 12:30', u'episode': 4, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'The.Following.S02E04', u'tvdbid': 258744, u'season': 2, u'show_name': u'The Following', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 4, u'quality': u'HD TV'}, {u'status': u'Downloaded', u'resource': u'Intelligence.US.S01E06.mkv', u'tvdbid': 267260, u'season': 1, u'show_name': u'Intelligence (2014)', u'resource_path': u'D:\\Intelligence.US.S01E06', u'provider': u'DIMENSION', u'date': u'2014-02-20 12:30', u'episode': 6, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Intelligence.US.S01E06', u'tvdbid': 267260, u'season': 1, u'show_name': u'Intelligence (2014)', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 6, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Almost.Human.S01E10', u'tvdbid': 267702, u'season': 1, u'show_name': u'Almost Human', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 10, u'quality': u'HD TV'}, {u'status': u'Downloaded', u'resource': u'Almost.Human.S01E10.mkv', u'tvdbid': 267702, u'season': 1, u'show_name': u'Almost Human', u'resource_path': u'D:\\Almost.Human.S01E10', u'provider': u'DIMENSION', u'date': u'2014-02-20 12:30', u'episode': 10, u'quality': u'HD TV'}]
#     elif testing_both_failed_download:
#         # The Following should show GOOD, Almost Human and Intelligence should show BAD
#         show_data = [{u'status': u'Downloaded', u'resource': u'The.Following.S02E04.mkv', u'tvdbid': 258744, u'season': 2, u'show_name': u'The Following', u'resource_path': u'D:\\The.Following.S02E04', u'provider': u'DIMENSION', u'date': u'2014-02-20 12:30', u'episode': 4, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'The.Following.S02E04', u'tvdbid': 258744, u'season': 2, u'show_name': u'The Following', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 4, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Intelligence.US.S01E06', u'tvdbid': 267260, u'season': 1, u'show_name': u'Intelligence (2014)', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 6, u'quality': u'HD TV'}, {u'status': u'Snatched', u'resource': u'Almost.Human.S01E10', u'tvdbid': 267702, u'season': 1, u'show_name': u'Almost Human', u'resource_path': u'', u'provider': u'nzb.su', u'date': u'2014-02-20 12:00', u'episode': 10, u'quality': u'HD TV'}]
#     elif testing_nothing:
#         # This is to test that nothing was received from SickBeard
#         show_data = []


def call_sb(sb_address, sb_port, sb_api, status_type):
    show_data = []
    # This function will call SickBeard and return the requested data.
    response = requests.get(
        'http://{}:{}/api/{}/?cmd=history&type={}'.format(
            sb_address, sb_port, sb_api, status_type))
    my_data = json.loads(response.content)
    for status in my_data['data']:
        show_data.append(status)
    return show_data

def trim_shows(shows, date):
    # This function will trim down the list depending on the date set in the config.
    pruned_shows = [
        show for show in shows if
        datetime.datetime.strptime(
            show['date'], '%Y-%m-%d %H:%M') >= date
    ]
    return pruned_shows

# I believe there is a way to get the json list and trim down the data in one call.
full_snatched = call_sb(configfile.get('SBInfo', 'sb_address'),
                        configfile.get('SBInfo', 'sb_port'),
                        configfile.get('SBInfo', 'sb_api'),
                        'snatched')

full_downloaded = call_sb(configfile.get('SBInfo', 'sb_address'),
                        configfile.get('SBInfo', 'sb_port'),
                        configfile.get('SBInfo', 'sb_api'),
                        'downloaded')

snatched_shows = trim_shows(full_snatched, date)

download_shows = trim_shows(full_downloaded, date)


# Create a unique ID with the show_name season number and episode number.
snatched_ids = [show['show_name'] + str(show['season']) + str(show['episode']) for show in snatched_shows]
download_ids = [show['show_name'] + str(show['season']) + str(show['episode']) for show in download_shows]

# Check all unique ID's (created in last function) and see if they exist in the downloaded ID's.
# If not add show to incomplete list.


'''I think I can combine the next 2 list comprehension'''
# Create a list of just incomplete ID's
incomplete_shows_ids = [snatched_id for snatched_id in snatched_ids if snatched_id not in download_ids]

# Create a list of failed shows
incomplete_shows = [show for show in snatched_shows if show['show_name'] + str(show['season']) + str(show['episode'])
                    in incomplete_shows_ids]

# Take the incomplete list and compare the 'date' key to see if it is older then 1 hour.
# If older then 1 hour print the Show Episode Info
if failed_report:
    for incomplete in incomplete_shows:
        hour_old = datetime.datetime.now() - datetime.timedelta(hours=1)
        show_time = datetime.datetime.strptime(incomplete['date'], '%Y-%m-%d %H:%M')
        if show_time < hour_old:
            failed_body += '{episode_name} Season {season_number} Episode {episode_number}\n'.format(
                episode_name=incomplete['show_name'],
                season_number=incomplete['season'],
                episode_number=incomplete['episode'])

# Set up the body to display Downloaded shows for the day.
if download_report:
    for download_show in download_shows:
        downloaded_body += '{episode_name} Season {season_number} Episode {episode_number}\n'.format(
            episode_name=download_show['show_name'],
            season_number=download_show['season'],
            episode_number=download_show['episode'])


# Combine the body's based on settings
if always_email:
    if not failed_body and not downloaded_body:
        # Nothing downloaded
        body = 'Nothing Downloaded Today.'
    elif not failed_body and downloaded_body:
        # Nothing failed but something finished downloading
        body = downloaded_message + downloaded_body
    elif failed_body and not downloaded_body:
        # Something failed and nothing finished downloading
        body = failed_message + failed_body
    elif failed_body and downloaded_body:
        # Something failed and something finished downloading
        body = failed_message + failed_body + '\n' + downloaded_message + downloaded_body
else:
    if failed_body:
        body = failed_body


if body:
    #Config can be found in config.py
    #Send email

    message = \
        "From: {sender}\n" \
        "To: {receivers}\n" \
        "Subject: {subject}\n \n" \
        "{body}".format(sender=configfile.get('EmailInfo', 'sender'),
                        receivers=configfile.get('EmailInfo', 'recipient'),
                        subject=configfile.get('EmailInfo', 'subject'),
                        body=body)

    session = smtplib.SMTP(configfile.get('EmailInfo', 'server'), int(configfile.get('EmailInfo', 'port')))

    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(configfile.get('EmailInfo', 'sender'), configfile.get('EmailInfo', 'password'))
    session.sendmail(configfile.get('EmailInfo', 'sender'), configfile.get('EmailInfo', 'recipient'), message)
    session.quit()
