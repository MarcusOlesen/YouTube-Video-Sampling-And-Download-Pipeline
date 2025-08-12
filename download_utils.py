import pandas as pd
import yt_dlp as yt
import subprocess
import os
import numpy as np
import time
import random
import json
import zipfile
import sys
import ffmpeg
from datetime import datetime

sys.path.append('../')
from ytutils import *

###############################################################################################################
# Function to check if a video is already in the downloads folder
def is_video_downloaded(video_id, download_dir):
    """
    Checks if a video with the given video ID is already present in the specified download directory.

    Parameters:
        video_id (str): Unique identifier of the video.
        download_dir (str): Directory where downloaded videos are stored.

    Returns:
        bool: True if the video file exists in the download directory, False otherwise.
    """
    file_path = os.path.join(download_dir, f"{video_id}.mp4")
    return os.path.exists(file_path)
###############################################################################################################

#  Function to check if the video has been logged (regardles if successful or not)
def is_video_attempted_downloded(video_id, log_path):
    """
    Checks if a log entry exists for a given video ID, indicating that a download attempt (successful or failed) 
    has already been made.

    Parameters:
        video_id (str): Unique identifier of the video.
        log_path (str): Directory where log files are stored.

    Returns:
        bool: True if a log file for the video exists in the log directory, False otherwise.
    """
    file_path = os.path.join(log_path, f"{video_id}.log.csv")
    return os.path.exists(file_path)
###############################################################################################################

# Function to check if a participant has a log that notes that they have insufficiant videos
def not_enough_videos(participant, log_path):
    """
    Checks if a participant has a log entry indicating they do not have enough videos to meet the required sample size (from an ealier run).

    Parameters:
        participant (str): Unique identifier of the participant.
        log_path (str): Directory where log files are stored.

    Returns:
        bool: True if a log file indicating insufficient videos exists for the participant, False otherwise.
    """
    file_path = f"{log_path}/insufficiant_vids_{participant}.log.csv"
    return os.path.exists(file_path)
###############################################################################################################

# Given a log dataframe containing all the log entries from log_path this function checks 
# how many videos have been successfully downloaded for a participant
def nb_videos_downloaded(log_df, participant):
    """
    Counts the number of videos successfully downloaded for a specified participant by filtering a log DataFrame. 
    If the log DataFrame is empty, returns zero.

    Parameters:
        log_df (pd.DataFrame): DataFrame containing log entries, with columns 'Participant ID' and 'status'.
        participant (str): Unique identifier of the participant.

    Returns:
        int: Number of videos successfully downloaded for the participant, based on entries where status is 'successful'.

    Notes:
        - The function first checks if the log DataFrame is empty; if so, it returns 0 immediately.
        - Only entries with the status 'successful' are counted, providing an accurate count of completed downloads.
    """
    if log_df.empty:
        return 0
    
    # Filter the DataFrame for the specified Participant ID and where status is True
    filtered_df = log_df[(log_df['Participant ID'] == participant) & (log_df['status'] == 'successful')]
    return len(filtered_df)
###############################################################################################################

def now():
    return pd.to_datetime(datetime.now())
###############################################################################################################

# Function that makes a log entry (.csv) for a video. This log entry is saved to log_path. 
def make_log_entry(participant, video_id, success, server_reply, start_time, end_time, log_path, exept = False, log=False, size=None, info={}):
    """
    Creates a log entry for a video download attempt, recording the participant ID, video ID, download status, 
    server response, and download duration. Saves the entry as a CSV file in the specified log directory.

    Parameters:
        participant (str): Unique identifier of the participant.
        video_id (str): Unique identifier of the video.
        success (bool): Indicates whether the download was successful.
        server_reply (str): Response message from the server or download tool.
        time (float): Time taken for the download in minutes.
        log_path (str): Directory where the log file will be saved.
        exept (bool): If True, indicates that this log entry is a special case for participants with insufficient videos.

    Returns:
        None

    Notes:
        - For participants with insufficient videos, a special log file is created to indicate the case.
        - Each log entry is saved in a separate CSV file named after the video ID or participant, depending on context.
    """
    total_seconds = (end_time-start_time).total_seconds()


    log_data = {
                    'Participant ID': participant,
                    'video_id': video_id,
                    'status': 'successful' if success else 'failed',
                    'server_reply': server_reply,
                    'size_MB': round(size / 1024**2, 2) if size else None,
                    'start_time': start_time, 
                    'end_time': end_time,
                    'download_time_minutes': round(total_seconds/60, 2),
                    'download_speed_KBs': round((size/1024)/total_seconds, 2) if size else None
                }
    log_data.update(info)
    log_data.update({'log': log})
    
    if exept: # special case where participant does not have enough videos
        temp_log_file_path = f"{log_path}/insufficiant_vids_{participant}.log.csv"
    else:
        temp_log_file_path = f"{log_path}/{video_id}.log.csv"
    
    log_df = pd.DataFrame([log_data])  # Wrap in a list to keep it as one row
            # Save each result in the log entry folder
    log_df.to_csv(temp_log_file_path, index=False)
