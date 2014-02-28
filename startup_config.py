__author__ = 'Anthony Barragree'

import ConfigParser

config = ConfigParser.RawConfigParser()

# This is the bit that will get all the config on the first run for simple user setup.
config.add_section('FirstRun')
config.set('FirstRun', 'is_first', 'False')

#with open('config.cfg', 'wb') as configfile:
#    config.write(configfile)

# Get SickBeard server info.
config.add_section('SBInfo')
    # Get Server address
config.set('SBInfo', 'sb_address', raw_input('What is the address to your SickBeard server?: '))
    #Get Server Port
config.set('SBInfo', 'sb_port', raw_input('What Port is SickBeard running on?: '))
    # Get SickBeard API Key
config.set('SBInfo', 'sb_aip', raw_input('What is your SickBeard servers AIP key?: '))

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

# Get how often the user wants to check

# Get if they always want a report or just when something fails.

with open('config.cfg', 'wb') as configfile:
    config.write(configfile)