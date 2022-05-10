from sys import argv, exit
from os import path, walk, remove, rename

import cv2
import peewee as pee 
from glob import glob
from PyQt6 import QtCore, QtGui, QtWidgets
from numpy import ndarray, uint8, frombuffer
from tkinter import messagebox, filedialog, Tk
from face_recognition import face_locations, face_encodings

from Pass_Biom import Ui_Pass_Biom
from google_client import UploadToGDrive

# Creating main app
app = QtWidgets.QApplication(argv)
Pass_Biom = QtWidgets.QMainWindow()
ui = Ui_Pass_Biom()
ui.setupUi(Pass_Biom)

# Connecting to the DB
db = pee.SqliteDatabase('Face_rec_data.sqlite')

class BaseModel(pee.Model):

    class Meta:
        database = db

# Connecting to the spreadsheets
class Users_data(BaseModel):

    user_id = pee.AutoField(column_name='User ID')
    pos = pee.TextField(column_name='Position')
    doc_id = pee.CharField(column_name='Document ID', unique=True)
    l_n = pee.TextField(column_name='Last name')
    f_n = pee.TextField(column_name='First name')
    m_n = pee.TextField(column_name='Middle name', null=True)
    face = pee.BlobField(column_name='Face coding')

    class Meta:

        table_name = 'Users data'

# db.create_tables([Users_data, Registration])

def res_img(cv_image):
    height, width = cv_image.shape[0], cv_image.shape[1]

    if width > height:
        MAX_WIDTH = 175
        MAX_HEIGHT = (MAX_WIDTH * height) // width
    elif width < height:
        MAX_HEIGHT = 175
        MAX_WIDTH = (MAX_HEIGHT * width) // height
    else:
        MAX_WIDTH = MAX_HEIGHT = 175
    
    return MAX_WIDTH, MAX_HEIGHT

def img_pros(im_path):
    img = open(im_path, "rb")
    chunk_arr = frombuffer(img.read(), dtype=uint8)
    img = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)
    small_img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    face_loc = face_locations(small_img)
    return img, small_img, face_loc

def insert_def_img():
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("Icons\\Add_image.png"),
                    QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    ui.image_Button.setIcon(icon)
    ui.image_Button.setIconSize(QtCore.QSize(175, 175))
    ui.image_Button.setObjectName('image_Button')

# Inserting data into window cells
def inserting_data():
    if ui.comboBox_addEdit.currentIndex() == 0:
        ui.lineEdit_lname.clear()
        ui.lineEdit_fname.clear()
        ui.lineEdit_patronymic.clear()
        ui.lineEdit_passport.clear()
        ui.lineEdit_post.clear()

        insert_def_img()
        
    else:
        global output_doc_id
        persone_index = ui.comboBox_addEdit.currentText().split(' ')
        persone_data = Users_data.get(Users_data.user_id == int(persone_index[0]))
        
        ui.lineEdit_lname.setText(persone_data.l_n)
        ui.lineEdit_fname.setText(persone_data.f_n)
        ui.lineEdit_patronymic.setText(persone_data.m_n)
        ui.lineEdit_passport.setText(persone_data.doc_id)
        ui.lineEdit_post.setText(persone_data.pos)
        output_doc_id = ui.lineEdit_passport.text()
        
        # Output the thumbnail to the image_Button if the cell is not empty
        images_path = glob(path.join('Persons\\', "*.*"))
        filenames = next(walk('Persons\\'), (None, None, []))[2]  # [] if no file
        
        name_index = filenames.index(f'{persone_data.doc_id}.jpg')
        name_path = images_path[name_index]
        preview, _, _ = img_pros(name_path)
        MAX_WIDTH, MAX_HEIGHT = res_img(preview)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(f'Persons\\{persone_data.doc_id}.jpg'))
        ui.image_Button.setIcon(icon1)
        ui.image_Button.setIconSize(QtCore.QSize(MAX_WIDTH, MAX_HEIGHT))
        ui.image_Button.setObjectName(path.splitext(filenames[name_index])[0])