###############################################################################################################

# Function to run through all the log files in log_path (each created by make_log_entry) 
# and concatinate them into one dataframe that can be used to check for vidoes downloaded 
# or attempted downloaded  
def concatenate_logs(log_path):
    """
    Combines all individual log CSV files in the specified directory into a single DataFrame. Useful for creating 
    a complete log of all download attempts, including successes, failures, and cases with insufficient videos.

    Parameters:
        log_path (str): Directory where log files are stored.

    Returns:
        pd.DataFrame: Concatenated DataFrame containing all log entries from individual CSV files. Returns an empty 
                    DataFrame if no log files are found.

    Notes:
        - Each CSV file is read and added to a list, which is then concatenated into a single DataFrame.
        - Files are expected to have standard columns like 'Participant ID', 'video_id', 'status', 'server_reply', start_time, 'download_time_minutes'.
    """
    # List to hold each DataFrame
    dataframes = []
    
    # Iterate over all files in the folder
    for filename in os.listdir(log_path):
        # Check if the file is a CSV
        if filename.endswith(".csv"):
            file_path = os.path.join(log_path, filename)
            
            # Read CSV file into a DataFrame and append it to the list
            df = pd.read_csv(file_path, dtype={'Participant ID': str, 'video_id': str})
            if 'log' in df.columns:
                df = df.drop(columns=['log'])
            dataframes.append(df)
    
    # Concatenate all DataFrames in the list
    if dataframes:  # Check if there are any dataframes to concatenate
        concatenated_df = pd.concat(dataframes, ignore_index=True)
    else:
        concatenated_df = pd.DataFrame()  # Return an empty DataFrame if no CSV files found
    
    return concatenated_df
###############################################################################################################
import shutil

def reset_directory(dir):
    # Check if the directory exists
    if os.path.exists(dir):
        # Delete the directory and its contents
        shutil.rmtree(dir)
    
    # Recreate the directory as an empty folder
    os.makedirs(dir)
    print(f"Reset directory: {dir}")
###############################################################################################################

# Function to check if video_id exists and extract format, vcodec, and acodec
def get_video_info(video_id, directory):
    # Construct the path to the JSON file using the video_id
    json_file_path = os.path.join(directory, f'{video_id}.info.json')
    
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        return {
        "format": None,
        "vcodec": None,
        "acodec": None
    }

    # Open and load the JSON data from file
    with open(json_file_path, 'rb') as f:
        data = json.load(f)

    # Extract the required information
    format_info = data.get("format", "Format not found")
    vcodec_info = data.get("vcodec", "VCodec not found")
    acodec_info = data.get("acodec", "ACodec not found")

    # Return the extracted information
    return {
        "format": format_info,
        "vcodec": vcodec_info,
        "acodec": acodec_info
    }
###############################################################################################################

class MyLogger:
    def __init__(self):
        self.logs = []  # Store logs in a list

    def debug(self, msg):
        # Capture all debug messages, including verbose logs
        self.logs.append(f"DEBUG: {msg}")

    def warning(self, msg):
        # Capture warnings
        self.logs.append(f"WARNING: {msg}")

    def error(self, msg):
        # Capture errors
        self.logs.append(f"ERROR: {msg}")
###############################################################################################################

