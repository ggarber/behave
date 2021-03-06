import cv2
import os
import sys

import classifiers
import enforcers
from utils import flip_frame, CvTimer, Capturer, say, convert_to_gray_and_equalize
import gui

#cx_freeze data hanlder
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

#INIT:
timer = CvTimer()

capturer = Capturer()
frame_width = capturer.get_cam_width()
frame_heigth = capturer.get_cam_height() 
print('capturing %sx%s' % (frame_width, frame_heigth)) 

face_enforcer = enforcers.EnforceFaceWithin(say)
#face_classifier = classifiers.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
face_classifier = classifiers.CascadeClassifier(find_data_file('cascades/haarcascade_frontalface_alt.xml'))

# mouse callback function sets red line to enforce
def set_y_limit_low(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        face_enforcer.set_enforce_parameters(y_limit_low=y) 

# Create a window and bind function(s) to window
cv2.namedWindow('behave')
cv2.setMouseCallback('behave', set_y_limit_low)

#FIXME quick and dirty counter for only processing every 5th frame.
fps_counter = 0
msg = None
debug = 'off'
#Main Loop
while(True):
    #Time tracking w opencv:
    timer.new_frame()

    fps_counter += 1

    #Capture frame-by-frame
    a_frame = capturer.get_frame()

    a_frame = flip_frame(a_frame)

    #display red line for lower limit
    #TODO: change this to a general method to show limits:
    gui.display_line(a_frame, (0, face_enforcer.y_limit_low),
                                (frame_width / 7, face_enforcer.y_limit_low), thickness=2)
    gui.display_line(a_frame, (frame_width - (frame_width / 7), face_enforcer.y_limit_low),
                                (1280, face_enforcer.y_limit_low), thickness=2)

    if fps_counter == 5:
        fps_counter = 0

        a_frame_prepared = convert_to_gray_and_equalize(a_frame)

        faces_list = face_classifier.detect_multiscale(a_frame_prepared)

        if len(faces_list) == 1:
            action_needed, msg = face_enforcer.check_face(faces_list[0])
            if action_needed:
                action_needed()

        if faces_list != () :
            #TODO: change the colour of the face rect when in warning.
            gui.display_faces(a_frame, faces_list, with_debug=debug)
    
    if msg:
        cv2.putText(a_frame, msg, (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))

    #key handler:
    to_do = gui.get_key_pressed()
    if to_do == 'quit':
        break
    #shame on me for the next lines FIXME!!!:
    elif to_do == 'debug':
        if debug == 'on':
            debug = 'off'
        elif debug == 'off':
            debug = 'on'

    if debug == 'on':
        #Timecv:
        cv2.putText(a_frame, "fps=%s avg=%s" % (timer.fps, timer.avg_fps), (10, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        #Frame counter:
        cv2.putText(a_frame, "frame=%s" % (timer.frame_num), (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

    #On-screen controls:
    cv2.putText(a_frame, "Behave!!! :)", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(a_frame, "Click with the mouse to begin", (10, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(a_frame, "Press 'd' to debug, 'q' to quit", (10, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    #Display the resulting frame
    cv2.imshow('behave', a_frame)

capturer.release()
cv2.destroyAllWindows()
