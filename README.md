# cat-door-pi
Facial recognition system to locate specific cat by a door using object detection (YOLOv5) on a Raspberry Pi.

## Overview
Full range of features of this system:
- Radar component detects movement and turns on camera to run the object detection model.
- If desired cat is detected, takes a screenshot and sends it to user via Telegram along with notification message.
- Records the total amount of time the cat spent outside per day and displays this in a web application. 
- If cat enters/exits through an unmonitored entrance, user presses either the "IN" or "OUT" button on an ESP32-S2 component. This will send a message to the Pi (via MQTT) to log the cat's current location. 

### Brief demo
https://youtu.be/w6o7DTU-GE0

[![Link to demonstration video](https://img.youtube.com/vi/w6o7DTU-GE0/0.jpg)](https://www.youtube.com/watch?v=w6o7DTU-GE0)

## Components
- Raspberry Pi 4B
- Pi Camera V1.2
- Adafruit QT Py ESP32-S2 (optional component)
- RCWL-0516 (optional radar component)

## User Guide
<details><summary><strong>Training Model with Custom Dataset</strong></summary>
<br>
:arrow_right: Create Dataset in Roboflow
<ol>
  <li> Assemble a number of photographs, ideally over 1000 photographs total. Include at
  least 5% images that are background images, i.e. that do not contain any cats. </li>
  <li> Create an account on Roboflow and load the photographs to a new dataset. </li>
  <li> Label each photograph with the appropriate labels, i.e. draw boxes around the cat’s
  face specifically from chin to tips of the ears, as shown below. The label name should be specific and also 
  include no spaces, ex. fluffy_face rather than “fluffy face”.
  
  <img src="https://github.com/peschv/cat-door-pi/blob/main/images/face_parameters.png" alt="The bounding box parameters around a cat face" width="200">  
  </li>
  <li> Once the dataset is completely labeled, select “Finish Uploading”, and in the select
  “Split Images Between Test/Valid/Train” at a ratio of 70% for Test, 20% for Valid and
  10% for Train. Generate a new version (in the “Generate” tab), and add the
  preprocessing step of auto-orient as well as resize to image size of 416 x 416 (which
  is the image size used in YOLOv5s). </li>
</ol>

:arrow_right: Train Model in Google Colab
<ol>
  <li> Open the Google Colab notebook for training YOLOv5 using Roboflow:
  https://colab.research.google.com/github/roboflow-ai/yolov5-custom-training-tutorial/b
  lob/main/yolov5-custom-training.ipynb </li>
  <li> Follow the instructions in the notebook. You may choose to modify parameters like
  batch size and/or epochs to experiment with its effect on the accuracy rate. </li>
  <li> Download the best.pt file from the notebook and save it onto your Pi. </li>
</ol>

:warning: Troubleshooting

If accuracy rate during training is low, try one or several of the following steps:
<ol>
  <li> Recheck your dataset in Roboflow for accidental duplicates or incorrect labels. </li>
  <li> Add more photographs to your dataset. Be sure to include images of the cat in
  different lighting conditions, with partial facial obstructions, and images of
  similar-looking cats. </li>
</details>

<details><summary><strong>Raspberry Pi 4 (incl. peripherals)</strong></summary>
<br>
:arrow_right: Create Virtual Environment and Download YOLOv5
<ol>
  <li> Use the Raspberry Pi Imager to download the Raspberry Pi (Bullseye) 64-bit OS onto
  a micro SD card, per Raspberry Pi Documentation:
  https://www.raspberrypi.com/documentation/computers/getting-started.html </li>  
  <li> Insert the SD card into the Pi, and follow the on-screen instructions to set up your Pi.
  If prompted, download any updates. </li>
  <li> Open the Terminal application and download pip3 using the following instructions:
  https://pimylifeup.com/ubuntu-install-pip/ </li>
  <li> In the Terminal, create a new virtual environment to contain the object detection code
  by entering the following: 
  
    python3 pip3 install virtualenv [install virtual environment]
    python3 virtualenv my_env [to create a new environment]
    source my_env/bin/activate [to activate the virtual environment]
  </li>
  <li> Your virtual environment should now be activated. While the virtual environment,
  install the YOLOv5 package by following the instructions on the YOLOv5 Github
  page: https://github.com/ultralytics/yolov5 
  - Important: be sure to run the following code, which will install the required
  packages: pip3 install -r requirements.txt
  </li>
  <li> Add your best.pt file that was downloaded from the Google Colab notebook to the
  new YOLOv5 directory. </li>
  <li> In the Terminal, install the following package inside your virtual environment: pip3
  install opencv-contrib-python </li>
</ol>

:arrow_right: Camera Setup

<ol>
  <li> Plug the camera into the camera port, and test that it works by running the following
  in the Terminal: libcamera-vid -t 0 </li>
  <li> Test that the object detection model works on its own by running the following in the
  Terminal (assuming your detect.py is located inside a folder called yolov5):
  python3 yolov5/detect.py --source yolov5/data/images/bus.jpg </li>
  <li> Test that the webcam function works: python3 yolov5/detect.py --source 0
  
  - If an error occurs, try using the libcamerify wrapper: libcamerify python3
  yolov5/detect.py --source 0 </li>
  <li> Test with your own model by running the following (this example uses the libcamerify
  wrapper): libcamerify python3 yolov5/detect.py --weights yolov5/best.pt --source 0
  You should see the model identify the objects that you trained it to recognize. </li>
  <li> Set up the Pi and camera next to the door being monitored. The camera should be
  placed at an angle that allows it to view part of the interior and exterior, preferably
  with a hard line separating the two spaces.
  
  - To assist finding correct placement, try running the following in the Terminal to
  allow you to see the camera’s view: libcamera-vid -t 0 </li>
  <li> When the camera is in place, open the Terminal to take a photograph that will be the
  same dimensions as the webcam stream fed to your object detection model:
  libcamera-jpeg -o placement.jpg --width 640 --height 480 </li>
  <li> Open your photograph in a pixel viewer, such as https://pixspy.com, and locate the
  x-axis point of the vertical line that will separate the inside from the outside. 
  
  -  If the angle allows you to create a hard vertical line, the value of the x-axis
  boundary variable can be set as a single number, namely the x-axis point
  separating inside from outside. Ex. where the (x,y) point is (298,336), the x-axis point 
  separating “IN” from “OUT” would be 298.
  - If the angle cannot be drawn neatly with a single line, you may need to note
  multiple points. The code for this type of situation can be seen in Table 1 in
  the cat_detection.py row.
  </li>
</ol>

:arrow_right: Radar Setup

The radar is an optional component whose purpose is to detect movement near the Pi,
thereby triggering the Pi camera to turn on (instead of constantly leaving the camera
running).
<ol>
  <li> Solder 5 male header pins to the radar component. </li>
  <li> Using 3 sets of Dupont wires, connect the radar component to the Pi so that the
  radar VIN pin connects to a 5V pin on the Pi, radar GND pin connects to GND on the
  Pi, and radar OUT pin connects to the Pi’s GPIO17 pin on the Pi, per the following
  hookup guide:
  https://www.electromaker.io/tutorial/blog/using-a-doppler-radar-sensor-with-the-raspb
  erry-pi-12 
  You may need a total wire length of 24” to connect the components, meaning
  three 8” Female-Female Dupont wires and six 8” Male-Female Dupont wires. </li>
  <li> To improve radar sensitivity, the radar component should be placed as far as possible
  from the Pi, i.e. to have the wires fully extended. Otherwise there may be interference
  causing reduced sensitivity. </li>
  <li> Open the Terminal, and inside your virtual environment, install the GPIO Python
  library: pip3 install RPi.GPIO </li>
  <li> Test that the radar component works by creating a new Python file with the following
  code: 
  
    from gpiozero import DigitalInputDevice
    radar = DigitalInputDevice(17, pull_up=False, bounce_time=30.0)
    def detector:
      print(“Something detected”)
    while True:
      radar.when_activated = detector
  </li>
  <li> Run the code in the Terminal, and wave your hand in front of the radar. You should
  see the console print “Something detected”. </li>
</ol>

:arrow_right: Change Detect.py Code

<ol>
  <li> Locate and open the detect.py file that is in the yolov5 directory. </li>
  <li> Add the following lines of code to this file: 
  
    Below the line 47 
      from utils.torch_utils import select_device, time_sync
      from cat_detection import find_cat # Import find_cat() from cat detection file
    Above the line 112 for path, im, im0s, vid_cap, s in dataset
      x_center = 0
      y_center = 0
      start_time = time.strftime(“%H%M”)
      obj_detected = False
    Inside for c in det[:, -1].unique(): and below the line 162 s+= f”{n}
    {names[int(c)]}{‘s’ * (n > 1)}, “
      # Code that sends detection to find_cat() from cat_detection.py
      xmin = det[0][0].tolist() # Min x axis point
      ymin = det[0][1].tolist() # Min y axis point
      xmax = det[0][2].tolist() # Max x axis point
      ymax = det[0][3].tolist() # Max y axis point
      x_center = (xmin+xmax)/2 # Calculate the center point of the two x axis points
      y_center = (ymin+ymax)/2 # Calculate the center point of the two y axis points
      conf_rating = det[0][4].tolist() # Confidence rating
      label = det[0][5].tolist() # Object label
      print('Confidence: ',conf_rating) # Print confidence rating to console
      # If object detected, set obj_detected variable to True
      if label == 1:
        obj_detected = True
    After the if statement block, on line 204, if save_img: (i.e. at the same
    indentation as this if statement, but insert the following code after the if block
    ends on line 221)
      # If object is detected, call find_cat()
      if obj_detected:
        find_cat(x_center, y_center)
      time_now = time.strftime(“%H%M”) # Get current time
      time_interval = int(time_now) - int(start_time) # Calculate time passed
      print(‘start_time:’, start_time, ‘ time_now:’, time_now, ‘ interval:’,time_interval)
      # If the object is detected, or if 20 mins has passed and no object was
      detected, then shut down this detect.py script.
      if (time_interval >= 20 and obj_detected == False) or obj_detected == True:
        sys.exit(0)
  </li>
  <li> Save the file. </li>
</ol>

:arrow_right: Integration

<ol>
  <li> Download the code files for the Cat Door Monitor, and place them inside your virtual
  environment. Important: you must place the cat_detection.py file inside the yolov5
  directory (the directory containing the YOLOv5). </li>
  <li> In the Terminal, install the Paho MQTT client package: pip3 install paho-mqtt </li>
  <li> There are several files whose contents need to be modified to your use case. Locate
  and open each of the files listed in the filename column, and adjust the associated
  variable according to the explanation column in the table below: 
  <table>
     <tr>
      <th>Filename</th>
      <th>Variable</th>
      <th>Explanation</th>
    </tr>
    <tr>
      <td>cat_detection.py</td>
      <td>boundary_pixel</td>
      <td>Should be the x axis point that separates the
      “inside” from the “outside” part of the door (ex.
      everything to the left of this point is “inside”).</td>
    </tr>
    <tr>
      <td> </td>
      <td>cat_name</td>
      <td>Change to the name of the cat you are detecting.</td>
    </tr>
    <tr>
      <td> </td>
      <td>object_label</td>
      <td>Change to the name of the object label you had
      created for your dataset.</td>
    </tr>
    <tr>
      <td> </td>
      <td>inside find_cat(), line 83:
      if x_center < boundary_pixel</td>
      <td>This line determines if the cat is inside or
      outside. Modifications may be required if the
      camera is positioned at such an angle that there
      is no clear vertical line separating inside from
      outside meaning both x_center and y_center
      points are required. For example, if the bottom of
      the frame is still considered inside, and this is not
      a 90 degree angle, may need to insert code to
      outline where the boundaries lie, such as:
      <code>if (y_center > 316 and y_center < 400) and (x_center > 170 and x_center < 283):
          location = 'OUT'
        elif (y_center > 316 and y_center < 400) and (x_center >= 284 and x_center < 350):
          x_center >= boundary_pixel or y_center >= 400:
            location = 'IN'</code>
       </td>
    </tr>
    <tr>
      <td>start_scripts.sh</td>
      <td>virtual environment name</td>
      <td>If your virtual environment has a different name
      than “myyolo”, need to change all instances of
      this name to your virtual environment name.</td>
    </tr>
    <tr>
      <td> </td>
      <td>name of directory containing run_mqtt.py and 
      run_radar.py files</td>
      <td>If these two files are located in a different
      directory than /himbeer-pi/myyolo/, will need to
      change these to the correct directory names.</td>
    </tr>
    <tr>
      <td>push_repo.py</td>
      <td>full_local_path</td>
      <td>If the git directory is located in a different
      directory name, need to modify this path. Select
      View->Show Hidden to be able to see your .git
      folder.</td>
    </tr>
    <tr>
      <td> </td>
      <td>repo.git.add()</td>
      <td>Similarly, if the full path of the aggregate_data.txt
      is located in a different directory, need to modify
      this line to the correct directory path.</td>
    </tr>
    <tr>
      <td> </td>
      <td>username</td>
      <td>Insert your Github username associated with the
      Github account hosting your repository.</td>
    </tr>
    <tr>
      <td> </td>
      <td>remote</td>
      <td>Enter the full URL path of your Github repository.
      Ex. https://github.com/{username}/my-repo.git</td>
    </tr>
    <tr>
      <td>run_mqtt.py</td>
      <td>cat_name</td>
      <td>Change to the name of the cat you are detecting.</td>
    </tr>
    <tr>
      <td> </td>
      <td>object_label</td>
      <td>Change to the name of the object label you had
      created for your dataset.</td>
    </tr>
    <tr>
      <td> </td>
      <td>topic_name</td>
      <td>If different, change to the subscription topic you
      are using on the MQTT public broker.</td>
    </tr>
    <tr>
      <td>run_webapp.py</td>
      <td>html.H2 on line 106</td>
      <td>Replace ‘Sylvester’ with the name of your cat.</td>
    </tr>
  </table>
  </li>
</ol>

:warning: Troubleshooting

- If error occurs because it cannot find pip, check if pip3 is installed by
  entering: pip3 --version
  
</details>

<details><summary><strong>ESP32-S2 Device (optional)</strong></summary>
The purpose of this device is to keep the logs accurate for the web application
  even when the cat enters/exits a non-monitored door. This is done by having the
  user press either "IN" or "OUT" on the ESP32 device which sends the information to the Pi.
  
<a href="https://github.com/peschv/cat-door-pi/blob/main/images/flowchart_esp32.png" 
   target="_blank">View this flowchart</a> for an overview on the code logic.

:arrow_right: Installation
<ol>
  <li> Plug the device into a computer using a USB cable. The device should display a
  factory-set rainbow swirl sequence. </li>
  <li> Open Arduino IDE, and follow the steps in the Adafruit user guide to correctly set up
  the Arduino IDE environment, specifically in how to download the board from the
  Boards Manager: https://learn.adafruit.com/adafruit-qt-py-esp32-s2/arduino-ide-setup </li>
  <li> In the Tools tab, select “Boards:” and locate the Adafruit QT Py ESP32-S2 board and
  select it. </li>
  <li> In the Tools tab, select Manage Libraries and download PubSubClient (MQTT client
  library), WiFi, and Adafruit NeoPixel libraries. </li>
  <li> Create a new sketch and copy the supplied ESP32_Touch_MQTT.ino code.
  Important: you must change the value of the variables listed in the table below. </li>
  
  <table>
    <tr>
      <th>Variable</th>
      <th>Value</th>
    </tr>
    <tr>
      <td>ssid</td>
      <td>The name of your WiFi network.</td>
    </tr>
    <tr>
      <td>password</td>
      <td>The password of your WiFi network.</td>
    </tr>
    <tr>
      <td>mqtt_broker</td>
      <td>Name of the MQTT public broker. If using EMQX, leave this
      value as broker.emqx.io</td>
    </tr>
    <tr>
      <td>topic</td>
      <td>The name of the subscription topic used on the MQTT public
      broker. It is recommended that you create a new custom topic
      for your project, like esp32/sylvestercatdoor as this may
      prevent unwanted messages from being published to your
      topic.</td>
    </tr>
  </table>
  
  <li> With regards to the touch pins, further customization might be required. The code is
  set up with the A2 pin transmitting an “OUT” message and the SCL pin transmitting
  an “IN” message to the public broker.
  
  - The values created in setup() for the pins may be too large or small. It may be
  advisable to add a temporary print line in loop() that prints the value of the
  touch input to the Serial Monitor, such as: “Serial.println(touchRead(9))”.
  Ideally, the values of touch9_base and touch6_base should be sufficiently
  high enough that the device will not pick up false readings, and will require
  the person to touch the pin lightly. For instance, if the base value is too low,
  then the device may read the pin as having been touched when the hand is
  5cm from the pin. In contrast, if the base value is set too high, then the device
  may not pick up any touch readings.
  - If you want to change which pins to use as the touch pins, please refer to the
  Adafruit pinout guide to see the available touch pins, and obtain the GPIO
  number of your desired touch pin:
  https://learn.adafruit.com/adafruit-qt-py-esp32-s2/pinouts
  - You may wish to add alligator clips to the pins, and attach a conductive
  material like tinfoil to the other ends of the clips, to make it easier for the user
  to touch the correct pin. If the alligator clips are used to clip onto the pins, you
  may need to again adjust the value of the variables touch9_base and
  touch6_base, as they will have higher base values due to the clamp force.
  </li>
  <li> Verify and upload the sketch to the device. </li>
  <li> To test the device, open a web version of the MQTT public broker, and subscribe to
  your topic. For the EMQX broker, this can be accessed at
  http://www.emqx.io/online-mqtt-client Touch one of the QT Py ESP32-S2 pins to
  publish to your topic. The device should display a brief green light to indicate the
  motion was registered, and connectToBroker() method called. This should be
  followed by the rainbow swirl sequence to indicate successful transmission. The web
  version should now populate with either an “IN” or “OUT” message. </li>
  <li> Plug the device into an outlet using a USB-C cable, and USB charger. If using
  alligator clips, you may wish to house the device and the wires inside a box. It is
  important that the box is made of non-conductive material like wood or plastic, as it
  may otherwise interfere with the touch pins. </li>
</ol>

:warning: Troubleshooting

- This device may on occasion “freeze” where it is no longer responsive to touch and does not
display the initial green light. Unplugging the component and plugging it back in will fix this
problem.
- If the device displays the green light but not the rainbow lights, make sure that the WiFi
signal is sufficiently strong so it can reach the device, and that the WiFi channel is on a
2.4Ghz band.
</details>

<details><summary><strong>Web Application</strong></summary>
<br>
The web application is coded in Python and is sent to Github using git, from where it is
pulled by Heroku to display it in the browser.

:arrow_right: Create Web Application
<ol>
  <li> Open the Terminal on the Pi, activate your virtual environment (if not already
activated) using: source my_env/bin/activate [where my_env is the name of your
environment] </li>
  <li> Download the Plotly package using the following command: pip3 install plotly </li>
</ol>

:arrow_right: Github Setup
<ol>
  <li> Create a Github account and add a new repository for this project by following
  Github’s tutorial:
  https://docs.github.com/en/get-started/importing-your-projects-to-github/importing-so
  urce-code-to-github/adding-locally-hosted-code-to-github </li>
  <li> Create a Github access token to use in place of a password by following this guide:
  https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/cre
  ating-a-personal-access-token </li>
  <li> Set up a credential store to house your access token and allow you to push to the
  repository without being repeatedly prompted for your username and access token.
  Please see the following tutorial: https://git-scm.com/docs/git-credential-store </li>
  <li> In the push_repo.py file, make changes to the username and remote name (see
  Table in Part III: Raspberry Pi 4). </li>
  <li> Manually push the files to your Github by executing the following commands inside your
  virtual environment in the Terminal:

    cd myyolo (cd into your virtual environment directory)
    git add assets (a directory)
    git commit assets -m “Added assets”
    git commit Procfile -m “Added Procfile for Heroku”
    git commit requirements.txt -m “Added requirements for Heroku”
    git commit run_webapp.py -m “Added web app”
    git commit runtime.txt -m “Added runtime for Heroku”
    git push https://github.com/yourUsername/name-of-your-app.git (replacing
    yourUsername your Github username and name-of-your-app with your Github
    repository name) </li>
</ol>

:arrow_right: Heroku Setup
<ol>
  <li> Navigate to https://www.heroku.com/ in your browser and create a new Heroku
  account. </li>
  <li> Create a new Heroku app and connect it to your Github repository by following this
  tutorial:
  https://austinlasseter.medium.com/how-to-deploy-a-simple-plotly-dash-app-to-heroku
  -622a2216eb73
  Important: you will likely need to navigate to Heroku dashboard settings, and
  manually add the heroku/python buildpack for the deployment to work. </li>
  <li> Select ‘View’ to view your new web application. Note that if the aggregate_data.txt
  file is empty, your graph will not display any data. </li>
</ol>
</details>

<details><summary><strong>Telegram Channel</strong></summary>
<br>
:arrow_right: Channel Creation
<ol>
  <li> On the Pi, open the Terminal and download the Telegram package with the
  command: pip3 install telegram </li>
  <li> Download the Telegram application on your smartphone. Create or log into your
  Telegram account. </li>
  <li> Open Telegram on a desktop browser and log into your account:
  https://my.telegram.org </li>
  <li> Create a new channel called Cat Door, and navigate to this channel. </li>
  <li> In the browser URL, obtain the channel ID. For example, if the URL is
  https://web.telegram.org/#/im?p=2838491234_555242857729481384 then the
  channel ID number is 2838491234 </li>
  <li> Add -100 (minus one hundred) to the front of your channel ID. Using the example
  above, the complete number would be -1002838491234. This number will be
  important in the next steps. </li>
</ol>

:arrow_right: Send Channel Messages
<ol>
  <li> Per https://core.telegram.org/bots/features#botfather, create a new Telegram 
  bot by opening the Telegram app and sending the message: /newbot </li>
  <li> You will be prompted to enter a name and username for the bot, and will be given an
  access token in return, such as
  
      4388204182:NFJ93T8Nm6Jc0KI4h11x1zZ3dJ1bihV8Pl </li>
  <li> Following the Python Telegram Bot API located here
  https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-A
  PI send a new message to your channel by creating a new Python file and inserting
  the following code (replacing the italicized characters with your recently obtained
  access token and channel number):
  
      import telegram
      bot = telegram.Bot(“4388204182:NFJ93T8Nm6Jc0KI4h11x1zZ3dJ1bihV8Pl”)
      bot.send_message(text=“Cat is inside”, chat_id=“-1002838491234”) </li>
  <li> You should now see the message pop up in your Telegram channel. Note: you may
  need to add your bot as an administrator on your channel. </li>
  <li> Create a new Python file called credentials.py and place it inside the yolov5 directory.
  Add the following code, replacing the italics with your actual complete channel ID
  number identified in step 5 above:
  
      TELEGRAM_CHAT = “-1002838491234”
      TELEGRAM_BOT = “4388204182:NFJ93T8Nm6Jc0KI4h11x1zZ3dJ1bihV8Pl” </li>
  <li> Ensure that the credentials.py file is in the same directory as cat_detection.py. </li>
  <li> Optional: in your Telegram channel settings, you may also choose to auto-delete
  messages for your channel after a set period of time to avoid clogging up the
  channel. </li>
</ol>

:warning: Troubleshooting
- If the Telegram test message fails, investigate if the access token and channel ID number
were typed correctly. It may be helpful to copy and paste these numbers into another
application and change the font, as some letters can look similar (such as l vs I).
</details>

<details><summary><strong>Automation</strong></summary>
<ol>
  <li> Open the Terminal and enter the following command: crontab -e </li>
  <li> In the file opened by the above command, add the following entries at the end to
  automate the start and end of the necessary scripts:
  
      # At 9:30am, start running MQTT and radar code
      30 9 * * * /bin/bash /home/himbeer-pi/myyolo/start_scripts.sh
      # At 11:15pm, stop running MQTT and radar code
      15 23 * * * /bin/bash /home/himbeer-pi/myyolo/stop_scripts.sh
      # At 11:30pm, push log to repo
      30 23 * * * /bin/python3 /home/himbeer-pi/myyolo/push_repo.py </li>
      
  <li> You can also change the times depending on the time of day when you might expect
  your cat to enter and exit the home. For example, to set up start_scripts.sh to run at
  7:15am, change the line to:
  
      15 7 * * * /bin/bash /home/himbeer-pi/myyolo/start_scripts.sh </li>
</ol>

</details>

## Results
Training results revealed a 98% accuracy rate. During implementation, the accuracy dropped to 91.3% (where the system correctly identified the cat in 42 of 46 instances). 

<img src="https://github.com/peschv/cat-door-pi/blob/main/images/results_1.png" 
  alt="Collection of results showing successful cat facial recognition" width="500">  
<img src="https://github.com/peschv/cat-door-pi/blob/main/images/results_2.png" 
  alt="Collection of results showing successful cat facial recognition" width="500">    
<img src="https://github.com/peschv/cat-door-pi/blob/main/images/results_3.png" 
  alt="Collection of results showing successful cat facial recognition" width="500">  
    
