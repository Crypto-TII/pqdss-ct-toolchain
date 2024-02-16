#!/bin/bash

# SMACK
# Clone SMACK repository
SMACK_TMP_DIR=/tmp/smack
git clone https://github.com/smackers/smack $SMACK_TMP_DIR

# Build SMACK
cd $SMACK_TMP_DIR || exit
bin/build.sh
# echo "source /home/user/smack.environment" >> ~/.bashrc

## BAM
#BAM_TMP_DIR=/tmp/bam
#git clone https://github.com/michael-emmi/bam-bam-boogieman $BAM_TMP_DIR