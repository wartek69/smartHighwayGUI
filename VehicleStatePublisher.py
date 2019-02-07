from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage
from vehicle_state.vehicle_state_pb2 import VehicleState, Type
from time import sleep

from threading import Thread

import logging

logger = logging.getLogger(__name__)


class VehicleStatePublisher(AbstractBlock, Thread):
    publish_topic = "vehicle_state"
    def __init__(self, name):
        AbstractBlock.__init__(self, name)
        Thread.__init__(self)
    def configure_block(self, configuration):
        pass

    def run(self):
        # create vehicle state message
        while(True):
            vehicle_state_message = VehicleState()
            vehicle_state_message.type = 1
            vehicle_state_message.value = 65
            dust_message = DustMessage(self.publish_topic, 0, vehicle_state_message.SerializeToString())
            self.publish(self.publish_topic, dust_message)
            logger.info("Published message on vehicle_state")
            sleep(1)

