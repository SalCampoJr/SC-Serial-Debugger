# SC-Serial-Debugger by Salvatore Campo

**SC-Serial-Debugger** is a dedicated graphical user interface (GUI) tool designed to act as a streamlined serial monitor. Built for developers working with embedded systems and serial-connected devices, it offers a minimal, responsive interface for real-time communication over COM ports.

## Features

- Connect to serial devices via COM ports  
- Configure baud rate and port settings  
- View incoming serial data in real time  
- Send text commands to connected devices   
- Includes a standalone `.exe` for Windows

## Requirements

### To run the executable

- Windows operating system  
- No installation required — simply launch `SC-Serial-Debugger.exe`

### To run the source code manually

- Python 3.x  
- `pyserial` library  
- Other dependencies listed in `requirements.txt`

## Installation (for source code)

```bash
# Clone the repository
git clone https://github.com/SalCampoJr/SC-Serial-Debugger.git

# Navigate to the project folder
cd SC-Serial-Debugger

# Install dependencies
pip install -r requirements.txt