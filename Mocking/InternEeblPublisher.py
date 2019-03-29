from dust_eebl.dust_eebl_pb2 import EEBL
from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage
from time import sleep
import random

from threading import Thread

import logging

logger = logging.getLogger(__name__)


class InternEeblPublisher(AbstractBlock, Thread):
    publish_topic = "eebl_intern_gui"

    def __init__(self, name):
        AbstractBlock.__init__(self, name)
        Thread.__init__(self)

    def configure_block(self, configuration):
        pass

    def run(self):
        # create vehicle state message using mock data
        i = 0;
        while (i < 15):
            i+=1
            eebl = EEBL()
            eebl.location.lat_value = 51.28
            eebl.location.lon_value = 4.42
            eebl.speed = 50
            eebl.type = 2

            dust_message = DustMessage(self.publish_topic, 0, eebl.SerializeToString())
            self.publish(self.publish_topic, dust_message)
            eebl = EEBL()
            eebl.location.lat_value = 51.28
            eebl.location.lon_value = 4.42
            eebl.speed = 69
            eebl.type = 2


            dust_message = DustMessage(self.publish_topic, 0, eebl.SerializeToString())
            self.publish(self.publish_topic, dust_message)
            logger.info("Published message on " + self.publish_topic)
            sleep(0.1)
        while(True):
            eebl = EEBL()
            eebl.location.lat_value = 51.28
            eebl.location.lon_value = 4.42
            eebl.speed = 50
            eebl.type = 2


            dust_message = DustMessage(self.publish_topic, 0, eebl.SerializeToString())
            self.publish(self.publish_topic, dust_message)
            sleep(0.1)

            eebl = EEBL()
            eebl.location.lat_value = 51.28
            eebl.location.lon_value = 4.42
            eebl.speed = 50
            eebl.type = 2

            dust_message = DustMessage(self.publish_topic, 0, eebl.SerializeToString())
            self.publish(self.publish_topic, dust_message)

            sleep(0.1)

