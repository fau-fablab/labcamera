#!/bin/sh

iw event | while read line; do
    echo $line
    #logger -t nikon $line
    if [ -z "${line##*connected to 00:90:b5:29:d7:3b*}" ]; then
        echo connected
        logger -t nikon connected starting ssh
        ssh -y -T -i /root/.ssh/id_dropbear -R 127.0.0.1:15740:192.168.1.1:15740 kamera@macgyver.fablab.fau.de 2>&1 | logger -t nikon &
    elif [ -z "${line##*disconnected*}" ]; then
        echo disconnected;
        logger -t nikon disconnnected stopping ssh \(pid $!\)
        kill $!
    fi;
done
