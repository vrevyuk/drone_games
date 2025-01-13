#/bin/bash

VPN_SERVER_IP="35.181.152.51"

case $1 in

	start)
	IPSEC_STATUS=$(/usr/sbin/ipsec status | grep "1 up")
	if [ ${#IPSEC_STATUS} -eq 0 ]; then
		echo "START IPSEC"
		/usr/sbin/ipsec restart
		echo "UP MYVPN"
		/usr/sbin/ipsec up myvpn
		sleep 2
		/usr/sbin/ipsec status
	fi

	PPP_IP=$(ip -4 addr show ppp0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
	while [ ${#PPP_IP} -eq 0 ]; do
		echo "UP PPP0"
		echo "c myvpn" > /var/run/xl2tpd/l2tp-control
		sleep 1
		ETH0_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
		PPP_IP=$(ip -4 addr show ppp0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
		PPP_GW=$(ip -4 addr show ppp0 | grep -oP '(?<=peer\s)\d+(\.\d+){3}')
		echo "WAIT FOR PPP => eth0: $ETH0_IP, ppp0: $PPP_IP->$PPP_GW"
	done

	IPSEC_ROUTE=$(ip route | grep $VPN_SERVER_IP)
	if [ ${#IPSEC_ROUTE} -eq 0 ]; then
		echo "SET ROUTE FOR IPSEC SERVER"
		route add $VPN_SERVER_IP gw $ETH0_IP dev eth0
	fi

	PPP_DEFAULT_ROUTE=$(ip route | grep "default dev ppp0")
	if [ ${#PPP_DEFAULT_ROUTE} -eq 0 ]; then
		echo "SET DEFAULT ROUTE"
		route add default dev ppp0
	fi

	sleep 10
	echo "CHECK TUNNEL"
	/opt/drone_games/ipsec_run.sh start
	exit 0
	;;

	stop)
	echo "STOPPING...."
	IPSEC_STATUS=$(/usr/sbin/ipsec status | grep "1 up")
	if [ ${#IPSEC_STATUS} -eq 0 ]; then 
		echo "ALREADY STOPPED"
		exit 0 
	fi
        ETH0_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
	route del default dev ppp0
	route del $VPN_SERVER_IP gw $ETH0_IP dev eth0
	echo "d myvpn" > /var/run/xl2tpd/l2tp-control
	sleep 1
	/usr/sbin/ipsec down myvpn
	sleep 1
	/usr/sbin/ipsec status
	echo "SUCCESSFULLY STOPPED"
	;;

	*)
	echo "ha-ha"
	exit 0
esac
