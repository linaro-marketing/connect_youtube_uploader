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
    from secrets import SECRETS_FILE, SECRETS_DIR, SCHED_API_KEY
except Exception as e:
    SECRETS_FILE = ""
    SECRETS_DIR = ""

from sched_data_interface import SchedDataInterface
from connect_youtube_uploader import ConnectYoutubeUploader

video_manager = ConnectYoutubeUploader(SECRETS_DIR, SECRETS_FILE)
data_interface =  SchedDataInterface(
                "https://bud20.sched.com",
                SCHED_API_KEY,
                "bud20")
sched_data =  data_interface.getSessionsData()
session_data = sched_data["BUD20-215"]
print(session_data)

session_speakers_description = ""
for speaker in session_data["speakers"]:
    speaker_role = ""
    if speaker["company"] != "" and speaker["position"] != "":
        speaker_role = f"{speaker['position']} at {speaker['company']}"
    elif speaker["company"] != "":
        speaker_role = speaker['company']
    elif speaker["position"] != "":
        speaker_role = speaker['position']
    session_speakers_description += f"{speaker['name']} - {speaker_role} \n {speaker['about']}"
session_abstract = session_data["description"].replace("<br>","\n").replace("<br/>", "\n")


connect_website_url = "https://connect.linaro.org/resources/{}/session/{}/".format("bud20", "bud20-215")
video_description = """Session Abstract

{}

Speakers

{}

Visit the Linaro Connect website for the session presentations and more:

{}
""".format(session_abstract, session_speakers_description, connect_website_url)
video_options={
    "file": "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/bud20-215.mp4",
            "title": session_data["name"],
            "description": video_description,
            "tags": "bud20,Open Source,Arm, budapest",
            "category": "28",
            "privacyStatus": "private"
}
print(video_options)
input()
video_id = video_manager.upload_video(video_options)
print(video_id)
thumbnail_set = video_manager.set_custom_thumbnail("/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/social_image_generator/output/BUD20-215.png", video_id)
print(thumbnail_set)
