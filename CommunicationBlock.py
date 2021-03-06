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
import sys
from threading import Lock

import logging

from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage

import configparser

logger = logging.getLogger(__name__)


# block used to communicate with the dust framework and represent the data in a web app
class CommunicationBlock(AbstractBlock):
    lock = Lock()
    publish_topic = []
    eebl_intern_timeout = datetime.now() - timedelta(seconds=0.25)
    eebl_extern_timeout = datetime.now() - timedelta(seconds=1)
    gps_timeout = datetime.now() - timedelta(seconds=2)
    intern_timeout_value = 0.25
    extern_timeout_value = 1
    gps_timeout_value = 2
    vehicle_timeout_value = 2
    can_message_timeout_value = 2

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
        self.load_config_param()

    def load_config_param(self):
        config = configparser.ConfigParser()
        config.read('config/gui_config.ini')
        self.intern_timeout_value = float(config['MESSAGE']['EEBL_INTERN_TIMEOUT'])
        self.extern_timeout_value = float(config['MESSAGE']['EEBL_EXTERN_TIMEOUT'])
        self.gps_timeout_value = float(config['MESSAGE']['GPS_TIMEOUT'])
        self.vehicle_timeout_value = float(config['MESSAGE']['VEHICLE_STATE_TIMEOUT'])
        self.can_message_timeout_value = float(config['MESSAGE']['CAN_MESSAGE_TIMEOUT'])
        print('')

    def setSocketio(self, socketio):
        self.socketio = socketio

    def timeout_check(self):
        while True:
            sleep(0.1)
            self.on_message("timeout", None)

    def configure_block(self, configuration):
        _thread.start_new_thread(self.timeout_check, ())

    def check_time_outs(self):
        logger.debug("entered check_time_outs")
        # lock neccessary because different instances of
        self.lock.acquire()
        if self.eebl_intern_timeout < datetime.now() - timedelta(
                seconds=self.intern_timeout_value) and self.tintern == False:
            self.tintern = True
            self.socketio.emit('eebl_intern', {'info': "Intern: NaN"})
            self.socketio.emit('intern', {'timeout': 'true'})
        if self.eebl_extern_timeout < datetime.now() - timedelta(
                seconds=self.extern_timeout_value) and self.textern == False:
            self.textern = True
            self.socketio.emit('eebl_extern', {'timeout': 'true'})
            # extern timeout used on index page to update squares
            self.socketio.emit('extern', {'timeout': 'true'})
        if self.gps_timeout < datetime.now() - timedelta(seconds=self.gps_timeout_value) and self.tgps == False:
            self.tgps = True
            self.socketio.emit('newgps', {'timeout': 'true'})

        for state_type, vehicle_state_timeout in list(self.vehicle_state_timeouts.items()):
            if vehicle_state_timeout.last_update < datetime.now() - timedelta(
                    seconds=self.vehicle_timeout_value) and vehicle_state_timeout.timeout == False:
                logger.debug("about to delete vehicle timeout")
                del self.vehicle_state_timeouts[state_type]
                logger.debug("deleted vehicle timeout")

                self.socketio.emit('vehicle_state', {'type': state_type,
                                                     'timeout': 'true'})

        for can_message_id, can_message_timeout in list(self.can_messages_timeouts.items()):
            if can_message_timeout.last_update < datetime.now() - timedelta(
                    seconds=self.can_message_timeout_value) and can_message_timeout.timeout == False:
                logger.debug("about to delete can messages timeout")
                del self.can_messages_timeouts[can_message_id]
                logger.debug("deleted can messages timeout")

                self.socketio.emit('can_messages', {'id': can_message_id,
                                                    'timeout': 'true'})
        self.lock.release()

    def on_message(self, topic: str, message: DustMessage):
        """Implement on message callback."""
        logger.debug("entered on message")
        self.check_time_outs()

        if topic == 'eebl_intern' or topic == 'eebl_intern_gui':
            eebl = EEBL()
            eebl.ParseFromString(message.get_payload_bytes())
            text = "Intern: NaN"
            if eebl.type == EEBL_Type.Value("OK"):
                text = "Intern: Ok"
                self.socketio.emit('eebl_intern_info', {'info': text})
                self.socketio.emit('intern', {'type': 'OK',
                                              'timeout': 'false'})

            if eebl.type == EEBL_Type.Value("OBJECT_DETECTED"):
                text = "Intern: OBJECT_DETECTED at {0:.4f}, {1:.4f} at speed {2:.2f}".format(eebl.location.lat_value,
                                                                                             eebl.location.lon_value,
                                                                                             eebl.speed)
                self.socketio.emit('eebl_intern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'OBJECT',
                                                   'timeout': 'false'})
                self.socketio.emit('intern', {'type': 'OBJECT_DETECTED',
                                              'timeout': 'false'})

            if eebl.type == EEBL_Type.Value("SENSOR_FAILURE"):
                text = "Intern: SENSOR FAILURE"
                self.socketio.emit('eebl_intern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'SENSOR!',
                                                   'timeout': 'false'})
                self.socketio.emit('intern', {'type': 'SENSOR_FAILURE',
                                              'timeout': 'false'})
            if eebl.type == EEBL_Type.Value("UNKNOWN"):
                text = "Intern: UNKNOWN"
                self.socketio.emit('eebl_intern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'UNKNOWN',
                                                   'timeout': 'false'})
                self.socketio.emit('intern', {'type': 'UNKNOWN',
                                              'timeout': 'false'})

            logger.debug(text)
            self.eebl_intern_timeout = datetime.now()
            self.tintern = False

        if topic == 'eebl_extern':
            eebl = EEBL()
            eebl.ParseFromString(message.get_payload_bytes())

            if eebl.type == EEBL_Type.Value("OBJECT_DETECTED"):
                text = "Extern: OBJECT_DETECTED at {0:.4f}, {1:.4f} at speed {2:.2f}".format(eebl.location.lat_value,
                                                                                             eebl.location.lon_value,
                                                                                             eebl.speed)
                self.socketio.emit('eebl_extern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'OBJECT',
                                                   'timeout': 'false'})
                self.socketio.emit('extern', {'type': 'OBJECT_DETECTED',
                                              'timeout': 'false'});
            if eebl.type == EEBL_Type.Value("UNKNOWN"):
                text = "UNKNOWN"
                self.socketio.emit('extern', {'type': 'UNKNOWN',
                                              'timeout': 'false'});
                self.socketio.emit('eebl_extern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'UNKNOWN',
                                                   'timeout': 'false'})
            if eebl.type == EEBL_Type.Value("OK"):
                self.socketio.emit('eebl_extern_info', {'eebl_lat': eebl.location.lat_value,
                                                        'eebl_lon': eebl.location.lon_value,
                                                        'speed': eebl.speed,
                                                        'type': 'OK',
                                                        'timeout': 'false'})
                self.socketio.emit('extern', {'type': 'OK',
                                              'timeout': 'false'});

            if eebl.type == EEBL_Type.Value("SENSOR_FAILURE"):
                self.socketio.emit('eebl_extern', {'eebl_lat': eebl.location.lat_value,
                                                   'eebl_lon': eebl.location.lon_value,
                                                   'speed': eebl.speed,
                                                   'type': 'SENSOR!',
                                                   'timeout': 'false'})
                self.socketio.emit('extern', {'type': 'SENSOR_FAILURE',
                                              'timeout': 'false'});

            logger.debug(text)

            self.eebl_extern_timeout = datetime.now()
            self.textern = False

        if topic == 'gps':
            logger.debug("entered gps topic")
            gps_data = GpsData()
            gps_data.ParseFromString(message.get_payload_bytes())
            print("Own Location: {0:.8f}, {1:.8f} at speed {2:.4f}".format(gps_data.lat_value,
                                                                           gps_data.lon_value,
                                                                           gps_data.speed_value))
            self.socketio.emit('newgps', {'gps_lat': gps_data.lat_value,
                                          'gps_lon': gps_data.lon_value,
                                          'speed': gps_data.speed_value,
                                          'timeout': 'false'})
            self.gps_timeout = datetime.now()
            self.tgps = False
        if topic == 'vehicle_state':
            logger.info("Vehicle state message arrived")
            vehicle_state = VehicleState()
            logger.debug("Made vehicle_state object")
            vehicle_state.ParseFromString(message.get_payload_bytes())
            logger.debug(vehicle_state.type)

            # convert number to enum names
            varname = vehicle_state_pb2._TYPE.values_by_number[vehicle_state.type].name
            logger.debug(varname)
            self.socketio.emit('vehicle_state', {'type': varname,
                                                 'value': vehicle_state.value,
                                                 'timeout': 'false'})
            self.vehicle_state_timeouts[varname] = self.VehicleStateTimeout(False, datetime.now())
            logger.debug("left vehicle_state")

        if topic == 'can_messages':
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
        logger.debug("lost message")
        pass
