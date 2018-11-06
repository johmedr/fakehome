#! /bin/bash 

PROC_NB=16
POPU_DIR="`pwd`/$1"

curl -s http://casas.wsu.edu/datasets/ | sed -n 's/.*href="\([^"]*\).*/\1/p' | grep 'http://casas.wsu.edu/datasets/' | grep '.zip' | xargs -P $PROC_NB wget -P "$POPU_DIR/archives" -N -q --show-progress

ls "$POPU_DIR/archives" | sed 's/\.zip$//' | xargs -P $PROC_NB -I{} sh -c "unzip -n \"$POPU_DIR/{}.zip\" -d \"$POPU_DIR/{}\" | awk 'BEGIN { ORS = \" \" } { print \"Extracted files $POPU_DIR/{}.zip to $POPU_DIR/{}/\\n\" }'"

ls -d $POPU_DIR/hh*/hh*/ | cut -d / -f 1 | xargs -I{} wget -P "$POPU_DIR/{}/{}/" -N -q --show-progress http://ailab.wsu.edu/casas/hh/{}/sensormap.png 
ls -d $POPU_DIR/hh*/hh*/ | cut -d / -f 1 | xargs -I{} wget -P "$POPU_DIR/{}/{}/" -N -q --show-progress http://ailab.wsu.edu/casas/hh/{}/hh.jpg 
