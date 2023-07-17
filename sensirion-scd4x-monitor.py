import argparse
import logging
import signal
import time
from datetime import datetime, timezone

import adafruit_scd4x
import board
import yaml
from influxdb import InfluxDBClient

logging.basicConfig(
    format="[%(module)s] [%(levelname)s] %(message)s",
    level=logging.INFO)
logger = logging.getLogger('RPI-SCD4x')


class TerminatedException(Exception):
    pass


def signal_handler(signum, frame):
    logging.info('Catched signal [ %d ].' % (signum))
    raise TerminatedException


class SCD4x:
    def __init__(self):
        self.i2c = board.I2C()
        self.scd4x = adafruit_scd4x.SCD4X(self.i2c)
        logger.info("Serial number: %s" % " ".join(
            [hex(i) for i in self.scd4x.serial_number]))
        self.scd4x.start_periodic_measurement()
        logger.info("Start measurement")

    def __del__(self):
        self.scd4x.stop_periodic_measurement()
        logger.info("Stop measurement")

    def read(self):
        if self.scd4x.data_ready:
            return (self.scd4x.CO2, self.scd4x.temperature, self.scd4x.relative_humidity)
        return None


class DB:
    def __init__(self, host, port, dbuser, dbuser_password, dbname):
        self.client = InfluxDBClient(
            host, port, dbuser, dbuser_password, dbname)

    def write(self, co2, temperature, humidity):
        data = [
            {
                "measurement": "air_condition",
                "tags": {
                    "host": "raspberry-pi-01"
                },
                "time": datetime.now(timezone.utc).isoformat(),
                "fields": {
                    "tempareture": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "co2": co2
                }
            }
        ]
        logger.debug(data)
        self.client .write_points(data)


def mainloop(sensor, db):
    try:
        while True:
            readings = sensor.read()
            if readings is not None:
                logger.debug("CO2: %d ppm" % readings[0])
                logger.debug("Temperature: %0.1f *C" % readings[1])
                logger.debug("Humidity: %0.1f %%" % readings[2])
                db.write(readings[0], readings[1], readings[2])
            time.sleep(3)

    except KeyboardInterrupt:
        logger.error('Stopped by keyboard imput (ctrl-c)')

    except TerminatedException:
        logger.error('Stopded by systemd.')

    except OSError as e:
        import traceback
        traceback.print_exc()
        raise e

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

    finally:
        logger.info('Cleanup and stop SCD4x monitoring service.')


if __name__ == '__main__':
    logger.info("Sensirion SCD4x monitoring service started.")
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="enable debug log",
                        action="store_true")
    parser.add_argument('-c', '--config', default='config.yaml')
    args = parser.parse_args()

    if args.debug:
        logger.info("Enable debug log.")
        logging.getLogger().setLevel(logging.DEBUG)

    with open(args.config) as file:
        global CONFIG
        CONFIG = yaml.safe_load(file.read())
        logger.info("Configuration: {0}".format(CONFIG))

    sensor = SCD4x()
    db = DB(
        CONFIG.get('influxdb').get('host'),
        CONFIG.get('influxdb').get('port'),
        CONFIG.get('influxdb').get('getdbuser'),
        CONFIG.get('influxdb').get('dbuser_password'),
        CONFIG.get('influxdb').get('dbname')
    )
    mainloop(sensor, db)
