#!/bin/sh

chmod +x start.sh
systemctl stop MES_bridge.service
systemctl disable MES_bridge.service
rm /etc/systemd/system/MES_bridge.service
cp daemon/MES_lora.service /etc/systemd/system/
systemctl enable MES_lora.service
systemctl daemon-reload
systemctl start MES_lora.service
systemctl status MES_lora.service