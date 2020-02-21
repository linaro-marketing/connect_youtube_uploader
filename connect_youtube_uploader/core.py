
#!/usr/bin/python3

from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from apiclient.discovery import build
import time
import sys
import random
import os
import httplib2
import json
import boto3
import requests

try:
    import httplib
except ImportError:  # python3 compatibility
    from http import client
    httplib = client

from oauth2client import client
from oauth2client import file
from oauth2client import tools


class cmd_flags(object):
    """
        Used to provide command-line level authentication rather than
        working through a web browser.
    """

    def __init__(self):
        self.auth_host_name = 'localhost'
        self.auth_host_port = [8080, 8090]
        self.logging_level = 'ERROR'
        self.noauth_local_webserver = True


class ConnectYoutubeUploader:
    """
    The ConnectYoutubeUploader enabled a video to be downloaded from s3 based on a session_id
    and uploaded to YouTube with the title/descriptions populated based on data from the SchedDataInterface
    module.

    Attributes
    ----------
    s3_bucket : string
        The s3 bucket e.g static-linaro-org
    videos_object_prefix: string
        The s3 object key prefix to the video objects e.g. connect/SAN19/videos/
    session_id: string
        The session id for a given video.

    Methods
    -------
    upload()
        Uploads a local .mp4 video to YouTube and adds video metadata based on the data
        provided by the SchedDataInterface.
    """

    def __init__(self, secrets_dir, client_secrets_file_name):

        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1

        # Always retry when these exceptions are raised.
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                                     httplib.IncompleteRead, httplib.ImproperConnectionState,
                                     httplib.CannotSendRequest, httplib.CannotSendHeader,
                                     httplib.ResponseNotReady, httplib.BadStatusLine)

        # Always retry when an apiclient.errors.HttpError with one of these status
        # codes is raised.
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

        # Maximum number of times to retry before giving up.
        self.MAX_RETRIES = 10

        # The secrets secrets_directory
        self.SECRETS_DIRECTORY = secrets_dir

        # The clients secrets file to use when authenticating our requests to the YouTube Data API
        self.CLIENT_SECRETS_FILE = client_secrets_file_name

        # This variable defines a message to display if the CLIENT_SECRETS_FILE is
        # missing.
        self.MISSING_CLIENT_SECRETS_MESSAGE = ""
        # WARNING: Please configure OAuth 2.0
        # To make this sample run you will need to populate the client_secrets.json file
        # found at:
        # %s
        # with information from the {{ Cloud Console }}
        # {{ https://cloud.google.com/console }}
        # For more information about the client_secrets.json file format, please visit:
        # https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        # """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
        #                                 self.CLIENT_SECRETS_FILE))

        # This OAuth 2.0 access scope allows an application to upload files to the
        # authenticated user's YouTube channel, but doesn't allow other types of access.
        self.YOUTUBE_UPLOAD_SCOPE = ['https://www.googleapis.com/auth/youtube']

        # Name of the API service
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'

        # Version of the YouTube API
        self.YOUTUBE_API_VERSION = 'v3'

        # Privacy statuses we can use to set on YouTube videos
        self.VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

        # The ID of the playlist for the current Connect
        # In the future this playlist ID should be retrieved dynamically based on the
        # connect code
        self.playlist_id = "PLKZSArYQptsOzc0kBoWyVSC3f0sHbJdBK"

        # Get the authenticated service to use in requests to the API
        self.service = self.get_authenticated_service()

    # Authorize the request and store authorization credentials.

    def get_authenticated_service(self):
        """
            Gets an authenticated service object for requests to the
            YouTube Data API
        """

        store = file.Storage(self.SECRETS_DIRECTORY +
                             "connect_youtube_uploader-oauth2.json")

        creds = store.get()

        if creds is None or creds.invalid:
            flow = client.flow_from_clientsecrets(self.SECRETS_DIRECTORY + self.CLIENT_SECRETS_FILE,
                                                  scope=self.YOUTUBE_UPLOAD_SCOPE,
                                                  message=self.MISSING_CLIENT_SECRETS_MESSAGE)
            creds = tools.run_flow(flow, store, cmd_flags())

        return build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                     http=creds.authorize(httplib2.Http()))

    def get_video_id_based_on_session_id(self, session_id):
        """
            Retrieve a video id of a YouTube video based on a session_id
        """
        current_videos = self.get_current_youtube_videos_based_on_string(
            session_id)
        if len(current_videos) == 1:
            return current_videos[0][1]
        else:
            return False

    def download_video(self, video_url, output_folder):
        """Downloads a video from video_url and outputs to output_path"""
        response = requests.get(video_url, stream=True)
        filename = os.path.split(video_url)[1]
        output_path = output_folder + filename
        if os.path.exists(output_folder) != True:
            print("Creating {}".format(output_folder))
            os.makedirs(output_folder)
        print("Downloading {} to {}".format(filename, output_folder))
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return output_path

    def update_video_status(self, video_id, status):
        """
            This method updates the status of a video based on the video_id and status provided.
        """
        # Call the API's videos.list method to retrieve the video resource.
        # Get the current video details
        videos_list_response = self.service.videos().list(
            id=video_id,
            part='status'
        ).execute()

        # If the response does not contain an array of 'items' then the video was
        # not found.
        if not videos_list_response['items']:
            return False

        # Since the request specified a video ID, the response only contains one
        # video resource. This code extracts the snippet from that resource.
        video_list_status = videos_list_response['items'][0]['status']
        print(video_list_status)
        input()

        # Set the privacy status of the video
        if status:
            video_list_status['privacyStatus'] = status

        # Update the video resource by calling the videos.update() method.
        self.service.videos().update(
            part='status',
            body=dict(
                status=video_list_status,
                id=video_id
            )).execute()

        return True

    def get_current_youtube_videos_based_on_string(self, string):
        """
            Gets the current videos on YouTube that contain the specified string in
            in the title or description
        """
        # Get the channels on Youtube and their ID's i.e uploads
        channels_response = self.service.channels().list(
            mine=True,
            part="contentDetails"
        ).execute()
        # From the API response, extract the playlist ID that identifies the list
        # of videos uploaded to the authenticated user's channel.
        youtube_uploads_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        # Retrieve the list of videos uploaded to the authenticated user's channel.
        playlistitems_list_request = self.service.playlistItems().list(
            playlistId=youtube_uploads_id,
            part="snippet",
            maxResults=50
        )
        videos = []
        while playlistitems_list_request:
            playlistitems_list_response = playlistitems_list_request.execute()
            # Print information about each video.
            for playlist_item in playlistitems_list_response["items"]:
                title = playlist_item["snippet"]["title"]
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                if string.lower() in title:
                    print("%s (%s)" % (title, video_id))
                    videos.append([title, video_id])
            playlistitems_list_request = self.service.playlistItems().list_next(
                playlistitems_list_request, playlistitems_list_response)
        if len(videos) > 0:
            return videos
        else:
            return False

    def build_resource(self, properties):
        """
            # Build a resource based on a list of properties given as key-value pairs.
            # Leave properties with empty values out of the inserted resource.
        """
        resource = {}
        for p in properties:
            # Given a key like "snippet.title", split into "snippet" and "title", where
            # "snippet" will be an object and "title" will be a property in that object.
            prop_array = p.split('.')
            ref = resource
            for pa in range(0, len(prop_array)):
                is_array = False
                key = prop_array[pa]
                # For properties that have array values, convert a name like
                # "snippet.tags[]" to snippet.tags, and set a flag to handle
                # the value as an array.
                if key[-2:] == '[]':
                    key = key[0:len(key)-2:]
                    is_array = True

                if pa == (len(prop_array) - 1):
                    # Leave properties without values out of inserted resource.
                    if properties[p]:
                        if is_array:
                            ref[key] = properties[p].split(',')
                        else:
                            ref[key] = properties[p]
                elif key not in ref:
                    # For example, the property is "snippet.title", but the resource does
                    # not yet have a "snippet" object. Create the snippet object here.
                    # Setting "ref = ref[key]" means that in the next time through the
                    # "for pa in range ..." loop, we will be setting a property in the
                    # resource's "snippet" object.
                    ref[key] = {}
                    ref = ref[key]
                else:
                    # For example, the property is "snippet.description", and the resource
                    # already has a "snippet" object.
                    ref = ref[key]
        return resource

    def upload_video(self, options):
        """
            Takes a dictionary of all video details e.g
            {
                "file":"/home/kyle.kirkby/Documents/Marketing/Connect/YVR18/videos/yvr18-100k.mp4",
                "title": "YVR18-100k: Opening Keynote by George Grey",
                "description": "The Opening Keynote by George Grey at Linaro Connect Vancouver 2018",
                "keywords": "Keynote,yvr18,Open Source,Arm, Vancouver",
                "category": "28",
                "privacyStatus": "private"
            }
        """
        request = self.get_upload_request(options)
        # Output Details while uploading
        video_id = self.resumable_upload(request, options["title"])
        return video_id

    def add_video_to_playlist(self, playlistId, videoId):
        """Adds a video(videoId) to a playlist(playlistId)"""
        # Create the body of the request

        bodyData = {'snippet.playlistId': playlistId,
                    'snippet.resourceId.kind': 'youtube#video',
                    'snippet.resourceId.videoId': videoId,
                    'snippet.position': ''}

        resource = self.build_resource(bodyData)

        add_to_playlist = self.service.playlistItems().insert(
            body=resource,
            part='snippet'
        ).execute()

        return add_to_playlist

    def get_upload_request(self, options):
        """
            Create the request to initialize the upload of a video.
            Takes a service and a dictionary containing the various options
        """

        # Get the Youtube Tags from the keywords
        tags = None
        try:
            if options["tags"]:
                tags = options["tags"].split(',')
        except Exception as e:
            tags = []

        # Create the body of the request
        body = dict(
            snippet=dict(
                title=options["title"][0:70],
                description=options["description"],
                tags=tags,
                categoryId=28
            ),
            status=dict(
                privacyStatus=options["privacyStatus"]
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = self.service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            # The chunksize parameter specifies the size of each chunk of data, in
            # bytes, that will be uploaded at a time. Set a higher value for
            # reliable connections as fewer chunks lead to faster uploads. Set a lower
            # value for better recovery on less reliable connections.
            #
            # Setting 'chunksize' equal to -1 in the code below means that the entire
            # file will be uploaded in a single HTTP request. (If the upload fails,
            # it will still be retried where it left off.) This is usually a best
            # practice, but if you're using Python older than 2.6 or if you're
            # running on App Engine, you should set the chunksize to something like
            # 1024 * 1024 (1 megabyte).
            media_body=MediaFileUpload(
                options["file"], chunksize=-1, resumable=True)
        )

        return insert_request

    def resumable_upload(self, request, title):
        """
            Creates a resumable upload
        """
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading {0} file...".format(title))
                status, response = request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print("Video id '%s' was successfully uploaded." %
                              response['id'])
                        video_id = response['id']
                        return video_id
                    else:
                        exit(
                            "The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." %
                      sleep_seconds)
                time.sleep(sleep_seconds)


if __name__ == "__main__":
    video_manager = ConnectYoutubeUploader("", "")
    # path_to_downloaded_video = video_manager.download_video("https://static.linaro.org/connect/bud20/videos/san19-405.mp4",
    #                              "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/")
    video_options={
        "file": "/home/kyle/Documents/scripts_and_snippets/ConnectAutomation/connect_youtube_uploader/output/san19-405.mp4",
                "title": "BUD20-212: Test video",
                "description": "Test Video",
                "keywords": "bud20,Open Source,Arm, budapest",
                "category": "28",
                "privacyStatus": "private"
    }
    uploaded = video_manager.upload_video(video_options)
