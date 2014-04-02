import ConfigParser
# This is a very rough initial pass of getting config into the config file.
# This will change a lot and I learn how to do this stuff.


def write_config(config):
    with open('config.cfg', 'wb') as configfile:
        config.write(configfile)


def initial_setup(config):
    config.add_section('SBInfo')
    config.add_section('EmailInfo')
    config.add_section('General')


def startup_config():
    config = ConfigParser.RawConfigParser()

    # Get SickBeard server info.
    config.add_section('SBInfo')
        # Get Server address
    config.set('SBInfo', 'sb_address', raw_input('What is the address to your SickBeard server?: '))
        #Get Server Port
    config.set('SBInfo', 'sb_port', raw_input('What Port is SickBeard running on?: '))
        # Get SickBeard API Key
    config.set('SBInfo', 'sb_api', raw_input('What is your SickBeard servers AIP key?: '))

    # Get Email server info
    config.add_section('EmailInfo')
        # Get SMTP server address
    config.set('EmailInfo', 'server', raw_input('What is the SMTP server address?: '))
        # Get SMTP Port number
    config.set('EmailInfo', 'port', raw_input('What is the SMTP server Port?: '))
        # Get username
    config.set('EmailInfo', 'sender', raw_input('What is your email address? (sender address): '))
        # Get password
    config.set('EmailInfo', 'password', raw_input('What is your password?: '))
    # Get where to send an email to
    config.set('EmailInfo', 'recipient', raw_input('Where would you like to send the report to?: '))
    # Subject of the Report Email
    config.set('EmailInfo', 'subject', raw_input('What do you want the subject of the email to be?: '))

    #General config stuff
    config.add_section('General')
    # Get how often the user wants to check
    config.set('General', 'days', raw_input('How many days do you want the report to contain?'))
    # Get how long the timeout value should be
    config.set('General', 'time', raw_input('How long should the timeout value be (in hours)?'))

    # Get if they always want a report or just when something fails.

    with open('config.cfg', 'wb') as configfile:
        config.write(configfile)
