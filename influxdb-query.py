import argparse
import json

import yaml
from influxdb import InfluxDBClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.yaml')
    args = parser.parse_args()

    with open(args.config) as file:
        config = yaml.safe_load(file.read())
        print("Configuration: {0}".format(config))

    host = config.get('influxdb').get('host') or 'localhost'
    port = config.get('influxdb').get('port') or 8086
    dbuser = config.get('influxdb').get('dbuser') or 'scd4x'
    dbuser_password = config.get('influxdb').get('dbuser_password') or 'changeme'
    dbname = config.get('influxdb').get('dbname') or 'ambient'

    client = InfluxDBClient(host, port, dbuser, dbuser_password, dbname)

    query = 'select tempareture, humidity, co2 from air_condition where time > now() - 10m;'
    result = client.query(query)
    print(json.dumps(list(result.get_points()), indent=2))


if __name__ == '__main__':
    main()
