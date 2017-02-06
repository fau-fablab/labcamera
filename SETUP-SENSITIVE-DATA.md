# SETUP Private Data
--------------------

## server-config
In file `server-config/bin/smugmug-uploader.py`:
* set EMAIL to the adress with which you registered with Smugmug
* set PASSWORD to your Smugmug Password
* set APIKEY to your Smugmug API-Key

## openwrt-config
In file openwrt-config/etc/dropbear/authorized_keys, add a public key for accessing the system.
In the same directory add the hostkeys (dropbear_rsa_host_key and dropbear_dss_host_key).
Add a SSH-key to openwrt/root/.ssh/id_dropbear. This allows to trigger nikon.sh on the server via the authorized_keys configuration.

Add your Password (password for accessing the router) hash in openwrt-config/etc/shadow.
