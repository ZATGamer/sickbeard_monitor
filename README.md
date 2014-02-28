SickBeard Monitor
=================

## Overview
As SickBeard only snatches the nzb files and doesn't check to make sure the snatched file actually downloaded.
I created this script to run and call the SickBeard history AIP and and determine if a file failed to download base on
time currently.
If the file exceeds the timeout value it will send an email to notify that a show "failed" to download.


## Config
You will need a config.py file containing:
> server = '{smtp.server.address}'

> port = {smtp.port.number}

> password = '{password}'

> sender = '{sender.address}'

> recipient = '{recipient.address}'

> subject = '{email subject}'