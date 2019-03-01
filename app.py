
from flask import Flask, render_template
import logging
from CommunicationBlock import CommunicationBlock
from __version__ import VERSION
from flask_socketio import SocketIO
import argparse
from ExternEeblPublisher import ExternEeblPublisher
from packaging import version
import sys

from VehicleStatePublisher import VehicleStatePublisher

logger = logging.getLogger(__name__)
if version.parse(VERSION) < version.parse("1.0.0"):
    logger.error("Project outdated, update version!")
    sys.exit(-1)

app = Flask(__name__)
socketio = SocketIO(app)

parser = argparse.ArgumentParser()
parser.add_argument("-C", "--configuration-path", help="Database name",
                    default="./config.json")
parser.add_argument("--verbose", help="Run in verbose mode",
                    action="store_true")
parser.add_argument("--mock", help="mock data of external eebl and vehicle state",
                    action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    configuration_path = args.configuration_path
    block = CommunicationBlock("demo_gui", socketio)

    block.parse_json_configuration_file(configuration_path)

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    main()
    if(args.mock) :
        # only for testing
        v = VehicleStatePublisher("vehiclestate")
        v.parse_json_configuration_file("./testpub.json")
        v.start()
        e = ExternEeblPublisher("eebl_publisher")
        e.parse_json_configuration_file("./externpub.json")
        e.start()
    socketio.run(app)
