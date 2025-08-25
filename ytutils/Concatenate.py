import os
import pandas as pd
import numpy as np
from datetime import time
from copy import deepcopy
import warnings
warnings.simplefilter(action='ignore', category=Warning)

def addAverageSpeakingRate(metadata, transcriptions):
    video_ids = pd.unique(transcriptions["id"]).tolist()
    subset_df = metadata[metadata["video_id"].isin(video_ids)][["video_id", "duration_seconds"]].drop_duplicates(subset="video_id")

    # Create a duration- and shots-dictionary
    duration_dict = subset_df.groupby("video_id")["duration_seconds"].first().to_dict()
    transcriptions["word_count"] = transcriptions["text"].apply(lambda x: len([word for word in x.split() if word]))
    total_words_dict = transcriptions.groupby("id")["word_count"].sum().to_dict()
    transcriptions = transcriptions.drop(columns="word_count")

    # Calculate the averageShotLength for each video
    averageSpeakingRate = {}
    for key in duration_dict.keys():
        averageSpeakingRate[key] = total_words_dict[key]/(duration_dict[key]/60)

    metadata["average_speaking_rate_wpm"] = metadata["video_id"].map(averageSpeakingRate)
    return metadata


def addAverageShotLength(metadata, scenes):
    video_ids = pd.unique(scenes["id"]).tolist()
    subset_df = metadata[metadata["video_id"].isin(video_ids)][["video_id", "duration_seconds", "fps"]].drop_duplicates(subset="video_id")

    # Create a duration- and shots-dictionary
    duration_dict = subset_df.groupby("video_id")["duration_seconds"].first().to_dict()
    shots_dict = scenes["id"].value_counts().to_dict()

    # Calculate the averageShotLength for each video
    averageShotLength = {}
    for key in duration_dict.keys():
        averageShotLength[key] = duration_dict[key]/shots_dict[key]

    metadata["average_shot_length_seconds"] = metadata["video_id"].map(averageShotLength)
    return metadata


def calculateTimestamps(row, mid_timestamp=True):
    # Convert start time and end time to time objects
    start = time.fromisoformat(row["start_time"])
    end = time.fromisoformat(row["end_time"])
    if not mid_timestamp:
        return start, end

    # Convert time objects to total microseconds
    total_microseconds_start = (start.hour * 3600 + start.minute * 60 + start.second) * 10**6 + start.microsecond
    total_microseconds_end = (end.hour * 3600 + end.minute * 60 + end.second) * 10**6 + end.microsecond
    
    # Calculate the midpoint
    total_midpoint = (total_microseconds_start + total_microseconds_end) / 2
    
    # Calculate the components of the midpoint time
    hours, remainder = divmod(total_midpoint, 3600 * 10**6)
    minutes, remainder = divmod(remainder, 60 * 10**6)
    seconds, microseconds = divmod(remainder, 10**6)

    # Calculate the midpoint time
    midpoint_time = time(int(hours), int(minutes), int(seconds), int(microseconds))
    
    return start, end, midpoint_time


def setSceneIds(row, scene_ids):
    id = row["id"]
    end = row["end_timestamp"]
    # Add video id, the timestamp at the end of each scene and an index to define each scene to the scene scene_ids list
    scene_ids.append((id, end, row.name))

    return row.name


def assign(id, mid, scene_ids):
    iteration = 0  # Initiate counter of iterations
    # Iterate over each tuple in scene_ids
    for scene_id in scene_ids:
        # If id of the subtitle/transcription = id of scene and the midpoint of the subtitle/transcription is less than the endtime of the scene
        if id == scene_id[0] and mid <= scene_id[1]:
            output = scene_id[2]  # Add the scene index to output
            break
        # Handle that Whisper can sometimes hallucinate after video has ended (>duration)
        # Else if the scene id is not equal to the next iteration scene id (Next iteration is a new video) and the midpoint of the subtitle/transcription is greater than the endtime of the current scene
        elif scene_id[0] != scene_ids[iteration+1][0] and mid > scene_id[1]:
            # Then the current midpoint of the subtitle/transcription is greater than the duration of the video, and thereby is a hallucination
            output = np.nan  # Add nan to output
            break   
        
        iteration += 1  # If algorithm should move on and check the next scene, then increase the iteration counter

    return iteration, output


def assignSceneIds(row, scene_ids_for_transcriptions):
    id = row["id"]
    mid = row["mid_timestamp"]

    iteration, output = assign(id, mid, scene_ids_for_transcriptions)  # Call assign function
    del scene_ids_for_transcriptions[:iteration]  # Remove <iteration> number of scenes from the copy scene_ids, since they have are done
    
    return output


