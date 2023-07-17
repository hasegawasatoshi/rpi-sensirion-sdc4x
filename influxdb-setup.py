import argparse
import os

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
    user = config.get('influxdb').get('user') or 'root'
    password = config.get('influxdb').get('password') or 'root'
    dbuser = config.get('influxdb').get('dbuser') or 'scd4x'
    dbuser_password = config.get('influxdb').get(
        'dbuser_password') or 'changeme'
    dbname = config.get('influxdb').get('dbname') or 'ambient'
    retension = config.get('influxdb').get('retension') or '12w'

    port = os.environ.get('INFLUXDB_PORT', 8086)
    user = os.environ.get('INFLUXDB_USER', 'root')
    password = os.environ.get('INFLUXDB_PASSWORD', 'root')
    dbuser = os.environ.get('INFLUXDB_DBUSER', 'scd4x')
    dbuser_password = os.environ.get('INFLUXDB_DBUSER_PASS', 'scd4x')
    dbname = os.environ.get('INFLUXDB_DBNAME', 'ambient')
    retension = '156w'

    client = InfluxDBClient(host, port, user, password, dbname)

    print(f"Create database: {dbname}")
    client.create_database(dbname)

    print(f"Create a retention policy: {retension}")
    client.create_retention_policy(
        'ambient_raw_data_policy', retension, 1, default=True)

    print(f"Create a db user: {dbuser}")
    client.create_user(dbuser, dbuser_password)


if __name__ == '__main__':
    main()
