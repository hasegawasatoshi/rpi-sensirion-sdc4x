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
python setup-influxdb.py 
```

Run the monitoring service
```
python sensirion-scd4x-monitor.py --debug
```

Comfirm readings
```
python query-data.py
```
