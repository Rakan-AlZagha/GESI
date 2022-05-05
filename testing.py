#----------------------------------------------------------------------------
# testing.py - script to test gestures and functionality using MediaPipe ML algorithm
# Created By  : Rakan AlZagha
# Created Date: Fall-Spring '22
# version = 1.0
# ---------------------------------------------------------------------------

import socket
import ssl
from threading import Event
import time
import cv2
import mediapipe as mp
import numpy as np
import csv
from urllib.request import urlopen
import requests
import re
import win32com.client

# url for live video liveStream
## input your livestream url here
url = "http://192.168.999.999"

# set buffer size
CAMERA_BUFFER_SIZE=4096

# image size
WIDTH=1280
HEIGHT=720

# which hand nodes to extract data from
handNodes=[0,4,5,9,13,17,8,12,16,20]

# level of error for prediction
errorTolerance=20

# start presentation example
app = win32com.client.Dispatch("PowerPoint.Application")
presentation = app.Presentations.Open(FileName=u'C:\\Users\\$USERNAME\\Downloads\\$NAME_OF_PRESENTATION.pptx', ReadOnly=1)

def main():
    """
    main() controls testing flow of gesture recognition and system interaction 
    by connecting to the live stream and matching user gestures to known ones
    """ 
    mp_drawing, mp_hands = mediapipeDeclaration()
    commandMode = ''
    attempt = 1

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        # before getting first frame
        preFrameTime = time.time()

        liveStream = connectToStream()

        # gesture data arrays
        knownGestures = loadKnownGestures()
        gestNames = loadKnownGesturesNames()

        # bit sequence to hold JPG data as it comes from stream (LIVE)
        bitSequence=b''

        while True:
            try:
                # begin decoding the JPGs in stream
                myHands=[]
                bitSequence+=liveStream.read(CAMERA_BUFFER_SIZE)
                jpgHead=bitSequence.find(b'\xff\xd8')
                jpgEnd=bitSequence.find(b'\xff\xd9')
                # check if non-corrupted JPG (full data)
                if isValidJPEG(jpgHead, jpgEnd):
                    jpg=bitSequence[jpgHead:jpgEnd+2]
                    bitSequence=bitSequence[jpgEnd+2:]

                    # fully formed image ready to apply Mediapipe algorithm on
                    image, handResults = imageSetup(jpg, hands)

                    # check amount of landmarks
                    if handResults.multi_hand_landmarks:
                        # set nodes onto hand
                        myHand, orientation = setLandmarks(handResults, mp_drawing, image, mp_hands)
                        # extract data
                        ## code to get left or right hand (discriminate against left or right gestures)
                        # leftOrRight = orientation.multi_handedness[0].classification[0].label
                        myHands.append(myHand)

                        # track time that passed            
                        elapsedTime = time.time() - preFrameTime
                        # check if hand data points exist
                        if myHands!=[]:
                            if attempt == 1:
                                unknownGesture=findDistances(myHands[0])
                                myGesture=matchGesture(unknownGesture,knownGestures,handNodes,gestNames,errorTolerance)
                                if elapsedTime > 4:
                                    # track time from start of when command is sent
                                    preFrameTime = time.time()
                                    if(myGesture == 'Unknown'):
                                        attempt = 1
                                        commandMode = ''
                                    else:
                                        commandMode += myGesture
                                        print('COMMAND MODE = ' + commandMode)
                                        attempt += 1
                            else:
                                unknownGesture=findDistances(myHands[0])
                                myGesture=matchGesture(unknownGesture,knownGestures,handNodes,gestNames,errorTolerance)
                                if(myGesture == 'Unknown'):
                                    print('Re-enter gesture!')
                                else:
                                    if(checkForReset(myGesture)):
                                        attempt = 1
                                        commandMode = ''
                                    cv2.putText(image,myGesture,(100,100),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,0,0),8)
                                    if elapsedTime > 4:
                                        # track time from start of when command is sent
                                        preFrameTime = time.time()
                                        # issue command to system/Alexa
                                        handleGesture(commandMode, myGesture)
                    # Flip the img horizontally for a selfie-view display.
                    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
            # error handling for live stream
            except socket.timeout as error:        
                print("Error: timeout error encountered.")
                return main()
            except OSError as error:
                print("Error: check connection to live stream.")
                return main()

def checkForReset(myGesture):
    if(myGesture == 'Stop'):
        print("Resetting system...issue new command mode in 4 seconds")
        return True
    else:
        return False

def connectToStream():
    """
    connectToStream() establishes the connection between the live stream
    and the python script, ongoing attempt until connection is established

    :return: live stream data
    """ 
    while True:
        try:
            ctx = ctxDefinition()
            liveStream = urlopen(url, context=ctx, timeout=2)
            return liveStream    
        except socket.timeout as error:
            print("Error: timeout error encountered.")
        except OSError as error:
            print("Error: check connection to live stream.")

