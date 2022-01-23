#!/bin/bash

# Read camera credentials and IP addresses.
# e.g., alexa:secret-passwd@192.168.1.15
. /home/casamia/alexa-ipcam-viewer/vars.sh

# Start the proxy server.
# Streams will be at rtsp://HOST_IP:554/stream-n
# where n is the order of the input streams below.
# Each rtsp stream is at port 554 which is why the proxy is at port 8554.
/home/casamia/live/proxyServer/live555ProxyServer -p 8554 \
  "rtsp://$CAM_1/12" \
  "rtsp://$CAM_2/12" \
  "rtsp://$CAM_3/12"
