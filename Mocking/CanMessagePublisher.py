from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage
from can_protobuf.can_pb2 import CanData
from time import sleep
import random

from threading import Thread

import logging

logger = logging.getLogger(__name__)


class CanMessagePublisher(AbstractBlock, Thread):
    publish_topic = "can_messages"

    def __init__(self, name):
        AbstractBlock.__init__(self, name)
        Thread.__init__(self)

    def configure_block(self, configuration):
        pass

    def run(self):
        # create vehicle state message using mock data
        i = 0;
        while(True):
            i+=1
            can_message = CanData()
            can_message.id = random.randint(0,30)
            can_message.data = b'\n\n'
            dust_message = DustMessage(self.publish_topic, 0, can_message.SerializeToString())
            self.publish(self.publish_topic, dust_message)
            logger.info("Published message on can_messages")
            sleep(1)


