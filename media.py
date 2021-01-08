# coding=gbk
import numpy as np

import cv2  

cap = cv2.VideoCapture('C:/Users/dell/Desktop/����/������ʵ����/DAVIS_dataset/tracking_J=0.avi')  
cap.set(cv2.CAP_PROP_POS_FRAMES,100)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES,100)
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()