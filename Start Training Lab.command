#!/bin/zsh
cd "$(dirname "$0")" || exit 1
print "Raid the Watchtower: Fictional local training lab"
print "This launcher deliberately opens the vulnerable educational version."
print "Keep this window open while you play. Close it to stop the lab."
python3 server.py --training-vulnerable --open-browser
print "The lab has stopped. You can close this window."
read -k 1
