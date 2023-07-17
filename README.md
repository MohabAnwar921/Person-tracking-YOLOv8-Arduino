# Person-tracking-YOLOv8-Arduino
In this project openCV and YOLOv8 are used to detect persons on the frame and send thier coordinates to the Arduino over Serial 
The arduino moves the X and Y servos to track the person
The selected person to track is bound by a Red bounding box and other people are bound by green boxes
to select a different person to track you press > or < 
remember to change the COM port for your arduino board in main.py
