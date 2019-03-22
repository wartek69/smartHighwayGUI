# smartHighwayGUI
Web application used for visualization of of several events that can happen.
# Running
```
python3 app.py
```
If you want to deploy the server to the outside, edit the following line in app.py
```
socketio.run(app)
```
to
```
socketio.run(app, host='0.0.0.0')
```

# Mocking
Data of vehicle state and external eebl can be mocked by running. (Use the externpub.json and testpub.json)
```
python3 app.py --mock

```
# Config
You can easily change the timeouts for each message that arrives from the dust framework by editing the gui_config.ini .
All the values under the message header are in seconds. When the timeout gets exceeded the backend will notify the
frontend and the user will be notified about a timeout.
To change the duration of the icons that are shown on the map you can easily edit the application.js file.
You will see the following variables: 
```
var stopicon_timeout = 5000;
var redCar_timeout = 6000;
```
The values are in milliseconds.

# Problems
- If you are getting segmentation faults, check that you are using the latest proto messages! (vehicle_state, can_message, ...)
- Make sure that when you are working with the gui and the canmapper, you are not mocking any data that is being sent out by the canmapper, since this might cause zero mqtt to throw an error since you are using the same address.
