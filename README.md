# Gesture-Enabled System Interaction (GESI) 

![Wide](https://user-images.githubusercontent.com/56772433/166868257-141398ff-e997-40f7-a708-0f5f75153c0c.png)

## Introduction
This project was created as part of the Department of Computer Science, Trinity College (Hartford, CT), Senior Capstone project. I was advised by Dr. Maminur Islam both semesters. 

You will find all files: training and testing scripts, 3D STL designs, presentation and poster, and the code for the ESP-EYE live stream here.

## Abstract
Gesture Enabled System Interaction (GESI) is a project that enables users to interact effectively
with devices based on intuitive hand gestures. 

With the exception of gaming, touch and voice have dominated the way we interact with technology over the last decade. Enabling users to utilize gestures to operate and interact with appliances, speakers, lights, machines, and more
will allow us to develop more interactive and robust technology. 

The purpose of this project is to add another dimension of user interaction with various systems and technologies. To achieve
this, I am developing a wearable piece of technology using the ESP-EYE microcontroller that will be mounted to a pair of 3D-designed and printed glasses. The microcontroller will broadcast raw real-time video of a user’s hand motions (first-person view) which will be intercepted by the object-detection algorithm running remotely. 

Once a gesture is recognized by the deep-learning object detection model, an API request will be sent to Amazon’s Alexa API (referred to as “skills”) for direct device interaction. A user will be able to interact with any device connected to
their Alexa account by issuing gestures that are unique to that specific device. 

As the project progresses, ultimately, the end-product will be optimized for reliable, robust, and natural
interactions with connected technologies.

## Current Work
Looking at current day approaches to gesture-based technology, the work is split between IoT developers and some commercial products. A company named Fibaro designs smart home devices/applications and has recently developed a gesture-based technology called “Swipe”. The idea behind it is to place a tablet in a common space at home and issue gestures to control home devices and music systems. The issue with this design is the lack of movability and robustness. Users need to be in a certain place in their house and within a certain range of proximity in order to operate these devices. It is not practical for user stories that would involve being able to operate devices via gestures from multiple locations. 


Other designs include hand-tracking via accelerometers, using a Xbox Kinect as a tracker, or using a wearable watch that records gestures. These designs are bulky, lack mobility, and do not directly address the need for gesture-control to be natural and robust. There is one project, named SHAIDES by Nick Bild, a software engineer, that begins to address the issues above. He utilizes one dynamic gesture to turn on and off a light using a bulky Jetson Nano and a Raspberry Pi Camera (later switches to a microcontroller for more lightweight use). He accomplishes interfacing with one API (Phillips REST), but this is the extent that his project went to and lacks integration to a broader range of devices and user autonomy over gestures. 


Taking all of this into consideration, I aim to follow the effective design choices of previous work and avoid previous mistakes that resulted in failures. This project will focus on usability, mobility (in terms of being able to utilize it from multiple locations), and integrating a user-friendly and natural interface. I will be taking the core ideas expressed by the aforementioned researchers and IoT projects and extending it to a unique model that incorporates the most effective hardware and software choices. My design will be unique to previous approaches by allowing for users to interface with multiple devices based on defined gestures (static/dynamic), integrate a lightweight sleek wearable solution, and cover a broad range of functionality (across types of devices). 

## Significance
With the emergence of platforms such as Amazon Alexa and Google Home that allow you to connect smart devices to one platform, the relevance of this project is vast. The best way to encapsulate the significance of this project is to provide a scenario. 


Imagine you, a proud owner of this product (GESI), are coming home from work and with the gesture of your hand you can open your car garage. Right when you enter the house, you decide to turn on the lights with another gesture. Say you are feeling cold on a cold fall evening, with one gesture you can control your thermostat without the click of a button. Music? Pre-programmable gestures to access your favorite playlists and automatically play on your bluetooth speaker via Alexa. Bedtime? One gesture to power off your room lights, close your motorized curtains, and turn off your TV with a specified night mode gesture-motion. The possibilities are simply endless. This product would enable users to access another dimension of user-interaction with systems. 

## Methodology 
### Diagram of technical process
![final-diag](https://user-images.githubusercontent.com/56772433/166872247-c94d92d8-1087-4272-9854-899e629259da.png)

MediaPipe Hands is a high-fidelity hand and finger tracking solution. It employs machine learning (ML) to infer 21 3D landmarks of a hand from just a single frame. It is used here to extract the most important nodes on the palm and fingers to train the gesture-recognition algorithm and later test the unknown gestures coming from the user. 

VoiceMonkey allows you to trigger Alexa routines externally from services such as IFTTT and Home Assistant and offers dynamic text-to-speech (TTS) capabilities. Essentially, we can use Alexa without speaking. It is as simple as creating a "Monkey", creating an Alexa routine to pair the monkey with Alexa's functionality, and then triggering it from the testing script (pair gesture to command).

For more information regarding MediaPipe and VoiceMonkey:
https://google.github.io/mediapipe/solutions/hands.html

https://voicemonkey.io/

## Final Product
### Glasses
![image](https://user-images.githubusercontent.com/56772433/166872523-e2d59323-f63a-495b-a239-a1b01f4f47da.png)
![image](https://user-images.githubusercontent.com/56772433/166872605-cad3b2f9-a659-4340-b80a-7ec320c98b9f.png)

### Glasses with battery and ESP-EYE mounted
![IMG_9500 (2)](https://user-images.githubusercontent.com/56772433/166869996-23a053e5-e546-4f5e-8c97-97712a92d2fd.JPG)

### Smart Home Mode
https://user-images.githubusercontent.com/56772433/166870876-bbc511b6-0143-480e-b7a3-64f70b14b61e.mp4

https://user-images.githubusercontent.com/56772433/166870782-8f62e7c0-6f62-45b8-8c57-db330b099c72.mp4


### Presentation Mode

https://user-images.githubusercontent.com/56772433/166870836-4533b042-be06-4260-839d-aab758ede73c.mp4


### Music Mode

https://user-images.githubusercontent.com/56772433/166870812-0328952b-4d6f-45e7-8189-26ac06d0df64.mp4


## Special considerations
Learning: 
- OpenCV course (LinkedIn Learning)
- Object-detection course
- Microcontroller and Arduino course
- General IoT course
- MediaPipe
- VoiceMonkey

### Special Equipment: 
ESP Eye Microcontroller - 
https://www.amazon.com/Espressif-ESP-Eye-Camera-Digital-Microphone/dp/B07RD7BG8L/ref=sr_1_2?dchild=1&keywords=esp+eye&qid=1632897551&s=industrial&sr=1-2

Powerbank for remote power - 
https://www.amazon.com/Diymore-Battery-Shield-Raspberry-Arduino/dp/B0784FPF8J/ref=sr_1_1_sspa?crid=1J2I0V9HA8DU3&keywords=battery%2Bshield&qid=1651730229&sprefix=battery%2Bshield%2Caps%2C130&sr=8-1-spons&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzS0ZGSUc0TUozOVVDJmVuY3J5cHRlZElkPUEwNzYwMDI3MUJKRkFYWUQ4RTA0TCZlbmNyeXB0ZWRBZElkPUEwNDg2NjI2MURBSDE3WkdNVDNHQiZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU&th=1

Batteries - 
https://www.18650batterystore.com/products/samsung-25r-18650?utm_campaign=859501437&utm_source=g_c&utm_medium=cpc&utm_content=201043132925&utm_term=_&adgroupid=43081474946&gclid=Cj0KCQjwyMiTBhDKARIsAAJ-9Vuh8i86kuZqzTag_RUACIY4b1qi529o--lhSF_fRCWtJDXsPXO4cH0aAt6GEALw_wcB

CAD designed glasses for microcontroller (can use local library 3D printer for free)

Budget = ~$50

## Future Directions
- Improve gesture-recognition algorithm in different conditions
- Train on different hand sizes for more accurate predictions
- Develop a user-oriented method of pairing gestures to commands via a web or iOS application
- Expanding to different smart-home interfaces (Google Home & HomePod)
- Improve comfort of glasses and make design sleeker

### Please email alzagharakan@gmail.com with any questions, ideas, or comments.




