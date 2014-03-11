import requests
import json
import datetime
import smtplib
import ConfigParser
import startup_config


def check_config():
    try:
        with open('config.cfg'):
            return True
    except IOError:
        return False


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


def build_report(episodes):
    # The Idea of this functions is to just build the base email message body.
    show_body = ''
    for episode in episodes:
        show_body += '{episode_name} Season {season_number} Episode {episode_number}\n'.format(
            episode_name=episode['show_name'],
            season_number=episode['season'],
            episode_number=episode['episode'])
    return show_body


if __name__ == '__main__':
    # First thing when the script runs is to check if the config exists
    if not check_config():
        startup_config.startup_config()

    # Open and read the config file.
    configfile = ConfigParser.RawConfigParser()
    configfile.read('config.cfg')

    # Show all downloaded shows for the day?
    download_report = True

    # Show all failed shows for the day?
    failed_report = True

    # Should I send an email if nothing downloaded at all?
    always_email = True

    ### Variables
    # Getting the time for later use
    date = datetime.datetime.now() - datetime.timedelta(days=int(configfile.get('General', 'days')))
    time = int(configfile.get('General', 'time'))
    failed_message = 'The following shows failed to download.\n'
    downloaded_message = 'The following shows were downloaded today.\n'
    failed_body = ''
    downloaded_body = ''
    body = ''

    # Call SickBeard and get snatched shows.
    full_snatched = call_sb(configfile.get('SBInfo', 'sb_address'),
                            configfile.get('SBInfo', 'sb_port'),
                            configfile.get('SBInfo', 'sb_api'),
                            'snatched')

    # Call SickBeard and get downloaded shows.
    full_downloaded = call_sb(configfile.get('SBInfo', 'sb_address'),
                              configfile.get('SBInfo', 'sb_port'),
                              configfile.get('SBInfo', 'sb_api'),
                              'downloaded')

    # Trim Snatched shows to set time frame.
    snatched_shows = trim_shows(full_snatched, date)

    # Trim Downloaded shows to set time frame.
    download_shows = trim_shows(full_downloaded, date)

    #Dertermin if the trimmed lists are blank.
    if not snatched_shows and not download_shows:
        if always_email:
            body = 'Nothing Downloaded Yesterday.'
    else:
        # Create a unique ID with the show_name season number and episode number.
        snatched_ids = [show['show_name'] + str(show['season']) + str(show['episode']) for show in snatched_shows]
        download_ids = [show['show_name'] + str(show['season']) + str(show['episode']) for show in download_shows]

        # Compare snatched_ids and download_ids
        # if something exists in snatched but not download, add it to incomplete_shows
        incomplete_shows_ids = [snatched_id for snatched_id in snatched_ids if snatched_id not in download_ids]

        # Build full incomplete_show list based of incomplete_show_ids
        incomplete_shows = [show for show in snatched_shows
                            if show['show_name'] + str(show['season']) + str(show['episode'])
                            in incomplete_shows_ids]

        # Take the incomplete list and compare the 'date' key to see if it is older then specified time (1 hour).
        # If older then time (1 hour) print the Show Episode Info

        if failed_report:
            failed_shows = [incomplete_show for incomplete_show
                            in incomplete_shows
                            if datetime.datetime.strptime(incomplete_show['date'], '%Y-%m-%d %H:%M')
                            < datetime.datetime.now() - datetime.timedelta(hours=time)]

        if failed_report:
            for incomplete in incomplete_shows:
                hour_old = datetime.datetime.now() - datetime.timedelta(hours=time)
                show_time = datetime.datetime.strptime(incomplete['date'], '%Y-%m-%d %H:%M')
                if show_time < hour_old:
                    failed_body += build_report(incomplete)

        # Call build_report to build the body for downloads
        if download_report:
            downloaded_body = build_report(download_shows)

        # Combine the body's based on settings
        if always_email:
            if not failed_body and downloaded_body:
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
