import smtplib
import RPi.GPIO as GPIO
import time
import cv2
from gpiozero import MotionSensor, LED, Buzzer
#from picamera import PiCamera
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


#def make_1080p():
#    cap.set(3, 1920)
#    cap.set(4, 1080)

pir = MotionSensor(21)
led = LED(20)
#camera = PiCamera()
camera = cv2.VideoCapture(0)
cv2.namedWindow("test", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#def change_res(width, height):
#    camera.set(3, width)
#    camera.set(4, height)

#change_res(1920,1080)



GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Email Variables
SMTP_SERVER = 'smtp.gmail.com'  # Email Server (don't change!)
SMTP_PORT = 587  # Server Port (don't change!)
GMAIL_USERNAME = 'XXXXXXXXXXXXXXX@gmail.com'  # change this to match your gmail account
# change this to match your gmail password
GMAIL_PASSWORD = 'XXXXXXXXXXXXXXX'

#Set GPIO pins to use BCM pin numbers
GPIO.setmode(GPIO.BCM)

#Set digital pin 21(BCM) to an input and enable the pullup
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Event to detect button press
GPIO.add_event_detect(21, GPIO.FALLING)


class Emailer:
    def sendmail(self, recipient, subject, content, image):

        #Create Headers
        emailData = MIMEMultipart()
        emailData['Subject'] = subject
        emailData['To'] = recipient
        emailData['From'] = "info@liibex.lv"

        #Attach our text data
        emailData.attach(MIMEText(content))

        #Create our Image Data from the defined image
        imageData = MIMEImage(open(image, 'rb').read(), 'jpg')
        imageData.add_header('Content-Disposition',
                             'attachment; filename="image.jpg"')
        emailData.attach(imageData)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, emailData.as_string())
        session.quit


sender = Emailer()

while(True):
    ret, frame = camera.read()
    if not ret:
        print("failed to grab frame")
        break
    print("show camera")
    cv2.imshow("test", frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
    if GPIO.event_detected(21) or (GPIO.input(10) == GPIO.HIGH):
        
        image = '/home/pi/Desktop/image.jpg'
        cv2.imwrite(image, frame)
        sendTo = 'XXXXXXXXXXXXXXX@gmail.com'
        emailSubject = "Someone is at your door!"
        emailContent = "Movement has been detected at your door at: " + time.ctime()
        sender.sendmail(sendTo, emailSubject, emailContent, image)
        print("Email Sent")

    time.sleep(0.1)

# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()
