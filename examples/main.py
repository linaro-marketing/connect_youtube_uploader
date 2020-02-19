import xml.etree.ElementTree
from urllib import request
import json
from io import BytesIO
import requests
from slugify import slugify
import re
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
try:
    from secrets import SECRETS_FILE, SECRETS_DIR
except Exception as e:
    SECRETS_FILE = ""
    SECRETS_DIR = ""

from connect_youtube_uploader import ConnectYoutubeUploader

video_manager = ConnectYoutubeUploader(SECRETS_DIR, SECRETS_FILE)
path = video_manager.download_video("https://static.linaro.org/connect/bud20/videos/san19-405.mp4",
                             "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/")
video_options = {
    "file": path,
    "title": "BUD20-212: Test video",
    "description": "Test Video",
    "keywords": "bud20,Open Source,Arm, budapest",
                "category": "28",
                "privacyStatus": "private"
}
uploaded = video_manager.upload_video(video_options)
