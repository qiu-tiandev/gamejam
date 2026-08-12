from datetime import datetime
import os


def _send(level: str, message: str, src: str, color_code: str = ""):
    color_prefix = f"\033[{color_code}m" if color_code else ""
    color_suffix = "\033[0m" if color_code else ""
    print(
        f"{color_prefix}[{datetime.now()}] [{os.path.abspath(src)}] {level}: {message}{color_suffix}"
    )


def sendWarning(message: str, src: str):
    _send("WARNING", message, src, "33")


def sendError(message: str, src: str):
    _send("ERROR", message, src, "31")


def sendInfo(message: str, src: str):
    _send("INFO", message, src)
