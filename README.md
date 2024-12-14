# Control drone through Internet.

- install linux on raspberry pi
- enable uart
- https://github.com/bluenviron/mediamtx/releases (*download corresponding to your cpu binary file*)
- git clone [git@github.com:vrevyuk/drone_games.git](https://github.com/vrevyuk/drone_games.git)
- cd drone_games
- sudo pip install --break-system-packages -r requirements.txt (*because services will be run under root privileges*)
- sudo cp ./uart2crsf.service /etc/systemd/system/uart2crsf.service
- sudo cp ./streamer.service /etc/systemd/system/streamer.service
- sudo systemctl daemon-reload
- sudo systemctl enable uart2crsf.service
- sudo systemctl enable streamer.service


# setup L2TP vpn connection with cli
## section in progress
// sudo apt install network-manager-l2tp resolvconf<br>
// sudo systemctl disable xl2tpd.service<br>
// include ipsec.d/ipsec.nm-l2tp.secrets