def ctxDefinition():
    """
    ctxDefinition() sets up the context to override SSL certification
    when connecting to the live stream

    :return: ctx (structure of security connection)
    """ 
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def mediapipeDeclaration():
    """
    mediapipeDeclaration() to set up ML algorithm for hand detection

    :return: mp.solutions.drawing_utils, mp.solutions.hands (mediapipe solution tools)
    """ 
    return mp.solutions.drawing_utils, mp.solutions.hands


def loadKnownGestures():
    """
    loadKnownGestures() load gesture data in 

    :return: knownGestures
    """ 
    knownGestures = []
    with open('./aggregate_gesture_data/gesture_data.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        examples = list(reader)  

    for i in range(0, len(examples)):
        handData = [tuple(map(int, re.findall('\d+', string[1:-1]))) for string in examples[i]]
        knownGesture=findDistances(handData)
        knownGestures.append(knownGesture)
    return knownGestures

def loadKnownGesturesNames():
    """
    loadKnownGesturesNames() load gesture names in

    :return: gestNames
    """ 
    gestNames = []
    with open("./aggregate_gesture_data/gesture_names.csv", newline='') as f:
        data = list(csv.reader(f))
        for name in data[0]:
            gestNames.append(name)
    return gestNames

def handleGesture(commandMode, myGesture):
    """
    handleGesture() take recognized gesture and match to functionality

    :param jpg: JPEG image
    :return: gestNames
    """ 
    if(commandMode == 'Unknown'):
        print('Invalid command-mode, please try again.')
    if(myGesture == 'Unknown'):
        print('Invalid gesture, please try again.')

    # smart home mode
    if(commandMode == 'One'):
        print('-----------------Smart Home Mode-----------------')
        if(myGesture == 'Thumb-up'):
            url = 'https://api.voicemonkey.io/trigger?access_token=$ACCESS_TOKEN'
            process_request(url)
        if(myGesture == 'Thumb-down'):
            url = ''
            process_request(url)
        if(myGesture == 'Go'):
            url = ''
            process_request(url)
        if(myGesture == 'Rock'):
            url = ''
            process_request(url)

    # presentation mode
    if(commandMode == 'Two'):
        print('-----------------Presentation Mode-----------------')
        if(myGesture == 'Go'):
            presentation.SlideShowSettings.Run()
        if(myGesture == 'Thumb-up'):
            presentation.SlideShowWindow.View.Next()
        if(myGesture == 'Thumb-down'):
            presentation.SlideShowWindow.View.Previous()
        if(myGesture == 'Rock'):
            presentation.SlideShowWindow.View.Exit()
            app.Quit()
    
    # music mode
    if(commandMode == 'Three'):
        print('-----------------Music Mode-----------------')
        if(myGesture == 'One'):
            url = ''
            process_request(url)
        if(myGesture == 'Rock'):
            url = ''
            process_request(url)
        if(myGesture == 'Go'):
            url = ''
            process_request(url)
        if(myGesture == 'Thumb-up'):
            url = ''
            process_request(url)
        if(myGesture == 'Thumb-down'):
            url = ''
            process_request(url)

    print('Gesture issued: ' + myGesture)

def imageSetup(jpg, hands):
    """
    imageSetup() take JPG image and apply transformations and filters to display

    :param jpg: JPEG image
    :param hands: hands data
    :return: describe what it returns
    """ 
    image=cv2.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    image = cv2.rotate(image, cv2.cv2.ROTATE_90_CLOCKWISE)
    image=cv2.resize(image,(480,640))

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    handResults = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, handResults

def isValidJPEG(jpgHead, jpgEnd):
    """
    isValidJPEG() checks if JPEG is not corrupt (allowing for stream to progress)

    :param jpgHead: head of JPG file data
    :param jpgEnd: tail of JPG file data
    :return: boolean
    """ 
    if jpgHead>-1 and jpgEnd>-1:
        return True
    else:
        return False

def setLandmarks(handResults, mp_drawing, image, mp_hands):
    """
    setLandmarks() takes hand data and sets landmarks from mediapipe algorithm

    :param handResults: describe about parameter p1
    :param mp_drawing: mediapipe hand node (on open cv tab)
    :param image: openCV image
    :param mp_hands: hands from mediapipe recognition
    :return: myHand
    """ 
    for hand_landmarks in handResults.multi_hand_landmarks:
        landmarks(mp_drawing, image, hand_landmarks, mp_hands)
        myHand=[]
        for landMark in hand_landmarks.landmark:
            myHand.append((int(landMark.x*WIDTH),int(landMark.y*HEIGHT)))
    return myHand, handResults

def landmarks(mp_drawing, image, hand_landmarks, mp_hands):
    """
    landmarks() sets the nodes on recognized hand using mediapipe algorithm

    :param handResults: describe about parameter p1
    :param mp_drawing: mediapipe hand node (on open cv tab)
    :param image: openCV image
    :param mp_hands: hands from mediapipe recognition
    """ 
    mp_drawing.draw_landmarks(
        image,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 22, 200), thickness=2, circle_radius=4),
        mp_drawing.DrawingSpec(color=(200, 50, 0), thickness=2, circle_radius=4))

