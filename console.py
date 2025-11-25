from datetime import datetime
import os
def sendWarning(message,src):
    print(f"[{datetime.now()}] [{os.path.abspath(src)}] WARNING: {message}")
def sendError(message,src):
    print(f"[{datetime.now()}] [{os.path.abspath(src)}] ERROR: {message}")
def sendInfo(message,src):
    print(f"[{datetime.now()}] [{os.path.abspath(src)}] INFO: {message}")