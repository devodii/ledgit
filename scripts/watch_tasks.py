import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

LOG = Path(os.environ.get("TASKS_LOG", "data/tasks/open.log"))


def play_sound() -> None:
    system = platform.system()
    if system == "Darwin" and shutil.which("afplay"):
        subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"], check=False)
    elif system == "Linux" and shutil.which("paplay"):
        subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"], check=False)
    elif system == "Linux" and shutil.which("aplay"):
        subprocess.run(["aplay", "-q", "/usr/share/sounds/alsa/Front_Center.wav"], check=False)
    elif system == "Windows":
        subprocess.run(["powershell", "-c", "[console]::beep(880,300)"], check=False)
    else:
        sys.stdout.write("\a")
        sys.stdout.flush()


def main() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.touch()
    print(f"watching {LOG} for new human tasks (Ctrl+C to stop)", flush=True)
    with LOG.open() as handle:
        handle.seek(0, os.SEEK_END)
        while True:
            line = handle.readline()
            if line:
                print(f"NEEDS YOU: {line.strip()}", flush=True)
                play_sound()
            else:
                time.sleep(1)


if __name__ == "__main__":
    main()
