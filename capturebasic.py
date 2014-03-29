import numpy as np
import cv2
import time
import subprocess
import time
import sys

#sys.setcheckinterval(0)

def launch():
    time_start = time.time()
    #INIT:
    COUNTER = 20
    counter = 0
    counter_ok = 0
    #Recognition:
    capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt.xml')
    scale_factor = 1.3
    min_neigh = 4
    flags = cv2.CASCADE_SCALE_IMAGE
    minSize = (200, 200)
    maxSize = None # (300, 300)
    #time init:
    fps_histo = []
    f = cv2.getTickFrequency()
    t = ms = tms = fr = 1

    def say():
        subprocess.call('say -v Victoria "I think your back is not straight, Mister."&', shell=True)

    while(True):
        #Time tracking:
        time_frame_starts = time.time()
        #opencv now:
        cvtime_frame_starts = cv2.getTickCount()

        #Capture frame-by-frame
        ret, frame = capture.read()

        if not ret:
            print 'frame skipped'
            continue

        #flips horizontally:
        #frame = np.fliplr(frame) # check which is faster:
        frame = cv2.flip(frame, 1)

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = face_cascade.detectMultiScale(gray, scale_factor, min_neigh,minSize=minSize, maxSize=maxSize, flags=flags)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            #displays coords on screen
            cv2.putText(frame, "pos(x, y)=(%s,%s)" % (x, y), (x + w + 10, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(frame, "size(w x h)=(%sx%s)" % (w, h), (x + w + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

        # FACE POSITION CONTROL:
        #assuming one face:
        if len(faces) == 1:
            face_rect = faces[0]
            # the face in my desk should be around x: 400-600 y: 60-150
            x, y, w, h = face_rect
            #>LOG>print 'face is positioned at x=%s y=%s' % (x, y)
            if x < 350 or x > 650 or y > 150:
                counter += 1
                print 'warning... :>'
        
                if counter == COUNTER:
                    print 'You are doing something wrong!!!'
                    say()
                    counter = 0
            elif counter > 0:
                counter_ok += 1
        
        if counter_ok == 10:
            print 'counter_ok is RESET'
            counter_ok = 0
            counter = 0

        #key handler:
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q') or k == 27:
            break

        #Time:
        time_frame_ends = time.time()
        time_frame = time_frame_ends - time_frame_starts
        fps = 1.0 / time_frame  
        cv2.putText(frame, "fps = %s" % (fps), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
        #cv
        fr += 1
        cvtime_frame = cv2.getTickCount() - cvtime_frame_starts
        fps = f / cvtime_frame
        fps_histo.append(fps)
        fps_avg = float(sum(fps_histo)) / len(fps_histo)
        cv2.putText(frame, "frame=%s, fps=%s, avg=%s" % (fr, fps, fps_avg), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

        #Display the resulting frame
        cv2.imshow('frame', frame)
        
        if time.time() - time_start >= 20:
            break

    capture.release()
    cv2.destroyAllWindows()

launch()
