from os import system
from datetime import datetime, timedelta
from calendar import timegm
import _thread
from time import sleep
from gps_protobuf.gps_pb2 import GpsData
from dust_eebl.dust_eebl_pb2 import EEBL, EEBL_Location, EEBL_Type
import logging

from pydust.abstract_block import AbstractBlock
from pydust.dust_message import DustMessage

logger = logging.getLogger(__name__)


class CommunicationBlock(AbstractBlock):

    publish_topic = []
    eebl_intern_timeout = datetime.now() - timedelta(seconds=0.25)
    eebl_extern_timeout = datetime.now() - timedelta(seconds=1)
    gps_timeout = datetime.now() - timedelta(seconds=2)

    def setSocketio(self, socketio):
        self.socketio = socketio

    def timeout_check(self):
        while True:
            sleep(0.1)
            self.on_message("timeout", None)

    def configure_block(self, configuration):
        _thread.start_new_thread(self.timeout_check, ())

    def on_message(self, topic: str, message: DustMessage):
        """Implement on message callback."""
        # if self.eebl_intern_timeout < datetime.now() - timedelta(seconds=0.25):
        #     self.var_eebl_intern.set("Intern: NaN")
        # if self.eebl_extern_timeout < datetime.now() - timedelta(seconds=1):
        #     self.var_eebl_extern.set("Extern: NaN")
        # if self.gps_timeout < datetime.now() - timedelta(seconds=2):
        #     self.var_gps.set("Own Location: Nan, NaN")

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
                                                   'speed': eebl.speed})

            if eebl.type == EEBL_Type.Value("SENSOR_FAILURE"):
                text = "Intern: SENSOR FAILURE"
                self.socketio.emit('eebl_intern', {'info':text})


            logger.debug(text)
            self.eebl_intern_timeout = datetime.now()

        if topic == 'eebl_extern':
            eebl = EEBL()
            eebl.ParseFromString(message.get_payload_bytes())
            text = "Intern: OBJECT_DETECTED at {0:.4f}, {1:.4f} at speed {2:.2f}".format(eebl.location.lat_value,
                                                                                         eebl.location.lon_value,
                                                                                         eebl.speed)
            self.socketio.emit('eebl_extern', {'eebl_lat': eebl.location.lat_value,
                                               'eebl_lon': eebl.location.lon_value,
                                               'speed': eebl.speed})
            logger.debug(text)
            # if self.eebl_extern_timeout < datetime.now() - timedelta(seconds=1):
            #     system('play --no-show-progress --null --channels 1 synth %s sine %f' % (0.25, 1000))
            self.eebl_extern_timeout = datetime.now()

        if topic == 'gps':
            gps_data = GpsData()
            gps_data.ParseFromString(message.get_payload_bytes())
            print("Own Location: {0:.8f}, {1:.8f} at speed {2:.4f}".format(gps_data.lat_value,
                                                                                      gps_data.lon_value,
                                                                                      gps_data.speed_value))
            self.socketio.emit('newgps',{'gps_lat': gps_data.lat_value,
                                         'gps_lon': gps_data.lon_value,
                                         'speed': gps_data.speed_value})
            self.gps_timeout = datetime.now()

    def on_message_lost(self, topic, message_id):
        """Implement message lost callback."""
        pass
