#!/bin/bash


echo "OTBR_AGENT_OPTS=\"-I wpan0 -B eth0 -d7 spinel+hdlc+uart:///dev/ttyUSB0\"" >/etc/default/otbr-agent
/app/script/server
tail -f /var/log/syslog
