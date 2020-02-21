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

from sched_data_interface import SchedDataInterface
from connect_youtube_uploader import ConnectYoutubeUploader

video_manager = ConnectYoutubeUploader(SECRETS_DIR, SECRETS_FILE)

# path_to_downloaded_video = video_manager.download_video("https://static.linaro.org/connect/bud20/videos/bud20-215.mp4",
#                                 "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/")
video_options={
    "file": "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/bud20-215.mp4",
            "title": "BUD20-215: Test video",
            "description": "Test Video",
            "keywords": "bud20,Open Source,Arm, budapest",
            "category": "28",
            "privacyStatus": "private"
}
video_id = video_manager.upload_video(video_options)
print(video_id)
thumbnail_set = video_manager.set_custom_thumbnail("/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/social_image_generator/output/BUD20-215.png", video_id)
print(thumbnail_set)
