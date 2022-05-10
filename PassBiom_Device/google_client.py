from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from datetime import date
from os import remove, popen

try:
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile('client_secret.json')
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
except: pass

def GetDriveContent():
    try:
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['title'] == 'Face_rec_data.sqlite':
                return file['id']
        return 0
    except: pass

def UploadToGDrive():
    try:
        x = 'Face_rec_data.sqlite'
        f = drive.CreateFile({'title': f'00000000867901b9_{date.today()}.sqlite'})
        f.SetContentFile(x)
        f.Upload()
        f = None
    except: 
        popen(f'copy Face_rec_data.sqlite 00000000867901b9_{date.today()}.sqlite')

# UploadToGDrive()

def LoadFromGDrive():
    try:
        try:
            remove('Face_rec_data.sqlite')
        except FileNotFoundError: pass

        id = GetDriveContent()
        file_obj = drive.CreateFile({'id': id})
        file_obj.GetContentFile("Face_rec_data.sqlite")
        file_obj = None
    except: pass
# LoadFromGDrive()