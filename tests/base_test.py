__author__ = 'nico'

from yousign.client import Client
import logging
import sys

sys.path.append('../yousign')

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

login = 'nico'
password = 'passwd'
api_key = 'keyyyyyy'

client = Client(wl_login, wl_password, api_key, debug=True)
