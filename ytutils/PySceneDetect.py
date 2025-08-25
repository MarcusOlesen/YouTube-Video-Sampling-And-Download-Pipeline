from scenedetect import detect, ContentDetector
from scenedetect.frame_timecode import FrameTimecode
import cv2
import os
import pandas as pd
from IPython.display import clear_output

def findmp4File(id, folder_path):
    # Find the .vtt file corresponding to the video id provided
    mp4_filename = [file for file in os.listdir(folder_path) if file.startswith(id) and file.endswith(".mp4")]
    return mp4_filename[0]


def findScenes(id, duration, fps, folder_path):
    try:
        # Detect the scenes from the downloaded .mp4 file, using the detect-function
        scenes = detect(folder_path + findmp4File(id, folder_path), ContentDetector())  # Each scene is a tuple of (start_frame, end_frame)
        # If there are no scenes detected, then return the video as one scene
        if len(scenes) == 0:
            start = FrameTimecode(timecode=0, fps=fps)
            end = FrameTimecode(timecode=int(duration*fps), fps=fps)
            scenes = [(start, end)]
    # Catch error related to corrupt video
    except:
        start = FrameTimecode(timecode=0, fps=fps)
        end = FrameTimecode(timecode=int(duration*fps), fps=fps)
        scenes = [(start, end)]
    return scenes


def extractScenesFrommp4(row, folder_path, scene_list):
    id = row["video_id"]  # Find the video id of the video that has been inputted
    duration = row["duration_seconds"]  # Find the duration of the video that has been inputted
    fps = row["fps"]  # Find the fps of the video that has been inputted
    scene_list.append([id, findScenes(id, duration, fps, folder_path)])  # Add the detected scenes from the find_scenes-function to the scenes list


def createDataFrame(scene_list):
    video_id_list = []
    start_time_list = []
    end_time_list = []
    start_frame_num_list = []
    end_frame_num_list = []

    for scene in scene_list:
        for frame in scene[1]:
            video_id_list.append(scene[0])
            start_time_list.append(frame[0].get_timecode())
            end_time_list.append(frame[1].get_timecode())
            start_frame_num_list.append(frame[0].frame_num)
            end_frame_num_list.append(frame[1].frame_num)

    # Create the transcription dataframe from the lists that store the data
    scenes = pd.DataFrame({
        "id": video_id_list,
        "start_time": start_time_list,
        "end_time": end_time_list,
        "start_frame_num": start_frame_num_list,
        "end_frame_num": end_frame_num_list
    })

    return scenes


def mp4ToScenes(metadata, video_folder_path, save_dataframe=True):
    """
    This function creates a dataframe of scenes from the video files.
    --- args ---
    metadata: pandas.DataFrame
    video_folder_path: string  # folder where video files are located (.mp4)

    --- kwargs ---
    save_dataframe: bool  |  default: True

    --- output ---
    Outputs from function
    scenes: pandas.DataFrame

    Outputs to current directory (if save_dataframe=True)
    scenes: .csv
    """

    video_ids = [file[:11] for file in os.listdir(video_folder_path) if file.endswith(".mp4")]

    subset_df = metadata[metadata["video_id"].isin(video_ids)][["video_id", "duration_seconds", "fps"]].drop_duplicates(subset="video_id")

    scene_list = []  # Initiate a list for storing the scenes
    # Call the extractScenesFrommp4-function on each row of the dataframe containing the downloaded video ids
    subset_df.apply(extractScenesFrommp4, folder_path=video_folder_path, scene_list=scene_list, axis=1)
    clear_output()  # Call clear_output(), or else it will print None many times, since the extractScenesFrommp4-function is not outputting anything

    scenes = createDataFrame(scene_list)
    if save_dataframe:
        scenes.to_csv("scenes.csv", index=False)

    return scenes