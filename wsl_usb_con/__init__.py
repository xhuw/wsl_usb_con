

VERSION = "0.1.0"

from . import usbipd
import sys
import time
from logging import basicConfig

def main():
    basicConfig(level="INFO")
    while True:
        usb_info = usbipd.list()
        print("select from: ")
        print("\t" + "\n\t".join(map(lambda x: f"{x[0]:3d}: {x[1]['BUSID']:5}  -  {x[1]['DEVICE'][:20]:20}  -  {x[1]['STATE']}", enumerate(usb_info))) + "\n")
        try:
            default = str([i for i, d in enumerate(usb_info) if "XTAG" in d['DEVICE']][0])
            from_user = input(f"space separated idx or [r]efresh or [q]uit, default {default}: ")
            from_user = from_user or default
        except IndexError:
            from_user = input("space separated idx or [r]efresh or [q]uit: ")
        if from_user.strip().lower() == "q":
            exit()
        if from_user.strip().lower() != "r":
            break
    
    ids = [int(i) for i in from_user.strip().split()]
    assert max(ids) < len(usb_info)

    devices = [
        usbipd.ManageDevice(usb_info[i]["BUSID"]) for i in ids
    ]

    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        list(map(lambda x: x.close(), devices))
