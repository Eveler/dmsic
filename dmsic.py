# -*- encoding: utf-8 -*-

# Author: Savenko Mike

import logging
import os
import smtplib
from configparser import ConfigParser, NoSectionError, NoOptionError
from email.mime.text import MIMEText
from logging.handlers import TimedRotatingFileHandler
from os.path import expanduser
from sys import exc_info
from traceback import format_exception

from qtui import Ui
# from db import Db
from smev import Adapter


class Integration:
    def __init__(self, ui=None, use_config=True,
                 config_path='./dmsic.ini'):
        logging.basicConfig(
            format='%(asctime)s %(name)s:%(module)s(%(lineno)d): '
                   '%(levelname)s: %(message)s', level=logging.INFO)
        if use_config:
            self.parse_config(config_path)
        else:
            self.mail_addr = ''
            self.smev_wsdl = "http://smev3-d.test.gosuslugi.ru:7500/smev/v1.2/ws?wsdl"
            self.smev_ftp = "ftp://smev3-d.test.gosuslugi.ru/"
            self.directum_wsdl = "http://snadb:8082/IntegrationService.svc?singleWsdl"
            self.smev_uri = 'urn://augo/smev/uslugi/1.0.0'
            self.local_name = 'directum'
            self.cert_method = 'sharp'
            self.mail_server, self.ftp_user, self.ftp_pass = None, None, None

        self.ui = ui

        try:
            self.__smev = Adapter(
                self.smev_wsdl, self.smev_ftp, method=self.cert_method,
                serial=self.crt_serial, container=self.container,
                crt_name=self.crt_name)
        except Exception:
            self.report_error()

        # self.db = Db()

    @property
    def smev(self):
        if not self.__smev:
            try:
                self.__smev = Adapter(
                    self.smev_wsdl, self.smev_ftp, method=self.cert_method,
                    serial=self.crt_serial, container=self.container,
                    crt_name=self.crt_name)
            except Exception:
                self.report_error()

        return self.__smev

    @smev.setter
    def smev(self, value):
        self.__smev = value

    def send(self, declar):
        self.smev.send_request(declar)

    def get_response(self):
        return self.smev.get_response()

    def parse_config(self, config_path):
        """
        Read the configuration. If something is missing, write the default one.
        """

        cfg = ConfigParser()
        do_write = False
        # If an exception, report it end exit
        try:
            lst = cfg.read(
                ["c:/dmsic/dmsic.ini", expanduser("~/dmsic.ini"), "./dmsic.ini",
                 config_path])
            if lst:
                logging.info('Configuration loaded from: %s' % lst)
            else:
                logging.warning('No config files found. Using default')
                lst = [os.path.abspath("./dmsic.ini")]
                logging.info('Configuration stored in: %s' % lst)

            if not cfg.has_section("main"):
                do_write = True
                cfg.add_section("main")
                cfg.set("main", "logfile", "dmsic.log")
                cfg.set("main", "loglevel", "warning")
                cfg.set("main", "log_count", "7")
            if not cfg.has_option("main", "logfile"):
                do_write = True
                cfg.set("main", "logfile", "dmsic.log")
            backupcount = 7
            if "log_count" in cfg.options("main"):
                backupcount = int(cfg.get("main", "log_count"))
            else:
                do_write = True
                cfg.set("main", "log_count", "7")
            handler = TimedRotatingFileHandler(
                os.path.abspath(cfg.get("main", "logfile")), when='D',
                backupCount=backupcount, encoding='cp1251')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s %(name)s:%(module)s(%(lineno)d): %(levelname)s: '
                '%(message)s'))
            logging.root.addHandler(handler)
            if "loglevel" not in cfg.options("main"):
                do_write = True
                cfg.set("main", "loglevel", "warning")
            loglevel = cfg.get("main", "loglevel").upper()
            logging.info("Set logging level to '%s'", loglevel)
            logging.root.setLevel(loglevel)
            if 'mail_addr' not in cfg.options('main'):
                do_write = True
                cfg.set('main', 'mail_addr', '')
            self.mail_addr = cfg.get('main', 'mail_addr')
            if 'mail_server' not in cfg.options('main'):
                do_write = True
                cfg.set('main', 'mail_server', '')
            self.mail_server = cfg.get('main', 'mail_server')

            if not cfg.has_section("smev"):
                do_write = True
                cfg.add_section('smev')
                cfg.set(
                    'smev', 'wsdl',
                    "http://172.20.3.12:7500/smev/v1.2/ws?wsdl")
                cfg.set('smev', 'ftp', "ftp://172.20.3.12/")
            if 'uri' in cfg.options('smev'):
                self.smev_uri = cfg.get('smev', 'uri')
            else:
                self.smev_uri = 'urn://augo/smev/uslugi/1.0.0'
            if 'local_name' in cfg.options('smev'):
                self.local_name = cfg.get('smev', 'local_name')
            else:
                # self.local_name = 'directum'
                self.local_name = 'declar'
            if 'wsdl' not in cfg.options('smev'):
                do_write = True
                cfg.set(
                    'smev', 'wsdl',
                    "http://172.20.3.12:7500/smev/v1.2/ws?wsdl")
            self.smev_wsdl = cfg.get('smev', 'wsdl')
            if 'ftp' not in cfg.options('smev'):
                do_write = True
                cfg.set('smev', 'ftp', "ftp://172.20.3.12/")
            self.smev_ftp = cfg.get('smev', 'ftp')
            if 'method' not in cfg.options('smev'):
                do_write = True
                cfg.set('smev', 'method', "sharp")
            self.cert_method = cfg.get('smev', 'method').lower()
            if 'crt_serial' in cfg.options('smev'):
                self.crt_serial = cfg.get('smev', 'crt_serial')
            else:
                raise Exception('Ошибка в настройках: необходимо указать '
                                'crt_serial в секции smev')
            if 'container' in cfg.options('smev'):
                self.container = cfg.get('smev', 'container')
            else:
                raise Exception('Ошибка в настройках: необходимо указать '
                                'container в секции smev')
            if 'crt_name' in cfg.options('smev'):
                self.crt_name = cfg.get('smev', 'crt_name')
            else:
                raise Exception('Ошибка в настройках: необходимо указать '
                                'crt_name в секции smev')
            if 'ftp_user' in cfg.options('smev'):
                self.ftp_user = cfg.get('smev', 'ftp_user')
            else:
                self.ftp_user = None
            if 'ftp_pass' in cfg.options('smev'):
                self.ftp_pass = cfg.get('smev', 'ftp_pass')
            else:
                self.ftp_pass = None

            if do_write:
                for fn in lst:
                    with open(fn, "w") as configfile:
                        cfg.write(configfile)
                        configfile.close()
        except NoSectionError:
            self.report_error()
            quit()
        except NoOptionError:
            self.report_error()
        except Exception:
            if do_write:
                for fn in lst:
                    with open(fn, "w") as configfile:
                        cfg.write(configfile)
                        configfile.close()
            raise

    def report_error(self):
        etype, value, tb = exc_info()
        trace = ''.join(format_exception(etype, value, tb))
        msg = ("*" * 70 + "\n%s\n" + "*" * 70) % trace
        logging.error(msg)

        if self.ui:
            self.ui.report_error(msg)

        if self.mail_server:
            from_addr = 'admin@adm-ussuriisk.ru'
            message = MIMEText(msg)
            message['Subject'] = 'SMEV integration error'
            message['From'] = from_addr
            message['To'] = self.mail_addr

            try:
                s = smtplib.SMTP(self.mail_server)
                s.sendmail(from_addr, [self.mail_addr], message.as_string())
                s.quit()
            except smtplib.SMTPException:
                etype, value, tb = exc_info()
                trace = ''.join(format_exception(etype, value, tb))
                msg = ("%s" + "\n" + "*" * 70 + "\n%s\n" + "*" * 70) % (
                    value, trace)
                logging.error(msg)


def main():
    ui = Ui()
    ui.exec()


if __name__ == '__main__':
    main()
