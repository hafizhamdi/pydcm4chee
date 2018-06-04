#!/usr/bin/python

import logging

logger = logging.getLogger('postdcm')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formater =logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formater)

logger.addHandler(ch)