def fillStartAndEndSubtitleTimes(df):
    # Fill NaN-valued start-time values for subtitles/transcriptions with the previous end-time value, if id is the same
    df["start_time_transcript"].fillna(df.groupby("id")["end_time_transcript"].shift(), inplace=True)
    # Fill NaN-valued end-time values for subtitles/transcriptions with the subsequent start-time value, if id is the same
    df["end_time_transcript"].fillna(df.groupby("id")["start_time_transcript"].shift(-1), inplace=True)
    return df


def fillRemainingTimes(df):
    # Fill remaining start- and end-time values for subtitles/transcriptions with the start- and end-time from the scenes
    df["start_time_transcript"].fillna(df["start_time_scene"], inplace=True)
    df["end_time_transcript"].fillna(df["end_time_scene"], inplace=True)
    return df


def joinTranscriptsAndScenes(transcriptions, scenes):
    # Outer join transcriptions and scenes to keep all rows of both dataframes and drop afterwards irrelevant columns
    transcripts_scenes = pd.merge(transcriptions, scenes, on=["id", "scene_index"], how="outer", suffixes=("_transcript", "_scene"))
    transcripts_scenes = transcripts_scenes.drop(columns=["scene_index",
                                                "start_timestamp_transcript",
                                                "end_timestamp_transcript",
                                                "mid_timestamp",
                                                "start_timestamp_scene",
                                                "end_timestamp_scene"])

    transcripts_scenes = fillStartAndEndSubtitleTimes(transcripts_scenes)  # Fill start- and end-times with values from surrounding subtitles/transcriptions
    transcripts_scenes = fillRemainingTimes(transcripts_scenes)  # Fill remaining start- and end-times by interpolating using the scene start- and end-times
    transcripts_scenes["text"].fillna("", inplace=True)  # Fill NaN values of text with empty string

    return transcripts_scenes


def joinAll(transcripts_scenes, metadata):
    transcripts_scenes_meta = pd.merge(metadata, transcripts_scenes, left_on="video_id", right_on="id", how="outer")
    transcripts_scenes_meta = transcripts_scenes_meta.drop(columns=["id"])

    return transcripts_scenes_meta


def concatenateFullData(metadata, scenes, transcriptions, from_YouTube=False, save_dataframe=False):
    """
    This function creates a dataframe of the concatenation of metadata, scenes and transcriptions.
    --- args ---
    metadata: pandas.DataFrame
    scenes: pandas.DataFrame
    transcriptions: pandas.DataFrame

    --- kwargs ---
    from_YouTube: bool    |  default: False  # assumes Whisper transcriptions; change to True if YouTube subtitles are being used as input
    save_dataframe: bool  |  default: False

    --- output ---
    Outputs from function
    full_data: pandas.DataFrame

    Outputs to current directory (if save_dataframe=True)
    full_data: .csv
    """

    metadata = addAverageSpeakingRate(metadata, transcriptions)
    metadata = addAverageShotLength(metadata, scenes)

    # Create timestamps from the time columns in the dataframe, so that the midpoint can be calculated
    scenes[["start_timestamp", "end_timestamp"]] = scenes.apply(calculateTimestamps, mid_timestamp=False, axis=1, result_type="expand")
    transcriptions[["start_timestamp", "end_timestamp", "mid_timestamp"]] = transcriptions.apply(calculateTimestamps, axis=1, result_type="expand")

    # Sort the dataframes, except metadata, by video id
    scenes = scenes.sort_values(by=["id", "end_timestamp"]).reset_index(drop=True)
    transcriptions = transcriptions.sort_values(by=["id", "end_timestamp"]).reset_index(drop=True)


    scene_ids = []  # Initiate an empty list to store scene_ids
    scenes["scene_index"] = scenes.apply(setSceneIds, scene_ids=scene_ids, axis=1)  # Call the setSceneIds function on the scene_detections

    scene_ids_for_transcriptions = deepcopy(scene_ids)  # Make a copy of the scene_ids list to be used for iteration and assigning scene ids to transcriptions
    transcriptions["scene_index"] = transcriptions.apply(assignSceneIds, scene_ids_for_transcriptions=scene_ids_for_transcriptions, axis=1)  # Call the subtitle-variant of the assignSceneIds function on the subtitles
    if not from_YouTube:
        transcriptions = transcriptions.dropna(subset=["scene_index"]).reset_index(drop=True)  # Drop NaN value scene indexes from the Whisper transcriptions, since they are hallucinations

    # Join transcriptions and scenes
    transcripts_scenes = joinTranscriptsAndScenes(transcriptions, scenes)

    # Join (transcriptions and scenes) and metadata
    full_data = joinAll(transcripts_scenes, metadata)
    if save_dataframe:
        full_data.to_csv("full_data.csv", index=False)

    return full_data