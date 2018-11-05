#!/bin/bash

DATA_PATH='/home/yop/Programmation/Recherche/wsu_datasets/data'
OUTPUT_FILE='./HHActivities.py.generated'

TMPFILE=`mktemp HHActivitiesTempXXX`
cat $DATA_PATH/hh*/hh*/ann.txt | grep -e "end" -e "begin" | awk '{print $5}' | cut -d '=' -f 1 | sort | uniq | cut -d . -f2- | grep -E "^[A-Z].*" | sed 's/_//g' > $TMPFILE
cat $TMPFILE | sed "s/_//g" | sed -e "s/^\([A-Z].*\)/class \1Activity\(Activity\):\\n    pass\\n/" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "ACTIVITY_TYPE_TRANSLATION = {" >> $OUTPUT_FILE
cat $TMPFILE | sed -e "s/^\([A-Z].*\)/    \"\1\": \1Activity,/" | 
	sed "s/\"\([A-Z][a-z]*\)\([A-Z][a-z]*\)\([A-Z][a-z]*\)\([A-Z][a-z].*\)\"/\"\1_\2_\3_\4\"/" |
 	sed "s/\"\([A-Z][a-z]*\)\([A-Z][a-z]*\)\([A-Z][a-z]*\)\"/\"\1_\2_\3\"/" |
	sed "s/\"\([A-Z][a-z]*\)\([A-Z][a-z]*\)\"/\"\1_\2\"/" >> $OUTPUT_FILE
echo "}" >> $OUTPUT_FILE
rm $TMPFILE
