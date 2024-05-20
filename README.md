# README

This python module manages the usbipd connection for multiple USB devices.
Run this in windows (not WSL).

This assumes that `usbipd` is can be found on your system PATH. You also need to
ensure that your WSL udev rules are configured to allow xmos usb devices.

## Installation

```
# From the root of this repo
pip install .
```

## Running

In an administrator shell:

```
python -m wsl_usb_con
```

Follow the instructions interactively to choose all the USB devices to connect.

**After starting the script the udev rules in wsl must be reloaded.**

```
# in WSL
service udev restart
udevadm control --reload-rules
udevadm trigger
```

