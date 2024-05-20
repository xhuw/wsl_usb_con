from subprocess import Popen, PIPE, run
from dataclasses import dataclass
import threading
import queue
import os
from logging import getLogger

LOGGER = getLogger(__name__)

def _parse_list_output(output):
    (header, *content) = output.split("\n")
    vid_pid_idx = header.find("VID:PID")
    device_idx = header.find("DEVICE")
    state_idx = header.find("STATE")

    ret = []
    for row in content:
        if row:
            ret.append({
                "BUSID": row[:vid_pid_idx].strip(),
                "VID:PID": row[vid_pid_idx:device_idx].strip(),
                "DEVICE": row[device_idx:state_idx].strip(),
                "STATE": row[state_idx:].strip()
            })
    return ret

def list():
    ret = run(
        "usbipd wsl list".split(),
        capture_output=True,
        text=True,
        check=True
    )
    ret = _parse_list_output(ret.stdout)
    return ret

@dataclass
class ErrCode:
    code: int

@dataclass
class Stdout:
    line: str

@dataclass
class Stderr:
    line: str


def wait_for_errcode(proc, q: queue.Queue, idx):
    return_code = proc.wait()
    q.put((idx, ErrCode(return_code)))


def wait_for_line(f, logger):
    while True:
        line = f.readline().strip()
        if not line:
            break
        logger.info(line)

class ManageDevice():

    def __init__(self, dev_name):
        self._dev_name = dev_name

        self._logger = LOGGER.getChild(dev_name)
        self._proc = Popen(f"usbipd wsl attach -ab {dev_name}".split(), text=True, stderr=PIPE, stdout=PIPE)
        self._threads = [
            # threading.Thread(target=wait_for_errcode, args=(self._proc, self._queue, self._idx)),
            threading.Thread(target=wait_for_line, args=(self._proc.stderr, self._logger)),
            threading.Thread(target=wait_for_line, args=(self._proc.stdout, self._logger))
        ]
        for i in self._threads:
            i.start()
    
    def close(self):
        self._proc.terminate()
        self._proc.wait()
        if self._proc.returncode != 0:
            # raise RuntimeError(f"Attach loop for {self._dev_name} exited with {self._proc.returncode}")
            # ignore exit code as we kill it and it returns non 0
            pass
        for t in self._threads:
            t.join()
        det_ret = run(
            f"usbipd wsl detach -b {self._dev_name}".split(),
            capture_output=True,
            text=True
        )
        if det_ret.stdout:
            self._logger.info(det_ret.stdout)
        if det_ret.stderr:
            self._logger.error(det_ret.stderr)
        if det_ret.returncode:
            self._logger.error("failed to detach usb from wsl")


def test():
    from logging import basicConfig
    basicConfig(level="INFO")
    print("start")
    dev = ManageDevice("2-7")
    import time
    time.sleep(3)
    print("close")
    dev.close()

