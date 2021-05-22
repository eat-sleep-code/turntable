# Turntable

This program is designed for a custom-built turntable used for photogrammetry (photography-based 3D scanning).


---
## Use With Other Camera Software

**Required:** this application may be used in conjunction with the following application:
   - [Camera Remote](https://github.com/eat-sleep-code/camera.remote): Turntable is designed to trigger this program via a web request.


---
## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 64MB
  - Enable I2C
  - Enable SPI
  - Set up your WiFi connection


## Installation

Installation of the program and any software prerequisites can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/turntable/main/install-turntable.sh -O ~/install-turntable.sh
sudo chmod +x ~/install-turntable.sh && ~/install-turntable.sh
```

---

## Usage
```
turntable
```

---

## Autostart Turntable Service
Want to start the Turntable service every time you boot your Raspberry Pi?  Here is how!

* Run `~/turntable/install-turntable.service.sh`