# Dynamic generation of the list of persons
def gen_in_combo():
    count = ui.comboBox_addEdit.count()

    if count > 1:
        ui.comboBox_addEdit.setCurrentIndex(0)
        for a in range(1, count):
            ui.comboBox_addEdit.removeItem(1)
        count = 1

    if count == 1 and (Users_data.select().count() != 0):
        for item in Users_data.select():
            ui.comboBox_addEdit.insertItem(item.user_id, 
                    f"{item.user_id} {item.doc_id} {item.l_n} {item.f_n} {item.m_n}")        
    inserting_data()

gen_in_combo()

def open_image():
    global img_path, MAX_WIDTH, MAX_HEIGHT
    
    # Image selection function
    Tk().withdraw()
    img_path = filedialog.askopenfilename(
        filetypes=(("JPEG image", "*.jpeg;*.jpg"),
                        ("PNG image", "*.png")))
    
    if img_path != '': 
        image, _, face_loc = img_pros(img_path)
        
        # Get base name of file
        basename = path.basename(img_path)
        file_name = path.splitext(basename)[0]

        if face_loc == []:
            Tk().withdraw()
            messagebox.showwarning("Увага!", "Обличчя не виявлено!")
            open_image()
            
        MAX_WIDTH, MAX_HEIGHT = res_img(image)
        
        # Set image into image_Button
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(img_path))
        ui.image_Button.setIcon(icon1)
        ui.image_Button.setIconSize(QtCore.QSize(MAX_WIDTH, MAX_HEIGHT))
        ui.image_Button.setObjectName(file_name)

# Remove data from a table
def delete():
    if ui.comboBox_addEdit.currentIndex() != 0:
        persone_index = ui.comboBox_addEdit.currentText().split(' ')
        Users_data.delete().where(Users_data.user_id == int(persone_index[0])).execute()
        remove(f'Persons\\{ui.lineEdit_passport.text()}.jpg')
        gen_in_combo()

