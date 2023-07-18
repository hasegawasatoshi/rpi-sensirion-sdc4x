import argparse
import logging
import os

import epaper
import yaml
from influxdb import InfluxDBClient
from PIL import Image, ImageDraw, ImageFont

DEFAULT_FONT_PATH = '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'

logging.basicConfig(
    format="[%(module)s] [%(levelname)s] %(message)s",
    level=logging.INFO)
logger = logging.getLogger('RPI-E-ink(epd2in66b)')


class EPaper:
    def __init__(self, module='epd2in66b'):
        self.base_x = 24
        self.base_y = 24
        self.offset_h = 36
        self.adjust_w = 120
        self.border_w = 16

        # Load font
        font_path = CONFIG.get('app').get('font').get('path') or DEFAULT_FONT_PATH
        self.font24 = ImageFont.truetype(os.path.join(os.path.dirname(font_path), os.path.basename(font_path)), 24)
        logger.info(f"Load font: {font_path})")

        # Initialize E-ink paper
        self.epd = epaper.epaper(module).EPD()
        self.epd.init()
        # self.Clear()
        logger.info(f"Initialize E-Paper ({module})")

    def draw(self, tempareture, humidity, co2):
        # Draw ambiant data
        HBlackimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 296*152
        drawblack = ImageDraw.Draw(HBlackimage)

        drawblack.rectangle((0, 0, self.epd.height, self.epd.width), fill=255)
        drawblack.text((self.base_x, self.base_y), u'CO2', font=self.font24, fill=0)
        drawblack.text((self.base_x, self.base_y + self.offset_h), u'気温', font=self.font24, fill=0)
        drawblack.text((self.base_x, self.base_y + self.offset_h * 2), u'湿度', font=self.font24, fill=0)

        text = u"%d ppm" % co2
        length = drawblack.textlength(text, font=self.font24)
        drawblack.text((self.epd.width - length + self.adjust_w, 24), text, font=self.font24, fill=0)

        text = u"%.1f ℃" % tempareture
        length = drawblack.textlength(text, font=self.font24)
        drawblack.text((self.epd.width - length + self.adjust_w, 24 + 36), text, font=self.font24, fill=0)

        text = u"%.1f ％" % humidity
        length = drawblack.textlength(text, font=self.font24)
        drawblack.text(
            (self.epd.width - length + self.adjust_w,
             self.base_y + self.offset_h * 2),
            text,
            font=self.font24,
            fill=0)

        # Draw border in red
        HRYimage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 296*152  ryimage: red or yellow image
        drawry = ImageDraw.Draw(HRYimage)
        drawry.rectangle((0, 0, self.epd.height, self.epd.width), fill=0)
        drawry.rectangle(
            (self.border_w,
             self.border_w,
             self.epd.height - self.border_w,
             self.epd.width - self.border_w),
            fill=255)

        # Display image
        self.epd.display(self.epd.getbuffer(HBlackimage), self.epd.getbuffer(HRYimage))


class DB:
    def __init__(self, host, port, dbuser, dbuser_password, dbname):
        self.client = InfluxDBClient(
            host, port, dbuser, dbuser_password, dbname)
        logger.info("Create InfluxDB client")

    def query(self, intervals):
        query = f'SELECT mean(tempareture) AS tempareture, mean(humidity) AS humidity, mean(co2) AS co2 FROM air_condition WHERE time > now() - {intervals} GROUP BY time({intervals}) ORDER BY DESC LIMIT 1;'
        result = self.client.query(query)
        points = list(result.get_points())
        data = {
            'tempareture': points[0].get('tempareture'),
            'humidity': points[0].get('humidity'),
            'co2': points[0].get('co2'),
            'ts': points[0].get('time')
        }
        logger.debug(data)
        return data


def main():
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

    display = EPaper()
    db = DB(
        CONFIG.get('influxdb').get('host'),
        CONFIG.get('influxdb').get('port'),
        CONFIG.get('influxdb').get('getdbuser'),
        CONFIG.get('influxdb').get('dbuser_password'),
        CONFIG.get('influxdb').get('dbname')
    )
    ambient = db.query(intervals=CONFIG.get('app').get('display').get('intervals'))
    display.draw(ambient.get('tempareture'), ambient.get('humidity'), ambient.get('co2'))
    logger.info("Updated")


if __name__ == '__main__':
    main()
