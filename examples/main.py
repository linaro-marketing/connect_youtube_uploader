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

from connect_youtube_uploader import ConnectYoutubeUploader

video_manager = ConnectYoutubeUploader(
    "")
updated = video_manager.get_video_id_based_on_session_id("yvr18-100k")
