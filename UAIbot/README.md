# Example of interaction of UAIbotJS with NiryoNed:

Assuming your local Python setup already has the support for pyniryo, first run the server.py program with Python

$ python server.py

This creates a webserver available at http://localhost:8777/
Open this page in a web browser and it will load the index.html file from this folder - it will load the UAIbotJS, 
the Niryo Ned robot visualization and creates a websocket connection with the Python program, which connects to the
real robot on the Ethernet port (you can change the IP address in the code, if not using the default one, or connecting the robot over Wifi).

# Controlling the interaction from Python

User can start their Python function (user_function in server.py) by pressing the [RUN PYTHON] button from the browser,
and it will run it on the side of the Python program.

The supported API calls from your Python user function for interaction with the UAIbotJS:

sim_show_config([joint1, joint2, joint3, joint4, joint5, joint5]) - moves the simulated arm to a joint-configuration-specified location

sim_show_pos([ROLL, PITCH, YAW, X, Y, Z]) - moves the simulated arm to a world-coordinates-specified location

joint_configuration = sim_inverse_kinematics([ROLL, PITCH, YAW, X, Y, Z]) - calculates a joint configuration pose from the world-coordinates-specified location

# Controlling the interaction from JavaScript

Alternately, user can start their JavaScript function (user_function in index.html) by pressing the [RUN JS] button from the browser, and it will run it on the side of the JavaScript server.

The supported API calls from the JavaScript user function for interaction with the Niryo Ned robot:

niryo_move([joint1, joint2, joint3, joint4, joint5, joint5]) - moves the real robot arm to the specified joint configuration
open() - opens the gripper
close() - closes the gripper

# Enabling the real robot and direct control

The web interface also contains the option to specify the commands manually from the user interface, as well as turn the communication with the real robot on and off to try the code only in simulation.
