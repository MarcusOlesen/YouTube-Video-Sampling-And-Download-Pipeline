import os
import pandas as pd
#import whisper
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def transcribeVideos(video_folder_path, output_folder_path, model_size="tiny", number_to_transcribe=False):
    """
    This function creates transcriptions from the video files.
    --- args ---
    video_folder_path: string  # folder where video files are located (.mp4)
    output_folder_path: string

    --- kwargs ---
    model_size: string         |  default: "tiny"
    number_to_transcribe: int  |  default: All unique videos

    --- output ---
    Outputs to "output_folder_path" directory
    transcriptions: .vtt

    ## model_size options ##
    model_size="large"    (Best quality)
    model_size="medium"
    model_size="small"
    model_size="base"
    model_size="tiny"  (Best efficiency)
    """

    # Get video ids for the downloaded .mp4 files
    video_ids = [file[:11] for file in os.listdir(video_folder_path) if file.endswith(".mp4")]

    # Get number of videos to transcribe (primarily for testing)
    if number_to_transcribe:
        video_ids = video_ids[:number_to_transcribe]

    # Load whisper model
    model = whisper.load_model(model_size)

    # Create output folder if it doesn't exist already
    os.makedirs(output_folder_path)

    for id in video_ids:
        result = model.transcribe(video_folder_path + id + ".mp4")  # Transcribe the video

        # Save as a VTT file
        vtt_writer = whisper.utils.get_writer("vtt", output_folder_path)
        vtt_writer(result, id + ".vtt")