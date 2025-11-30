from datetime import datetime
import os
def sendWarning(message,src):
    print(f"\033[33m[{datetime.now()}] [{os.path.abspath(src)}] WARNING: {message}\033[0m")
def sendError(message,src):
    print(f"\033[31m[{datetime.now()}] [{os.path.abspath(src)}] ERROR: {message}\033[0m")
def sendInfo(message,src):
    print(f"[{datetime.now()}] [{os.path.abspath(src)}] INFO: {message}")