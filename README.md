# smart_shoulder_implant
Smart shoulder implant research project integrating Arduino-based sensor data logging, BOTA 6-axis force/torque sensing, and xArm robotic control for data-driven biomechanical testing and evaluation.

## Overview

The project consists of three independent modules:

1) **Embedded Data Logging (Arduino)**  
  Acquisition of sensor signals using an Arduino-based system.

2) **Force/Torque Sensor Logging (Python)**  
  Logging and handling of data from the BOTA MiniONE 6-axis F/T sensor.

3) **Robotic Arm Control (Python)**  
  Control of the UFACTORY xArm 5 robotic arm for repeatable movement and testing.

## System Components

- HSFPAR003A Sensor  
- BOTA MiniONE Series 6-axis F/T Sensor (USB Interface)  
- UFACTORY xArm 5 (5-DoF, 700mm reach)  
- Arduino Microcontroller  

## Repository Structure

firmware/ → Arduino-based data acquisition

robotics/ → Robot arm control scripts

data_acquisition/ → Sensor data logging (BOTA sensor)

data/ → Sample raw data

## Getting Started

Each module is independent and can be run separately.

### Arduino Firmware
- Open `.ino` file in Arduino IDE
- Upload to the microcontroller

### Python Scripts
- Run using Python 3:
```
bash
python main.py
```
Example raw sensor data is provided in "main/data"
**Notes**
This repository reflects an early-stage prototype
Code builds on existing SDKs and hardware interfaces
Components are entirely independent of each other

Author
Vedant
Biomedical Engineering Student
