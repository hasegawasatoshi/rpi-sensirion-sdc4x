# rpi-sensirion-sdc4x
Monitoring service for Sensirion SCD4x

## Usage

Create a virtual environment.
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt 
```

Configuration
```
cp config.yaml.sample config.yaml
vim config.yaml
```

Install InfluxDB
```
sudo apt install influxdb
sudo systemctl start influxdb
sudo systemctl enable influxdb
```

Setup InfluxDB
```
python influxdb-setup.py 
```

Install packages for e-Ink dispay
```
sudo apt install -y fonts-ipafont libopenjp2-7
```

Run the monitoring service
```
python sensirion-scd4x-monitor.py --debug
```

Comfirm readings
```
python influxdb-query.py
```

## Install

Install python modules in systemwide.
```
sudo pip install requirements.txt
```

Install related files.
```
sudo mkdir -p /opt/ambient/bin
sudo mkdir -p /opt/ambient/etc
sudo install -v -o root -g root -m 644 -t /opt/ambient/bin ./sensirion-scd4x-monitor.py
sudo install -v -o root -g root -m 644 -t /opt/ambient/bin ./waveshare-epd2in66b-display.py
sudo install -v -o root -g root -m 644 -t /opt/ambient/etc ./config.yaml
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system ./sensirion-scd4x-monitor.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system ./waveshare-epd2in66b-display.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system ./waveshare-epd2in66b-display.timer
sudo systemctl daemon-reload
```

Start and enable monitoring servcie.
```
sudo systemctl start sensirion-scd4x-monitor.service
sudo systemctl enable sensirion-scd4x-monitor.service
sudo systemctl start waveshare-epd2in66b-display.service
sudo systemctl enable waveshare-epd2in66b-display.service
sudo systemctl start waveshare-epd2in66b-display.timer
sudo systemctl enable waveshare-epd2in66b-display.timer
```
