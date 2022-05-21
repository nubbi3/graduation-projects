#!/bin/bash

LOGTIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$LOGTIME] startup run..." >>/etc/startup_run.log
service ssh start >>/etc/startup_run.log