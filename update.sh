#!/bin/bash
# update.sh
#assumes files are already uploaded
#scp -r SomaFMBox <rpi-ip-address>:/home/[username]/     
# Usage: ./update.sh --remote_username "[USER_NAME]" --remote_host "[RPI-IP-ADDRESS]"


# Default values (if you want to set any defaults)
REMOTE_USER=""
REMOTE_HOST=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --remote_username)
            REMOTE_USER="$2"
            shift 2
            ;;
        --remote_host)
            REMOTE_HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter passed: $1"
            echo "Usage: $0 --remote_username <user> --remote_host <host>"
            exit 1
            ;;
    esac
done

# Ensure that both REMOTE_USER and REMOTE_HOST are set
if [[ -z "${REMOTE_USER}" || -z "${REMOTE_HOST}" ]]; then
    echo "Error: Both --remote_user and --remote_host must be provided."
    echo "Usage: $0 --remote_user <user> --remote_host <host>"
    exit 1
fi


REMOTE_BASE_DIR="/home/${REMOTE_USER}/SomaFMBox"

echo "Uploading Files script..."
scp somafm_box.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/
scp dials/dials.ino ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE_DIR}/dials/

#broadcast the following:
echo "Compiling Arduino sketch..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_BASE_DIR}/dials && arduino-cli compile --fqbn arduino:mbed_nano:nano33ble ."
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_BASE_DIR}/dials && arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:mbed_nano:nano33ble ."

#Start the Stream
echo "Starting The Radio Broadcast..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "python3 ${REMOTE_BASE_DIR}/somafm_box.py"
