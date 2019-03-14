from collections import namedtuple
from os import system
from datetime import datetime, timedelta
from calendar import timegm
import _thread
from time import sleep
from gps_protobuf.gps_pb2 import GpsData
from dust_eebl.dust_eebl_pb2 import EEBL, EEBL_Location, EEBL_Type
from vehicle_state import vehicle_state_pb2
from vehicle_state.vehicle_state_pb2 import VehicleState, Type
from can_protobuf.can_pb2 import CanData
import vehicle_state.vehicle_state_pb2

import logging

from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage

logger = logging.getLogger(__name__)

# block used to communicate with the dust framework and represent the data in a web app
class CommunicationBlock(AbstractBlock):

    publish_topic = []
    eebl_intern_timeout = datetime.now() - timedelta(seconds=0.25)
    eebl_extern_timeout = datetime.now() - timedelta(seconds=1)
    gps_timeout = datetime.now() - timedelta(seconds=2)

    # t variables used to prevent spamming the client with timeouts -> one timeout enough
    tintern = False;
    textern = False;
    tgps = False;
    tvehiclestate = False;

    # list of vehicle state timeouts
    vehicle_state_timeouts = {}
    VehicleStateTimeout = namedtuple('VehicleStateTimeout', 'timeout last_update')

    # list of canmessage timeouts
    can_messages_timeouts = {}
    CanMessagesTimeout = namedtuple('CanStateTimeout', 'timeout last_update')

    def __init__(self, name, socketio):
        AbstractBlock.__init__(self, name)
        self.socketio = socketio

    def setSocketio(self, socketio):
        self.socketio = socketio

    def timeout_check(self):
        while True:
            sleep(0.1)
            self.on_message("timeout", None)

    def configure_block(self, configuration):
        _thread.start_new_thread(self.timeout_check, ())

    def check_time_outs(self):
        if self.eebl_intern_timeout < datetime.now() - timedelta(seconds=0.25) and self.tintern == False:
            self.tintern = True
            self.socketio.emit('eebl_intern', {'info': "Intern: NaN"})
        if self.eebl_extern_timeout < datetime.now() - timedelta(seconds=1) and self.textern == False:
            self.textern = True
            self.socketio.emit('eebl_extern', {'timeout': 'true'})
        if self.gps_timeout < datetime.now() - timedelta(seconds=2) and self.tgps == False:
            self.tgps = True
            self.socketio.emit('newgps', {'timeout': 'true'})

        for state_type, vehicle_state_timeout in list(self.vehicle_state_timeouts.items()):
            if vehicle_state_timeout.last_update < datetime.now() - timedelta(
                    seconds=2) and vehicle_state_timeout.timeout == False:
                del self.vehicle_state_timeouts[state_type]
                self.socketio.emit('vehicle_state', {'type': state_type,
                                                     'timeout': 'true'})

        for can_message_id, can_message_timeout in list(self.can_messages_timeouts.items()):
            if can_message_timeout.last_update < datetime.now() - timedelta(seconds=2) and can_message_timeout.timeout == False:
                del self.can_messages_timeouts[can_message_id]
                self.socketio.emit('can_messages', {'id': can_message_id,
                                                     'timeout': 'true'})

    def on_message(self, topic: str, message: DustMessage):
        """Implement on message callback."""

        self.check_time_outs()

        if topic == 'eebl_intern' or topic == 'eebl_intern_gui':
            eebl = EEBL()
            eebl.ParseFromString(message.get_payload_bytes())
            text = "Intern: NaN"
            if eebl.type == EEBL_Type.Value("OK"):
                text = "Intern: Ok"
                self.socketio.emit('eebl_intern', {'info':text})

            if eebl.type == EEBL_Type.Value("OBJECT_DETECTED"):
                text = "Intern: OBJECT_DETECTED at {0:.4f}, {1:.4f} at speed {2:.2f}".format(eebl.location.lat_value,
                                                                                             eebl.location.lon_value,
                                                                                             eebl.speed)
                self.socketio.emit('eebl_intern_det', {'eebl_lat': eebl.location.lat_value,
                                                       'eebl_lon': eebl.location.lon_value,
                                                       'speed': eebl.speed,
                                                       'timeout': 'false'})

            if eebl.type == EEBL_Type.Value("SENSOR_FAILURE"):
                text = "Intern: SENSOR FAILURE"
                self.socketio.emit('eebl_intern', {'info':text})

            logger.debug(text)
            self.eebl_intern_timeout = datetime.now()
            self.tintern = False

        if topic == 'eebl_extern':
            eebl = EEBL()
            eebl.ParseFromString(message.get_payload_bytes())
            text = "Intern: OBJECT_DETECTED at {0:.4f}, {1:.4f} at speed {2:.2f}".format(eebl.location.lat_value,
                                                                                         eebl.location.lon_value,
                                                                                         eebl.speed)
            self.socketio.emit('eebl_extern', {'eebl_lat': eebl.location.lat_value,
                                               'eebl_lon': eebl.location.lon_value,
                                               'speed': eebl.speed,
                                               'timeout': 'false'})
            logger.debug(text)
            # if self.eebl_extern_timeout < datetime.now() - timedelta(seconds=1):
            #     system('play --no-show-progress --null --channels 1 synth %s sine %f' % (0.25, 1000))
            self.eebl_extern_timeout = datetime.now()
            self.textern = False

        if topic == 'gps':
            gps_data = GpsData()
            gps_data.ParseFromString(message.get_payload_bytes())
            print("Own Location: {0:.8f}, {1:.8f} at speed {2:.4f}".format(gps_data.lat_value,
                                                                                      gps_data.lon_value,
                                                                                      gps_data.speed_value))
            self.socketio.emit('newgps',{'gps_lat': gps_data.lat_value,
                                         'gps_lon': gps_data.lon_value,
                                         'speed': gps_data.speed_value,
                                         'timeout': 'false'})
            self.gps_timeout = datetime.now()
            self.tgps = False
        if topic == 'vehicle_state':
            logger.info("Vehicle state message arrived")
            vehicle_state = VehicleState()
            vehicle_state.ParseFromString(message.get_payload_bytes())
            # convert number to enum names
            varname = vehicle_state_pb2._TYPE.values_by_number[vehicle_state.type].name
            logger.debug(varname)
            self.socketio.emit('vehicle_state', {'type': varname,
                                                 'value': vehicle_state.value,
                                                 'timeout': 'false'})
            self.vehicle_state_timeouts[varname] = self.VehicleStateTimeout(False, datetime.now())
        if topic =='can_messages':
            logger.info("Can message arrived!")
            can_message = CanData()
            can_message.ParseFromString(message.get_payload_bytes())
            logger.debug(can_message.data.hex())
            self.socketio.emit('can_messages', {'id': can_message.id,
                                                'value': can_message.data.hex(),
                                                'timeout': 'false'})
            self.can_messages_timeouts[can_message.id] = self.CanMessagesTimeout(False, datetime.now())




    def on_message_lost(self, topic, message_id):
        """Implement message lost callback."""
        pass
