# labcamera
Automation tools for a digital camera used in a FabLab environment 

## Requirements
* Nikon DSLR with Wifi (we use a D5300)
* Linux Server with python2.7, gphoto2 and optionally sigal (we use shell.fablab.fau.de)
* OpenWRT Accesspoint (we use a TP-Link WR710N)

## Content
* `fablabap-config`: Contains the required configuration of the OpenWRT AP

to apply this configuration, archive the content of the folder to .tar.bz2 and upload via System->Backup/Flash Firmware option in OpenWRT Webinterface

* `server-config`: Contains the required files that are found in the user's home on a remote server

## Architecture (and current setup)
```
DSLR <-- fablabap --> shell.fablab.fau.de
  ^         /\            |
  +--------/  \-----------+
```

When Wireless is enabled on DSLR, it creates a Wifi network (SSID `Nikon_WU2_0090B529D73B`). The FabLabAP connects to it and the nikon.sh daemon (started from `/etc/rc.local` and found in `/root`) notices the connection and opens a reverse TCP tunnel between the camera and shell.fablab.fau.de via SSH (using the private key found `/root/.ssh/id_dropbear`).

Shell recognizes the ssh key and executes `/home/kamera/bin/nikon_connected.py`, as configured in `/home/kamera/.ssh/authorized_keys`. This script invokes gphoto2 to download the files from the DSLR via the revers TCP tunnel (thus it connects to localhost). It first gets a file list, filters not-yet downloaded files and then downloads the new ones. After all new files were downloaded, it uses gphoto2's `--capture-tethered` mode to wait for events emitted by the camera and download newly captured photos. All pictures are downloaded into `/home/kamera/pictures`.

After all new files (in the first pass) or a newly captured image (while waiting for events) was downloaded, the `/home/kamera/bin/gphoto2_hook.sh` scripted is executed. This script in turn initiates the uploading to smugmug (via `/home/kamera/bin/smugmug-uploader.py`) and rebuild of the local gallery (via `/home/kamera/bin/build_gallery.sh`). The `build_gallery.sh` is lockfile protected against parallel execution, so many new pictures won't kill the server.

## Configurations
The following files need to be configured to adapt these files to a new camera, hardware or configuration:

* `fablabap-config/etc/config/wireless`: SSID of Nikon DSLR (contains MAC address)
* `fablabap-config/root/nikon.sh`: MAC address of DSLR, username and hostname of shell.fablab.fau.de
* `server-config/bin/*`: scripts that handle connection between shell.fablab.fau.de and DSLR, downloads and processes new images
* `server-config/sigal.conf.py`: configuration of local gallery

## TODOs
* Make downloads possible that are longer then 30s (currently we get disconnected from the DSLR every 30s).

The solution is probably to get gphoto2 to keep the controll channel to the camera open. This should disable the 30s-disconnect.

* Make camap more versatile for out-of-lab use.

Check if AP is located outside of the FabLab and use OpenVPN to create a local network that gives access to all FAU FabLab services (such as fablab-share). This should be available via the wired LAN port and a new wireless network.
