#! /bin/sh
echo 'In script Connect'
#
# WiMAX interface
#
IFACE='wmx0'

#
# For more ID: wimaxcu plist
#

#NETID = '21' #Yota
NETID='41' #Comstar

ifconfig $IFACE up
wimaxcu status
wimaxcu ron
wimaxcu scan
wimaxcu connect network $NETID
dhclient $IFACE
wimaxcu status link
wimaxcu status connect