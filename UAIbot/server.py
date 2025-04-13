###### before code cleanup


import asyncio
import websockets
import http.server
import socketserver
import time
import threading

from pyniryo import *
import numpy as np


robot = NiryoRobot('169.254.200.200')
robot.calibrate_auto()

# Serve HTML page
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Cache-Control", "private, no-store, no-cache, must-revalidate");
        self.send_header("Pragma", "no-cache");        
        SimpleHTTPRequestHandler.end_headers(self)

# Start HTTP server (to serve the HTML page)
PORT = 8777
httpd = socketserver.TCPServer(("localhost", PORT), CORSRequestHandler)
print(f"Serving HTML on http://localhost:{PORT}")
_future = None
wsocket = None
condition = threading.Condition()
returned_value = None

min_joint = [-2.96705972839, -2.09003177926, -1.34006379968, -2.09003177926, -1.92003671012, -2.53002928369 ]
max_joint = [2.96705972839, 0.610167106497, 1.57009819509, 2.09003177926, 1.05016461093, 2.53002928369 ]

def ramp_joints(joints):
    for i in range(6):
        if joints[i] < min_joint[i]:
            joints[i] = min_joint[i]
        if joints[i] > max_joint[i]:
            joints[i] = max_joint[i]
    return joints

# WebSocket Handler
async def websocket_handler(websocket):
    global wsocket, _future, condition, returned_value
    print("WebSocket connection established!")
    wsocket = websocket
    try:
        async for message in websocket:
            

            # Split the message into parts
            parts = message.split()
            print(f"Received from JS: {message}", parts[0]) # , _future, _future.done())

            if (message == "pos1"):
                robot.move_joints(0.2, -0.3, 0.15, 0.05, 0.55, -0.85)
            elif (message == "open"):
                robot.open_gripper()
            elif (message == "close"):
                robot.close_gripper()
            elif (parts[0] == "cfg"):
                if _future and not _future.done():
                    print(f"setting future")
                    _future.set_result(parts[1:])
                    returned_value = [float(x) for x in parts[1:]];
                    with condition:
                        condition.notify()
                
            # Check if it's a "q" command and has 6 joint values
            elif parts[0] == "q" and len(parts) == 7:
                try:
                    # Convert joint values to floats
                    joint_values = [float(parts[i]) for i in range(1, 7)]
                    
                    joint_values = ramp_joints(joint_values)
                    
                    # Move the robot with parsed values
                    robot.move_joints(*joint_values)
                    
                    await websocket.send(f"Python received: {message}")  # Echo back
                except ValueError:
                    await websocket.send("Error: Invalid joint values!")
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket closed")

def sim_show_config(config):
    if wsocket:
        print("sending...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Set the new loop for this thread
        loop.run_until_complete(wsocket.send("cfg " + " ".join(map(str, config))))

        print("sent...")

    
def sim_show_pos(position):
    if wsocket:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Set the new loop for this thread
        loop.run_until_complete(wsocket.send(f"pos " + " ".join(map(str, position))))
        
       

def sim_inverse_kinematics(position):
    global _future, condition, returned_value
    if wsocket:
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Set the new loop for this thread
        asyncio.run_coroutine_threadsafe(wsocket.send(f"inv " + " ".join(map(str, position))), loop)
        #loop.run_until_complete(wsocket.send(f"inv " + " ".join(map(str, position))))

    loop = asyncio.get_event_loop()
    _future = loop.create_future()
    print(f"waiting for future")
    with condition:
        condition.wait()
    #cfg = loop.run_until_complete(_future)
    print(f"got future")
    return returned_value


    
# This will hold the server object globally
ws_server = None
    
    
async def start_websocket_server():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        print("WebSocket server started")
        await asyncio.Future()  # Keep running
        
        
def user_function():
    
    # pos 0 1.9 0 0.3 0.3 0.2
    # pos 0 3 0 0.35 -0.15 0.2 
    
    print("hello from niryo (user thread)")
    time.sleep(15)
    sim_show_config([0, 0, 0, 0, 0, 0])
    
    time.sleep(5)
    # sim_show_pos([0, 0.5, 0, 0.4, 0.1, 0.2])
    
    # time.sleep(5)
    # inv = sim_inverse_kinematics([0, 0.5, 0, 0.4, 0.1, 0.2])
    # print("inv:", inv)
    
    start = np.array([0, 1.9, 0, 0.3, 0.3, 0.2])
    end = np.array([0, 3, 0, 0.35, -0.15, 0.2])
    
    num_steps = 100
    for i in range(num_steps + 1):
        pos = (1 - i / num_steps) * start + (i / num_steps) * end
        print(pos)
        #cfg = sim_inverse_kinematics(list(pos))
        cfg = sim_inverse_kinematics([0, 0.5, 0, 0.4, 0.1, 0.2])
        print(cfg)
        sim_show_config(cfg)
        time.sleep(1)

    print("user_function is exiting...")
        

# Run both HTTP and WebSocket server
async def main():
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, httpd.serve_forever)  # Run HTTP server in background
    await start_websocket_server()
    

# Start user_function in a thread
usr_thread = threading.Thread(target=user_function, daemon=True)
usr_thread.start()

    
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted.")
    httpd.shutdown()
    httpd.server_close()
    if ws_server:
        ws_server.close()
        time.sleep(1)
    


       
        
        
    