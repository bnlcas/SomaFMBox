#!/usr/bin/env python3
import serial
import subprocess
import time
import os
import signal

# /dev/ttyACM0 or /dev/ttyUSB0)
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

channels = ["http://ice1.somafm.com/defcon-128-mp3",
            "http://ice1.somafm.com/secretagent-128-mp3",
            "http://ice1.somafm.com/groovesalad-128-mp3",
            "http://ice1.somafm.com/dronezone-128-mp3",
]

police_scanner_url = "http://ice1.somafm.com/scanner-128-mp3"

# Globals for streaming processes
current_process = None
police_scanner_process = None

def start_stream(url):
    global current_process
    # If a process is running, kill it
    if current_process is not None:
        try:
            current_process.kill()
        except Exception as e:
            print("Error killing process:", e)
    # Start new stream (using curl piped to mpg321)
    print("Starting stream:", url)
    current_process = subprocess.Popen(["bash", "-c", f"curl -s {url} 2>&1 | mpg321 -"],
                                        preexec_fn=os.setsid)
    
def toggle_police_scanner_stream(start_stream):
    global police_scanner_process
    if (police_scanner_process is not None) and (not start_stream):
        try:
            police_scanner_process.kill()
        except Exception as e:
            print("Error killing police scanner process:", e)
    elif start_stream:
        police_scanner_process = subprocess.Popen(["bash", "-c", f"curl -s {police_scanner_url} 2>&1 | mpg321 -"],
                                        preexec_fn=os.setsid)
    
def set_volume(volume):
    # This example uses 'amixer' to set the Master volume. Adjust as necessary.
    print(f"Setting volume to {volume}%")
    subprocess.call(["amixer", "set", "Master", f"{volume}%"])

def terminate_stream():
    # Restart the stream. In this example, we just kill the process; you could also call start_stream() with a default channel.
    global current_process
    print("Resetting stream...")
    if current_process is not None:
        try:
            current_process.kill()
            current_process = None
        except Exception as e:
            print("Error resetting:", e)
    # Optionally, restart the default stream after a brief delay:
    #time.sleep(1)
    # For example, restart channel 0
    #start_stream(channels[0])

def main():
    global current_process
    # Open serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # wait for Arduino to reset if needed
    
    # Start with a default stream (say channel 0)
    start_stream(channels[0])
    
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                print("Received:", line)
                if line.startswith("CHANNEL:"):
                    try:
                        channel_number = int(line.split(":")[1])
                        channel_number = channel_number % len(channels)
                        if(channel_number < 0):
                            channel_number += len(channels)
                            start_stream(channels[channel_number])
                        else:
                            print("Channel not defined.")
                    except ValueError:
                        print("Invalid channel number.")
                elif line.startswith("VOLUME:"):
                    try:
                        volume = int(line.split(":")[1])*6
                        set_volume(volume)
                    except ValueError:
                        print("Invalid volume value.")
                elif line == "SCANNER_ON":
                    toggle_police_scanner_stream(True)
                elif line == "SCANNER_OFF":
                    # Return to default or previous channel; here we simply restart channel 0
                    toggle_police_scanner_stream(False)
                elif line == "OFF":
                    terminate_stream()
                elif line == "ON":
                    start_stream()
                # Add other commands as needed
        except Exception as e:
            print("Error:", e)
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if current_process is not None:
            try:
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            except Exception as e:
                print("Error killing process group:", e)
        print("Exiting.")
