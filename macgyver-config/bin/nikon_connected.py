#!/usr/bin/env python

import os
import sys
import subprocess
import operator

os.chdir('/home/kamera/pictures/')
gphoto_call = ['gphoto2', '--port', 'ptpip:127.0.0.1']

print "getting new images"
try:
    # get file list from camera
    cam_ls = subprocess.check_output(gphoto_call + ['--list-files'])
    cam_ls = [l[1:].split()[0:2] for l in cam_ls.split('\n') if l.startswith('#')]
    local_ls = os.listdir('.')
    
    # Build list to download
    new_ls = [c for c in cam_ls if c[1] not in local_ls and c[1].endswith('.JPG')]
    for fnum, fname in new_ls:
        subprocess.call(gphoto_call + ['--get-file', fnum])

    # Rebuild gallery
    subprocess.call(['/home/kamera/bin/build_gallery.sh'])
    # Upload new photos
    subprocess.call(['/home/kamera/bin/smugmug-uploader.py', 'Camera Roll']+[fname for fnum, fname in new_ls])
except subprocess.CalledProcessError as e:
    print e

print "waiting for new pictures (and downloading)"
cmd = gphoto_call + ['--capture-tethered', '--keep', '--hook-script', '/home/kamera/bin/gphoto2_hook.sh'] 
subprocess.call(cmd)

