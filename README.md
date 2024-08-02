# robot_head_pi
making a robot head with a raspberry pi inside

__Poppy Robot Project files__ 
[Poppy Robot Head stls from the poppy opens source project](https://github.com/poppy-project/Poppy-eva-head-design) <br/>

### Parts list:

- __Servo and servo mount__ 
[Cheap Ali express servos](https://www.aliexpress.com/w/wholesale-servo-25kg.html?spm=a2g0o.productlist.search.0)  and 
[servo pan tilt](https://www.aliexpress.com/w/wholesale-servo-pan-tilt-MG995-MG996.html?spm=a2g0o.productlist.search.0) <br/>
- __Raspberry Pi 4__ <br/>
- __90 degree USB C adapter to power pi__
[90 Degree Right Angle USB-C Male to USB-C Female Adapter](https://www.amazon.com.au/dp/B0B2NJ3P3L) <br/>
- __Stereo Camera__
I used [this one](https://www.amazon.com.au/Synchronized-Stereo-USB-Camera-Industrial/dp/B07R8LQKV4) from Amazon but shop around.<br/>
- __Arducam TOF camera__ <br/>
- __breadboard__ (just broke off the side for the 5v and earth rail) <br/>
- __perf board__ <br/>
- __2 x white leds__ (but you can use any colour you like) <br/>
- __2 x 220 ohm resistors__
- __tiny cylinder magnets__ I used these ones [from Amazon](https://www.amazon.com.au/dp/B0CM3KX5BC)

### Instructions
#### Step 1:
Mound the stereo camera, the time of flight camera and the leds on the pef board. 
The LEDs are should be in series with 220 ohm resistors and connected to pins 17 and 26 on the pi. I use 220 ohms because the pi gives 3.3 volts. Also, I drilled 2.5mm holes to mount the electronics on the perf board.
![perf board](https://github.com/jonathanrandall/robot_head_pi/blob/main/images/perf_board.png)

#### Step 2:
Print the following three robot head pieces from the Poppy Robot Project files listed above. [Poppy Robot Head](https://github.com/poppy-project/Poppy-eva-head-design) <br/>
__The work for this was done by 3 students of the ENSAM Bachelor of technology at Bordeaux, France: Damien MARTY, Clément GEA and Éléa CHARPNTIER, under the supervison of Jean-Luc CHARLES and Cécile DELARUE, professors at ENSAM Bordeaux.__ I have included the STL files in this repo (in the directory STL), just incase they become unavaiable on the original repo. <br/>
1. The eva_head_frontBottom
2. The head_RPi4Support
3. The head_top-part

They also provide some connectors to attach the tft for the face, but I'm using a pef board instead of a tft, so I just used hot glue.

#### Step 3:
This is where my design differs from the original design.
Print the servo_head_connection-Body_v2.stl file. This is used to connect the head to the serov pan-tilt. I've also included the freecad file incase you want to adjust the position of the holes. It uses m2 screws.
![connector for pan tilt](https://github.com/jonathanrandall/robot_head_pi/blob/main/images/connector_for_pan_tilt.png)



