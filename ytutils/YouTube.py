import pandas as pd
import yt_dlp as yt
import subprocess
import os
import numpy as np
import time

def downloadVideos(watch_history, output_folder_path, s=0, format="b", provided=False, generated=False, number_to_download=False):
    """
    This function downloads subtitles, info files, thumbnails and videos from the watch history dataframe.
    --- args ---
    watch_history: pandas.DataFrame
    output_folder_path: string

    --- kwargs ---
    s: float                 |  default: 0     # set to amount of seconds to pause between downloads
    format: string           |  default: "b"   # see in format options below
    provided: bool           |  default: True  # set to False to only download auto-generated subtitles
    generated: bool          |  default: True  # set to False to only download provided subtitles
    number_to_download: int  |  default: All unique videos

    --- output ---
    Outputs to "output_folder_path" directory
    subtitles: .vtt
    info files: .json
    thumbnails: .webp
    videos: .mp4

    ## format options ##
    format="b"    (Best)
    format="22"   (720p)
    format="18"   (360p)
    format="133"  (240p)
    format="160"  (144p)
    format="w"    (Worst)
    """

    # Get unique id's as a list
    na_removed_watch_history = watch_history[watch_history["video_id"].notna()]
    video_ids = pd.unique(na_removed_watch_history["video_id"]).tolist()

    downloaded_videos = os.listdir(output_folder_path)  # Find all files in folder
    downloaded_videos_id = [file[:11] for file in downloaded_videos if file.endswith(".mp4")]  # Find all downloaded videos in the folder and extract their video id to a list

    # Get number of videos to download (primarily for testing)
    if number_to_download:
        video_ids = video_ids[:number_to_download]

    url_prefix = "https://www.youtube.com/watch?v="  # Get the url prefix for merging with video id's

    # Iterate through the id's
    for video_id in video_ids:
        if video_id in downloaded_videos_id:
            continue

        url = url_prefix + video_id  # Get the url

        if provided:
            # We define the yt-dlp command with the below command for the command line, where we can specify options.
            yt_dlp_command = f"yt-dlp -f {format} --write-sub --write-info-json --write-thumbnail -o \"{output_folder_path}{video_id}.mp4\" \"{url}\""
        if not provided and generated:
            # We define the yt-dlp command with the below command for the command line, where we can specify options.
            yt_dlp_command = f"yt-dlp -f {format} --write-auto-subs --write-info-json --write-thumbnail -o \"{output_folder_path}{video_id}.mp4\" \"{url}\""
        if not provided and not generated:
            # We define the yt-dlp command with the below command for the command line, where we can specify options.
            yt_dlp_command = f"yt-dlp -f {format} --write-info-json --write-thumbnail -o \"{output_folder_path}{video_id}.mp4\" \"{url}\""

        time.sleep(s)
        # Run the command from command line
        subprocess.run(yt_dlp_command, stdout=subprocess.PIPE, shell=True, text=True)

        # Read .info.json file
        try:
            infofile = pd.read_json(f"{output_folder_path}{video_id}.info.json", lines=True)
            if provided:
                # Initiate that videos have provided subtitles
                infofile["subtitles_are_provided"] = True
            if not provided:
                # Initiate that videos don't have provided subtitles
                infofile["subtitles_are_provided"] = False
            # Write initialization to .info.json file
            infofile.to_json(f"{output_folder_path}{video_id}.info.json", index=False)
        except FileNotFoundError:
            continue

    if provided and generated:
        downloaded_subtitles = os.listdir(output_folder_path)  # Find all files in folder
        downloaded_subtitles_id = [file[:11] for file in downloaded_subtitles if file.endswith(".vtt")]  # Find all downloaded subtitles in the folder and extract their video id to a list
        not_downloaded = [id for id in video_ids if id not in downloaded_subtitles_id]  # Create a list with the id's for the subtitles that needs to be downloaded, but hasn't been downloaded yet

        for video_id in not_downloaded:
            # Video does not have provided subtitles
            try:
                infofile = pd.read_json(f"{output_folder_path}{video_id}.info.json")
                infofile["subtitles_are_provided"] = False
                infofile.to_json(f"{output_folder_path}{video_id}.info.json", index=False)

                url = url_prefix + video_id  # Get the url
                yt_dlp_command = f"yt-dlp --skip-download --write-auto-subs -o \"{output_folder_path}{video_id}\" \"{url}\""
                subprocess.run(yt_dlp_command, stdout=subprocess.PIPE, shell=True, text=True)
            except FileNotFoundError:
                continue