# Batch adding people to the list
def batch_list():
    # Get image captions
    filenames = next(walk('Batch_adding\\'), (None, None, []))[2]  # [] if no file
    
    ui.listWidget.clear()

    for b, filename in enumerate(filenames):
        # Remove image extension
        name = path.splitext(filename)[0]
        split_string = name.split(' ')
        id_exist = False

        for item in Users_data.select().where(Users_data.doc_id):
            if len(split_string) == 5 and item.doc_id == split_string[1].upper(): 
                id_exist = True
                break

        if len(name.split(' ')) == 5 and id_exist == False:
            item = QtWidgets.QListWidgetItem()
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap("Icons\\Tick.png"), 
                            QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            item.setIcon(icon1)
            ui.listWidget.setIconSize(QtCore.QSize(13, 13))
            ui.listWidget.addItem(item)
            text_item = ui.listWidget.item(b)
            text_item.setText(name)
    
        else:
            item = QtWidgets.QListWidgetItem()
            icon2 = QtGui.QIcon()
            icon2.addPixmap(QtGui.QPixmap("Icons\\Cross.png"), 
                            QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            item.setIcon(icon2)
            ui.listWidget.setIconSize(QtCore.QSize(13, 13))
            ui.listWidget.addItem(item)
            text_item = ui.listWidget.item(b)
            text_item.setText(name)

def batch_adding():
    # Get paths to images
    images_path = glob(path.join('Batch_adding\\', "*.*"))
    filenames = next(walk('Batch_adding\\'), 
                            (None, None, []))[2]  # [] - if no file
    
    for b, filename in enumerate(filenames):
        name = path.splitext(filename)[0]
        split_string = name.split(' ')
        id_exist = False

        image, small_frame, face_loc = img_pros(images_path[b])

        for item in Users_data.select().where(Users_data.doc_id):
            if len(split_string) == 5 and item.doc_id == split_string[1].upper(): 
                id_exist = True
                break

        if len(split_string) == 5 and id_exist == False and face_loc != []:
            split_string[0] = split_string[0].split('_')
            split_string[0] = ' '.join(split_string[0])
            
            face_enc = face_encodings(small_frame, face_loc)
            face_enc = ndarray.tobytes(face_enc[0])

            # Creating a new record
            Users_data.create(pos=split_string[0].lower().capitalize(), 
                                doc_id=split_string[1].upper(),
                                l_n=split_string[2], f_n=split_string[3], 
                                m_n=split_string[4], face=face_enc)

            cv2.imwrite(f'Persons\\{split_string[1]}.jpg', image)
    
    gen_in_combo()
    ui.listWidget.clear()
    Tk().withdraw()
    messagebox.showinfo("Готово!", "Пакетне додавання здійснено!")

def save_data():
    id_exist = False
    filenames = next(walk('Persons\\'), (None, None, []))[2]  # [] if no file
    
    # Read values ​​from all lineEdit cells
    data = []
    data.append((ui.comboBox_addEdit.currentText().split(' '))[0])
    data.append(ui.lineEdit_lname.text())
    data.append(ui.lineEdit_fname.text())
    data.append(ui.lineEdit_patronymic.text())
    data.append(ui.lineEdit_passport.text())
    data.append(ui.lineEdit_post.text())
    data.append(ui.listWidget.count())
    data.append(ui.image_Button.objectName())

    for item in Users_data.select().where(Users_data.user_id):
        if item.doc_id == data[4]: 
            id_exist = True
    
    if data[6] > 0:
        batch_adding()

    elif data[1]=="" or data[2]=="" or data[4]=="" or data[5]=="": 
        Tk().withdraw()
        messagebox.showwarning("Увага!", 
                "Інформація не введена в одне з обов'язкових полів!")

    elif data[0] == 'Додати' and data[7]=='image_Button':
        Tk().withdraw()
        messagebox.showwarning("Увага!", "Зображення не вибрано!")

    elif data[0] == 'Додати' and id_exist == True:
        Tk().withdraw()
        messagebox.showwarning("Увага!", "Така особа вже існує!")
    
    else:
        #If 'Add' is selected
        if ui.comboBox_addEdit.currentIndex() == 0:
            image, small_frame, face_loc = img_pros(img_path)
            face_enc = face_encodings(small_frame, face_loc)
            face_enc = ndarray.tobytes(face_enc[0])

            Users_data.create(pos=data[5].lower().capitalize(), 
                            doc_id=data[4].upper(),
                            l_n=data[1], f_n=data[2], 
                            m_n=data[3], face=face_enc)
            
            cv2.imwrite(f'Persons\\{data[4]}.jpg', image)
            Tk().withdraw()
            messagebox.showinfo("Готово!", "Особу додано!")

        else:     
            if output_doc_id != data[4] and id_exist == True:
                Tk().withdraw()
                messagebox.showwarning("Увага!", "Така особа вже існує!")

            # If the image has not changed
            elif f'{data[7]}.jpg' in filenames:
                Users_data.update(pos=data[5].lower().capitalize(), 
                    doc_id=data[4].upper(),
                    l_n=data[1], f_n=data[2], 
                    m_n=data[3]).where(Users_data.user_id==data[0]).execute()
                
                # Rename the image if doc_id has been changed
                if output_doc_id != data[4]: 
                    rename(f'Persons\\{data[7]}.jpg', f'Persons\\{data[4]}.jpg')
            
            else:
                image, small_frame, face_loc = img_pros(img_path)
                face_enc = face_encodings(small_frame, face_loc)
                face_enc = ndarray.tobytes(face_enc[0])

                Users_data.update(pos=data[5].lower().capitalize(), 
                    doc_id=data[4].upper(),
                    l_n=data[1], f_n=data[2], 
                    m_n=data[3], 
                    face=face_enc).where(Users_data.user_id==data[0]).execute()

                remove(f'Persons\\{output_doc_id}.jpg')
                cv2.imwrite(f'Persons\\{data[4]}.jpg', image)

        gen_in_combo()
                
ui.comboBox_addEdit.currentIndexChanged.connect(inserting_data)
ui.image_Button.clicked.connect(open_image)
ui.pushButton_clear.clicked.connect(lambda: ui.listWidget.clear())
ui.pushButton_add.clicked.connect(batch_list)
ui.pushButton_delete.clicked.connect(delete)
ui.pushButton_save.clicked.connect(save_data)
    

Pass_Biom.show()
db.close()
app.aboutToQuit.connect(lambda: UploadToGDrive())
exit(app.exec())