def findDistances(gestureDataPoints):
    """
    findDistances() takes gesture capture and calculates distances between
    hand nodes (palm and fingers)

    :param gestureDataPoints: distance between handNodes
    :return: distanceMatrix
    """ 
    distanceMatrix, lengthOfGestureDataPoints = generateDistanceMatrix(gestureDataPoints)
    palmSize=generatePalmSize(gestureDataPoints)
    distanceMatrix = populateDistanceMatrix(gestureDataPoints, lengthOfGestureDataPoints, palmSize, distanceMatrix)
    return distanceMatrix

def generateDistanceMatrix(gestureDataPoints):
    """
    generateDistanceMatrix() creates an empty numpy array given of data points

    :param gestureDataPoints: distance between handNodes
    :return: distanceMatrix, lengthOfGestureDataPoints
    """ 
    lengthOfGestureDataPoints = len(gestureDataPoints)
    distanceMatrix = np.zeros([lengthOfGestureDataPoints, lengthOfGestureDataPoints],dtype='float')
    return distanceMatrix, lengthOfGestureDataPoints

def generatePalmSize(gestureDataPoints):
    """
    generatePalmSize() calculates size of palm given node data

    :param gestureDataPoints: distance between handNodes
    :return: palmSize
    """ 
    palmSize=((gestureDataPoints[0][0]-gestureDataPoints[9][0])**2+(gestureDataPoints[0][1]-gestureDataPoints[9][1])**2)**(1./2.)
    return palmSize

def populateDistanceMatrix(gestureDataPoints, lengthOfGestureDataPoints, palmSize, distanceMatrix):
    """
    populateDistanceMatrix() matches data to matrix points from gesture hand nodes

    :param gestureDataPoints: distance between handNodes
    :param lengthOfGestureDataPoints: number of data points
    :param palmSize: computed palm size
    :param distanceMatrix: empty matrix
    :return: distanceMatrix
    """ 
    for row in range(0, lengthOfGestureDataPoints):
        for column in range(0, lengthOfGestureDataPoints):
            distanceMatrix[row][column]=(((gestureDataPoints[row][0]-gestureDataPoints[column][0])**2+(gestureDataPoints[row][1]-gestureDataPoints[column][1])**2)**(1./2.))/palmSize
    return distanceMatrix

def matchGesture(unknownGesture,knownGestures,handNodes,gestureNames,errorTolerance):
    """
    matchGesture() takes unknownGesture by user and matches it to known gestures

    :param unknownGesture: gesture from user
    :param knownGestures: gestures that were already trained
    :param handNodes: key nodes to track
    :param gestureNames: gesture names that were trained
    :param errorTolerance: to what error level algorithm should match to
    :return: gesture
    """ 
    minimumError, gestureErrors = gestureErrorCalculator(unknownGesture,knownGestures,handNodes,gestureNames)
    minIndex=0
    for i in range(0, len(gestureErrors)):
        if gestureErrors[i]<minimumError:
            minimumError=gestureErrors[i]
            minIndex=i
    gesture = gestureWithinTolerance(minimumError, errorTolerance, minIndex, gestureNames)
    return gesture

def gestureErrorCalculator(unknownGesture,knownGestures,handNodes,gestureNames):
    """
    gestureErrorCalculator() calculates errors between known and unknown user gesture
    (yet to be matched)

    :param unknownGesture: gesture from user
    :param knownGestures: gestures that were already trained
    :param handNodes: key nodes to track
    :param gestureNames: gesture names that were trained
    :return: minimumError, gestureErrors
    """ 
    gestureErrors=[]
    for i in range(0,len(gestureNames)):
        error=errorMargin(knownGestures[i],unknownGesture,handNodes)
        gestureErrors.append(error)
    minimumError=gestureErrors[0]
    return minimumError, gestureErrors

def gestureWithinTolerance(minimumError, errorTolerance, minIndex, gestureNames):
    """
    gestureWithinTolerance() checks if match is within error margin

    :param minimumError: lowest error from known gestures
    :param errorTolerance: to what error level algorithm should match to
    :param minIndex: which index (gestureName) matched to
    :param gestureNames: gesture names that were trained
    :return: gesture
    """ 
    if minimumError<errorTolerance:
        gesture=gestureNames[minIndex]
    if minimumError>=errorTolerance:
        gesture='Unknown'
    return gesture

def errorMargin(gestureMatrix, userMatrix, handNodes):
    """
    errorMargin() calculates error rate between known gesture and unknown user gesture

    :param gestureMatrix: gestures already known
    :param userMatrix: gesture data from user
    :param handNodes: key nodes to track
    :return: currError
    """ 
    currError=0
    for row in handNodes:
        for column in handNodes:
            difference = abs(gestureMatrix[row][column]-userMatrix[row][column])
            currError += difference
    return currError


def process_request(url):
    """
    process_request() makes an API call to Alexa's services/systems

    :param url: VoiceMonkey API url call
    """ 
    requests.get(url)
    
if __name__ == "__main__":
   result = main()
