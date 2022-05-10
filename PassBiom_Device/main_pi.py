import cv2
import numpy as np
import peewee_sqlite as pee
from time import time
from smbus2 import SMBus
from mlx90614 import MLX90614
from subprocess import run
from datetime import datetime
from gpiozero import MotionSensor
from google_client import UploadToGDrive, LoadFromGDrive
from PIL import Image, ImageFont, ImageDraw 
from face_recognition import face_locations, face_encodings, compare_faces

LoadFromGDrive()

names = []
known_face_encodings = []
header_font = ImageFont.truetype("bahnschrift.ttf", 47)
subhead_font = ImageFont.truetype("bahnschrift.ttf", 20)

pir = MotionSensor(4)

bus = SMBus(1)
mlx = MLX90614(bus, address=0x5A)

# Getting faces and names from a DB
face, name, position = pee.lists_gen()
known_face_encodings+=face
names+=name
roles = pee.ListOfRoles('00000000867901b9')

def face_rec():
    time1 = time()
    temp_check = False
    
    # Load Camera
    cap = cv2.VideoCapture(0)
    width, height  = cap.get(3), cap.get(4)
    new_size = (int(width*1.6), int(height*1.6))
    
    while (time() - time1) <= 30:
        _, cv_img = cap.read()

        # Drawing a rectangle at the top
        overlay = cv_img.copy()
        cv2.rectangle(overlay, (0, 0), (int(width), int(height*0.25)), (0, 0, 0), -1)
        cv_img = cv2.addWeighted(cv_img, 0.6, overlay, 0.4, 0)
        
        # Converting cv2 array into Pillow data
        pil_img = Image.fromarray(cv_img)
        draw = ImageDraw.Draw(pil_img)

        small_frame = cv2.resize(cv_img, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find face location (example: [(1047, 3354, 1845, 2555)])
        face_location = face_locations(rgb_small_frame)
        face_location = face_location[:1]
        
        def r_d_s():
            open_cv_image = np.array(pil_img)
            date_t = datetime.now().strftime("%d.%m.%Y %H.%M.%S.%f")

            # Drawing rectangle around face 
            h, w, y, x = face_location[0], face_location[1], face_location[2], face_location[3]
            cv2.rectangle(open_cv_image, (x, y), (w, h), (250, 250, 250), 2) 
            
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            open_cv_image = cv2.resize(open_cv_image, new_size, fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            
            cv2.imshow("window", open_cv_image)
            
            return open_cv_image, date_t

        if len(face_location) != 0:
            # Getting the temperature
            temperature = round(mlx.get_object_1(),1)
                    
            # (example: [array([-9.32926461e-02,  1.26772478e-01, ...) | 1 sec./frame
            face_encoding = face_encodings(rgb_small_frame, face_location)

            # See if the face is a match for the known face(s)
            matches = compare_faces(known_face_encodings, face_encoding[0], tolerance=0.5)
            
            name = "Identity not identified!"
            if True in matches:
                first_match_index = matches.index(True)
                name = names[first_match_index]

            face_location = np.array(face_location[0]) / 0.25
            face_location = face_location.astype(int)
            
            # Text printing
            if name == "Identity not identified!":
                draw.text(((width*15)/100, (width*1.5)/100), name, (0,0,200), font=header_font)
                open_cv_image, date_t = r_d_s() 
                pee.Registration.create(user_id=0, ver='-')
                cv2.imwrite('Unrecognized_faces/{}.jpg'.format(date_t), open_cv_image)
                cv2.waitKey(2000)
                
            elif position[first_match_index] not in roles:
                draw.text(((width*18)/100, (height*1.5)/100), "Welcome, {}!".format(name),
                              (255,255,255), font=header_font)
                draw.text(((width*45)/100, (height*17)/100), "REJECTED",
                            (0,0,200), font=subhead_font)
                
                pee.Registration.create(user_id=first_match_index+1, ver='-')
                r_d_s()
            
            else:
                if temperature > 35.0 and temperature <= 37.0:
                    _, date_t = r_d_s()
                    
                    draw.text(((width*18)/100, (height*1.5)/100), "Welcome, {}!".format(name),
                              (255,255,255), font=header_font)
                    draw.text(((width*4)/100, (height*17)/100), "{}".format(date_t[:22]),
                              (255,255,255), font=subhead_font)
                    draw.text(((width*48)/100, (height*17)/100), "OK",
                              (0,200,0), font=subhead_font)
                    draw.text(((width*70)/100, (height*17)/100), "Temperature: {}".format(temperature),
                              (255,255,255), font=subhead_font)
                    
                    pee.Registration.create(user_id=first_match_index+1, temp=temperature, ver='+')
                    temp_check = True
                
                elif temperature > 37.0:
                    draw.text(((width*18)/100, (height*1.5)/100), "Welcome, {}!".format(name),
                              (255,255,255), font=header_font)
                    draw.text(((width*25)/100, (height*17)/100),
                              "The temperature is too high: {}".format(temperature),
                              (0,0,200), font=subhead_font)
                    
                    pee.Registration.create(user_id=first_match_index+1, temp=temperature, ver='-')
                    
                else:
                    draw.text(((width*18)/100, (height*1.5)/100), "Welcome, {}!".format(name),
                              (255,255,255), font=header_font)
                    draw.text(((width*30)/100, (height*17)/100), "Measure the temperature!",
                              (0,0,200), font=subhead_font)
                    
                r_d_s()
                
                if temp_check == True:
                    cv2.waitKey(5000)
                    break
        
        else:
            draw.text(((width*16)/100, (height*1.5)/100), "Come to the camera!",
                      (255,255,255), font=header_font)
            open_cv_image = np.array(pil_img)
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            open_cv_image = cv2.resize(open_cv_image, new_size, fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            cv2.imshow("window", open_cv_image)
        
        if cv2.waitKey(1) == 27: 
            cap.release()
            cv2.destroyAllWindows()
            bus.close()
            UploadToGDrive()
            quit()
            
        # Turn on screen
        run(["xset", "-display", ":0.0", "dpms", "force", "on"])
            
    cap.release()
    monitor()
    
def monitor():
    # Turn off screen
    run(["xset", "-display", ":0.0", "dpms", "force", "off"])
    
    while True:
        round(mlx.get_object_1(),1)
        pir.wait_for_motion()
        break
    
    face_rec()
monitor()