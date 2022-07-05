# PassBiom Administrator
This part of the project is an administrator interface application designed to add personal data to the database.

![Admin_app](/PassBiom_Administrator/Screenshots/Admin_app.png)

Before using this application, you need to create a personal profile in [Google Cloud](https://console.cloud.google.com/welcome?project=passbiom-348314&hl=ru) and receive a JSON file with credentials. It should be placed in the folder with the project. This is necessary so that after saving the data to the database and closing the application window, the database can go to the specified cloud for further download by the device.

Adding can be done in two ways:
1. One person at a time;
2. Batch addition.

If everything is clear with individual addition of persons, then with batch addition, questions may arise. To add many people at once, you need to collect all the photos with the correct signature (Person_position + Document_ID + Surname + First_name + Parental) and a clear face image in the "Batch_adding" folder, then click the "Додати" button.

The structure of the database is as follows:

![DB_structure](/PassBiom_Administrator/Screenshots/DB_structure.png)

## Prerequisites
In order for the program to work, you need to install several additional modules. They can be installed with the following command:
```bash
pip install Requirements.txt
```

## Getting started
You can clone the program using the command below or download and unzip the archive.
```bash
https://github.com/AndriyKy/PassBiom.git
```
To run the program, simply run the *DB_administration.py* file.
