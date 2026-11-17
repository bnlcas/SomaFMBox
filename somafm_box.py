#!/usr/bin/env python3
import time
import serial
import subprocess
import os
import signal
from weather_forecast import WeatherForecast

# /dev/ttyACM0 or /dev/ttyUSB0)
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

print('starting the radio')
print(f'path: {os.getcwd()}')

#FIP urls: https://gist.github.com/harperreed/b5ceabbbbca0a79d478ec0b81f449892
channels = ["https://somafm.com/dronezone.pls",
            "file:golden_record_sounds.wav",
            "https://somafm.com/secretagent.pls",
            "https://somafm.com/groovesalad.pls",
            "https://somafm.com/defcon.pls",
            "https://somafm.com/deepspaceone.pls",
            "https://somafm.com/thetrip.pls",
            "https://somafm.com/beatblender.pls",
            "https://somafm.com/lush.pls",
            "https://icecast.radiofrance.fr/fip-midfi.mp3?id=radiofrance",
            "https://icecast.radiofrance.fr/fippop-midfi.mp3?id=radiofrance",
            "https://icecast.radiofrance.fr/fipworld-midfi.mp3?id=radiofrance"
]

channel_ind = 0
system_volume = 25

police_scanner_url = "https://somafm.com/scanner.pls"
#"http://ice1.somafm.com/scanner-128-mp3"

# Globals for streaming processes
current_process = None
police_scanner_process = None

weather_forecast = WeatherForecast()

def start_stream(url):
    global current_process
    # If a process is running, kill it
    if current_process is not None:
        try:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            #current_process.kill()
        except Exception as e:
            print("Error killing process:", e)
    # Start new stream (using curl piped to mpg321)
    print("Starting stream:", url)
    #also tried; #mpv -"],#mpg321 -"], -a hw:3,0
    # -a plughw:3,0    
    current_process = subprocess.Popen(["bash", "-c", f"curl -s {url} 2>&1 | mpg321 -"],
                                        preexec_fn=os.setsid)
    print("Started process with PID:", current_process.pid)

def start_file_stream(filename):
    global current_process
    # If a process is running, kill it
    if current_process is not None:
        try:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            #current_process.kill()
        except Exception as e:
            print("Error killing process:", e)
    # Start new stream (using curl piped to mpg321)
    #also tried; #mpv -"],#mpg321 -"], -a hw:3,0
    # -a plughw:3,0
    filepath = '/home/atom/SomaFMBox/assets/' + filename
    track_time = int(time.time() % 6602)
    current_process = subprocess.Popen(["bash", "-c", f"mpv {filepath} --start={track_time} --loop-file=inf"],
                                        preexec_fn=os.setsid)
    print("Started process with PID:", current_process.pid)
    

def toggle_police_scanner_stream(start_stream):
    global police_scanner_process
    if (police_scanner_process is not None) and (not start_stream):
        try:
            print('stopping police')
            #police_scanner_process.kill()
            os.killpg(os.getpgid(police_scanner_process.pid), signal.SIGTERM)
        except Exception as e:
            print("Error killing police scanner process:", e)
    elif start_stream:
        if(time.localtime().tm_hour < 11):
            weather_forecast.speak_todays_forecast()
        print('starting police') #["bash", "-c", fcurl -s {police_scanner_url} 2>&1 | mpg321 -a plughw:3,0 -"],        
        police_scanner_process = subprocess.Popen(["bash", "-c", f"curl -s {police_scanner_url} 2>&1 | mpg321 -"],
                                        preexec_fn=os.setsid)
    
def set_volume(volume, invert = False):
    # This example uses 'amixer' to set the Master volume. Adjust as necessary.
    if invert:
        volume = 100 - volume
    print(f"Setting volume to {volume}%")
    subprocess.call(["amixer", "-c", "3", "set", "PCM", f"{volume}%"])

def terminate_stream():
    # Restart the stream. In this example, we just kill the process; you could also call start_stream() with a default channel.
    global current_process
    print("Resetting stream...")
    if current_process is not None:
        try:
            #current_process.kill()
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            current_process = None
        except Exception as e:
            print("Error resetting:", e)
    else:
        print("no process")
    # Optionally, restart the default stream after a brief delay:
    #time.sleep(1)
    # For example, restart channel 0
    #start_stream(channels[0])

def main():
    global current_process
    global police_scanner_process
    global channels
    global channel_ind
    global system_volume
    # Open serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    set_volume(system_volume)
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
                        channel_ind = int(line.split(":")[1])
                        channel_ind = channel_ind % len(channels)
                        if(channel_ind < 0):
                            channel_ind += len(channels)
                        if(channels[channel_ind].split(':')[0] == 'file'):
                            start_file_stream(channels[channel_ind].split(':')[1])
                        else:
                            start_stream(channels[channel_ind])
                        print(f'Set to channel {channel_ind}')
                    except ValueError:
                        print("Invalid channel number.")
                elif line.startswith("VOLUME:"):
                    try:
                        volume = int(line.split(":")[1])
                        #set_volume(volume)
                    except ValueError:
                        print("Invalid volume value.")
                elif line.startswith("DELTA_VOLUME:"):
                    try:
                        system_volume +=  int(line.split(":")[1])*4
                        if(system_volume > 100):
                            system_volume -= 100
                        if(system_volume < 0):
                            system_volume += 100
                        set_volume(system_volume)
                    except ValueError:
                        print("wrong system volume")
                elif line == "SCANNER_ON":
                    toggle_police_scanner_stream(True)
                elif line == "SCANNER_OFF":
                    # Return to default or previous channel; here we simply restart channel 0
                    toggle_police_scanner_stream(False)
                elif line == "OFF":
                    terminate_stream()
                elif line == "ON":
                    print('nothing yet')
                    #start_stream(channels[channel_ind])
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
                print("killing current stream")
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            except Exception as e:
                print("Error killing process group:", e)
        if police_scanner_process is not None:
            try:
                os.killpg(os.getpgid(police_scanner_process.pid), signal.SIGTERM)
            except Exception as e:
                print("Error killing process group:", e)
        print("Exiting.")