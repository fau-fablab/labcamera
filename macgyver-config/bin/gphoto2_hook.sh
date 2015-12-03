#!/bin/sh

case "$ACTION" in
  download)
    /home/kamera/bin/build_gallery.sh
    /home/kamera/bin/smugmug-uploader.py 'Camera Roll' "$ARGUMENT"
    ;;
esac
