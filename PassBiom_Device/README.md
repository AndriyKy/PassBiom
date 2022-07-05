# PassBiom Device
The PassBiom_Device project directory contains software designed to be installed on a Raspberry Pi Model B minicomputer.

The device structure of the recognition system is given below.
![Device`s_structure](/PassBiom_Device/Screenshots/Devices_structure.png)

An example of a successfully passed check.
![Successful_recognition](/PassBiom_Device/Screenshots/Successful_recognition.jpeg)


This directory, like PassBiom_Administrator, should contain a file with [Google Cloud](https://console.cloud.google.com/welcome?project=passbiom-348314&hl=ru) credentials.

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
To run the program, simply run the *main_pi.py* file.
