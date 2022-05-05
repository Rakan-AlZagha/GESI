#----------------------------------------------------------------------------
# training.py - script to train gestures using MediaPipe ML algorithm
# Created By  : Rakan AlZagha
# Created Date: Fall-Spring '22
# version = 1.0
# ---------------------------------------------------------------------------

import socket
import ssl
from unicodedata import name
import cv2
import mediapipe as mp
import numpy as np
import csv
from urllib.request import urlopen

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
errorTolerance=10

def main():
    """
    main() controls training flow of gesture data collection 
    by connecting to the live stream and aggregating gesture data into a CSV
    """ 
    mp_drawing, mp_hands = mediapipeDeclaration()

    # set up mediapipe model params
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        # gesture data arrays
        trainGestureCount=0
        knownGestures=[]
        finalHandsData = []

        # ask user for gesture data input
        gestureNames, numGest = getTrainingData()

        liveStream = connectToStream()

        # bit sequence to hold JPG data as it comes from stream (LIVE)
        bitSequence=b''

        # while training is active
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
                        myHand = setLandmarks(handResults, mp_drawing, image, mp_hands)
                        # extract data
                        myHands.append(myHand)
                        # check if hand data points exist
                        if myHands!=[]:
                            print('Show gesture by the name of ',gestureNames[trainGestureCount],': Press R to record gesture (hold still)!')
                            if cv2.waitKey(1) & 0xff==ord('r'):
                                # record data and save to CSV
                                finalHandsData, knownGestures = addTrainingData(myHands, finalHandsData, myHand, knownGestures)
                                trainGestureCount=trainGestureCount+1
                                if trainGestureCount==numGest:
                                    saveToCSV(finalHandsData, gestureNames)
                                    print("\nTraining has been completed. Please check CSV to ensure gestures were recorded.\n\nGoodbye!")
                                    break
                    # flip image for non-mirrored effect
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

def getTrainingData():
    """
    getTrainingData() guides user through training process

    :return: gestureNames, gestCount
    """ 
    welcomeMessage()
    gestCount=int(input())
    gestureNames=[]
    for gestureNum in range(1, gestCount+1):
        nameGestureX='What would you like to name gesture #'+ str(gestureNum) +'\n'
        gestureName=input(nameGestureX)
        gestureNames.append(gestureName)
    return gestureNames, gestCount

def welcomeMessage():
    """
    welcomeMessage() displays welcome message
    """ 
    print('Hello!\nWelcome to GESI (GESTURE ENABLED SYSTEM INTERACTION)...')
    print('How many gestures would you like to train on?\n')

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
    return myHand

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

def addTrainingData(myHands, finalHandsData, myHand, knownGestures):
    """
    addTrainingData() takes final hand data and adds it to final gestures

    :param myHands: contains current gesture being added
    :param finalHandsData: array of gesture data
    :param myHand: hand data from gesture
    :param knownGestures: gestures that have been labeled and recognized
    :return: finalHandsData, knownGestures
    """ 
    knownGesture=findDistances(myHands[0])
    finalHandsData.append(myHand)
    knownGestures.append(knownGesture)
    return finalHandsData, knownGestures

def saveToCSV(finalHandsData, gestureNames):
    """
    saveToCSV() saves hand data and gesture names to CSV

    :param finalHandsData: describe about parameter p1
    :param gestureNames: name of gesture training data
    :return: describe what it returns
    """ 
    example = list(finalHandsData)
    with open('./aggregate_gesture_data/gesture_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(example)
    with open("./aggregate_gesture_data/gesture_names.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows([gestureNames])

if __name__ == "__main__":
   result = main()