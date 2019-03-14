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
# Problems
- If you are getting segmentation faults, check that you are using the latest proto messages! (vehicle_state, can_message, ...)
- Make sure that when you are working with the gui and the canmapper, you are not mocking any data that is being sent out by the canmapper, since this might cause zero mqtt to throw an error since you are using the same address.
