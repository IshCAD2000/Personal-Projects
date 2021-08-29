# Code Created by: Ish Kadakia
# Analyses camera information of the hand frame-by-frame to send an 
#   information string over to an Arduino.   
#   

import cv2
import mediapipe as mp
import time
import serial
from math import sqrt

# define averaging accuracy (acc > 1 for now)
acc = 1

# set up comms to the arduino
arduino = serial.Serial('COM3', 9600)

# Setup the camera paramters
wCam, hCam = 648, 488
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# create the hand tracking code
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands()

# for now, creating the time
start = time.time()
t = []

# define all arrays for this code
x0 =[]   # xposition
y0 =[]   # yposition


def norm(num, mx, mn):

    # This function normalizes any number given the mx and mnimum

    return (num - mn) / (mx - mn) 

def speed0(pos, t):

    ans = round( norm( ( pos[i]-pos[i-acc] ) / ( t[i]-t[i-acc] ), 1700, 0), 2)
    return ans 

def put_bounds(val, mn, mx):

    if( (mn<val) & (val<mx) ):
        if val<0:
            return "1"+str(-val)
        else:
            return "0"+str(val)
    elif val>mx :
        return "0"+str(mx)
    elif val<mn :
        return "1"+str(-mn)
    return "00"

def ratio(p1, p2, p0):

    # 1) to make sure we don't get any divide b zero errors
    if ( (p1[0] == 0) | (p2[0] == 0) | (p1[1] == 0) | (p2[1] == 0) ) :
        return 0

    mag12 = sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)
    mag20 = sqrt((p2[0]-p0[0])**2+(p2[1]-p0[1])**2)

    
    return int( (mag12/mag20)* 100)

# counter
i=0
# let's begin shall we?
while True:

    # defines the frames for analysis and picture
    success , img = cap.read()
    imgflip = cv2.flip(img, 1)  # do all drawings on imgflip
    imgRGB = cv2.cvtColor(imgflip, cv2.COLOR_BGR2RGB)
    results_hand = hands.process(imgRGB)
    h, w, c = img.shape
 
    if results_hand.multi_hand_landmarks:

        for handLms in results_hand.multi_hand_landmarks: 

            # add to time
            t.append(time.time()-start)

            # data for position 0's calculations
            xyz0 = handLms.landmark[0]
            xyz0 = [xyz0.x, xyz0.y, xyz0.z]
            x0.append(int((xyz0[0])*w))
            y0.append(int((xyz0[1])*h))

            # data for pos4 ( Thumb Tip )
            xyz4 = handLms.landmark[4]
            xyz4 = [xyz4.x, xyz4.y, xyz4.z]

            # data for pos 5 ( Tip of Palm for Digit 1 )
            xyz5 = handLms.landmark[5]
            xyz5 = [xyz5.x, xyz5.y, xyz5.z]

            # # data for pos 8 ( Index Finger Tip )
            xyz8 = handLms.landmark[8]
            xyz8 = [xyz8.x, xyz8.y, xyz8.z]

            # # Uncomment to see reference dots on the image.
            # mpDraw.draw_landmarks(imgflip, handLms)
    else:
        t.append(time.time()-start)

        # just making everything zero//flushing values out
        x0.append(0)
        y0.append(0)
        xyz0 = xyz4 = xyz5 = xyz8 =  [0, 0, 0]

    # Processing the data from the list
    if (i==acc) :
        
        # x0, y0 Speed Calculations
        vx0 = put_bounds(int(speed0(x0, t)*25), -9, 9)
        vy0 = put_bounds(int(speed0(y0, t)*25), -9, 9)

        # flush arrays.
        x0  = []
        y0  = []
        t   = []
        i   = 0

        # Anaylse tip of Index and Thumb fow Forward/Backward movement
        # forward
        forw_c = (ratio(xyz8, xyz5, xyz0) > 70)
        back_c = (ratio(xyz4, xyz5, xyz0) > 60)
        if forw_c  :
            forw = "1"
        else:
            forw = "0"

        # backward
        if back_c :
            back = "1"
        else:
            back = "0"

        # making sure that forw and back are not activated at the same time
        if (forw_c=='1'):
            back = '0'   # prioritise forward

        # Send the full info string to the Arduino
        send = vx0  + vy0 + forw + back  +"\n"   # "\n" to indicate EOS  
        # Send the all data to the arduino, encoded in bytes
        arduino.write(send.encode())

    else:
        i+=1

    # #Uncomment to see yourself 
    # cv2.imshow("Image", imgflip)
    # cv2.waitKey(1)

# and that's it!
