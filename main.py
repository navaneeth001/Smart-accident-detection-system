import serial
import time
import requests
import RPi.GPIO as GPIO
import cv2
import os
import RPLCD as LCD

GPIO.setwarnings(False)
display = LCD.CharLCD(numbering_mode = GPIO.BCM, cols = 16, rows = 2, pin_rs = 26, pin_e = 19, pins_data = [13,6,5,24])

cur_time = time.time()
pre_time = cur_time

Port = '/dev/ttyS0'

GPIO.setmode(GPIO.BCM)

GPIO.setup(23,GPIO.IN)
GPIO.setup(18,GPIO.OUT)
    

    

def Send_Msg(msg):
     global display 

     url = "https://www.fast2sms.com/dev/bulk"
     payload = "sender_id=FSTSMS&message={}&language=english&route=p&numbers=9497553163".format(msg) 
     headers = {
                 'authorization': "fJkEanDThd9zhb7iHF18mP7FMpMjetcR0Z87Wa5qISGVmaO5D1sNoZp55TuX",
                 'Content-Type' : "application/x-www-form-urlencoded",
                 'Cache-Control': "no-cache",
               }
              
     response = requests.request("POST", url, data=payload, headers=headers)

     display.write_string(response.text)
    
def Capture(cur_time, pre_time):
     global display

	 Camera 1 = 0
	 Camera 2 = 1
	 
	 x = 1
	 
	 frame1 = cv2.VideoCapture(Camera1)
	 frame2 = cv2.VideoCapture(Camera2)
	 
	 if frame1.isOpened() and frame2.isOpened():
	     pass

     else:
         frame1.open()
         frame2.open()
       
     frame1.set(3,640)
     frame1.set(4,480)
    
     frame2.set(3,640)
     frame2.set(4,480)
    
     path = '/home/pi/Desktop/CameraCapture/Capture({})'.format(time.ctime(time.time()))
     os.mkdir(path)

	 while x <= 10:
	     cur_time = time.time()

         Capture1, Image1 = frame1.read()
         Capture2, Image2 = frame2.read()
          
         if cur_time - pre_time >= 1:   
             display.clear()
             display.write_string("\n\tSaving Image")
                
             cv2.imwrite('{}/Camera1({}).png'.format(path,time.ctime(cur_time)),Image1)
             cv2.imwrite('{}/Camera2({}).png'.format(path,time.ctime(cur_time)),Image2)
                
             display.write_string('\t{}'.format(time.ctime(cur_time)))
                
             pre_time = cur_time
             x = x + 1
                
     frame1.release()
     frame2.release()


    

count = 0

while True:
  
     if GPIO.input(23) == 1:
         display.clear()
         count = count + 1
      
         if count % 2 != 0:
             GPIO.output(18,1)
         
             run = 0
             race = 0
         
             while run == 0:
         
                 GPS_data = serial.Serial(Port, 9600)
                 GPS_info = GPS_data.readline()
       
                 if (GPS_info.find('$GPRMC')) >= 0:
                     GPRMC_data = str(GPS_info).split('$GPRMC,',1)
                     GPRMC_info = str(GPRMC_data).split(',')
                     Locate_latt = GPRMC_info[3]
                     Locate_long = GPRMC_info[5]
      
                     if str(GPRMC_info).find('A') and Locate_latt != '' and Locate_long != '':
                         display.write_string("Location Set")

                         msg = ' Emergency Message : Latitude = {}, Longitude = {} '.format(Locate_latt,Locate_long)
                       
                         display.clear()
                         display.write_string(msg)
               
                         Send_Msg(msg)
                         Capture(cur_time,pre_time)
              
                         display.clear()
                         display.write_string('\n\tImages saved...')
                     
                         run = 1
                     
                         GPIO.output(18,0)
               
                     else:
                         time.sleep(1)

                         display.clear()
		                 display.write_string(' Checking...')
		     
		                 Capture(cur_time, pre_time)
		                 
						 if race == 0:
						     msg = ' Emergency Message : Latitude = 0.00, Longitude = 0.00 '
					
							 Send_Msg(msg)
							 
							 race = 1
							 
				 else:
				     time.sleep(1)
			
					 display.clear()
					 display.write_string(' Checking...') 
					 
					 Capture(cur_time, pre_time)
					 
                     if race == 0:
					     msg = ' Emergency Message : Latitude = 0.00, Longitude = 0.00 '

						 Send_Msg(msg)
						 Capture(cur_time,pre_time)
						 
						 race = 1

         
                         time.sleep(3)
                         display.clear()