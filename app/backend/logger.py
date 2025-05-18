import datetime
import os

LOGNAME = "log.txt"

def start_log():
    if os.path.exists(LOGNAME):
        time = f"_no_time_found_{datetime.datetime.now()}"
        with open(LOGNAME, "r") as f:
            line = f.read().split("\n")[0]
            if line.startswith("Server started at"):
                time = " ".join(line.split(" ")[3:])
        os.rename(LOGNAME, f"log_old{time}.txt")
    with open(LOGNAME, "w") as f:
        f.write(f"Server started at {datetime.datetime.now()}\n")

def log_message(message):
    with open(LOGNAME, "a") as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

def log_error(error):
    with open(LOGNAME, "a") as f:
        f.write(f"{datetime.datetime.now()}: USER ERROR: {error}\n")

def log_update(update):
    with open(LOGNAME, "a") as f:
        f.write(f"{datetime.datetime.now()}: UPDATE: {update}\n")