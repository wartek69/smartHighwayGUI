import threading

from flask import Flask, render_template
import logging
import sys
from CommunicationBlock import CommunicationBlock
from flask_socketio import SocketIO
import argparse

from VehicleStatePublisher import VehicleStatePublisher

logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

parser = argparse.ArgumentParser()
parser.add_argument("-C", "--configuration-path", help="Database name",
                    default="./config.json")
parser.add_argument("--verbose", help="Run in verbose mode",
                    action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    configuration_path = args.configuration_path
    block = CommunicationBlock("demo_gui")
    #todo setSocketIo In constructor of block
    block.setSocketio(socketio)
    block.parse_json_configuration_file(configuration_path)

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    main()
    # only for testing
    v = VehicleStatePublisher("vehiclestate")
    v.parse_json_configuration_file("./testpub.json")
    print("parsed file")
    v.start()
    socketio.run(app)
