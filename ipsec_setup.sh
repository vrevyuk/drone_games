#/bin/bash

VPN_SERVER_IP="35.181.152.51"
VPN_SERVER_NAME="3.83.101.13"
VPN_IPSEC_PSK="V6XAfm3XSFoGoBjpMctD"
VPN_USER="vpnuser"
VPN_PASSWORD="nLJNBu7EhxagrGKW"

echo "---------------------------------------------------------------------"
echo "Setup ipsec vpn tunnel configuration to $VPN_SERVER_IP for $VPN_USER"

cat > /etc/ipsec.conf <<EOF
# ipsec.conf - strongSwan IPsec configuration file

conn myvpn
  auto=add
  keyexchange=ikev1
  authby=secret
  type=transport
  left=$VPN_SERVER_NAME
  leftprotoport=17/1701
  rightprotoport=17/1701
  right=$VPN_SERVER_IP
  rightid=3.83.101.13
  ike=aes128-sha1-modp2048
  esp=aes128-sha1
EOF
echo "/etc/ipsec.conf....done"

cat > /etc/ipsec.secrets <<EOF
: PSK "$VPN_IPSEC_PSK"
EOF
chmod 600 /etc/ipsec.secrets
echo "/etc/ipsec.secrets....done"


cat > /etc/xl2tpd/xl2tpd.conf <<EOF
[lac myvpn]
lns = $VPN_SERVER_IP
ppp debug = yes
pppoptfile = /etc/ppp/options.l2tpd.client
length bit = yes
EOF
echo "/etc/xl2tpd/xl2tpd.conf....done"

cat > /etc/ppp/options.l2tpd.client <<EOF
ipcp-accept-local
ipcp-accept-remote
refuse-eap
require-chap
noccp
noauth
mtu 1280
mru 1280
noipdefault
defaultroute
usepeerdns
connect-delay 5000
name "$VPN_USER"
password "$VPN_PASSWORD"
EOF
chmod 600 /etc/ppp/options.l2tpd.client
echo "/etc/ppp/options.l2tpd.client....done"

mkdir -p /var/run/xl2tpd
touch /var/run/xl2tpd/l2tp-control
echo "/var/run/xl2tpd/l2tp-control....done"

cp ./ipsec_run.service /etc/systemd/system/ipsec_run.service
systemctl enable ipsec_run.service
systemctl start ipsec_run.service

echo "---------------------------------------------------------------------"
echo "Setup has been successfully done"
echo "---------------------------------------------------------------------"
