import os
import pandas as pd
from IPython.display import clear_output
pd.set_option('display.max_colwidth', None)

def findvttFile(id, folder_path):
    # Find the .vtt file corresponding to the video id provided
    vtt_filename = [file for file in os.listdir(folder_path) if file.startswith(id) and file.endswith(".vtt")]
    return vtt_filename[0]


def addText(line, text, previous_was_timestamp):
    if previous_was_timestamp: # If there is no previous text for the given timestamp
        return line  # Just return the line
    else:  # If there is already text for the given timestamp
        return text + " " + line  # Add the new line to the previous text for that timestamp


def addLastLineToOutput(last_line, output):
    word_list = []  # Initiate a word list
    for word in last_line[1].split("<c> "):  # Iterate over each word in the last line, that has timestamps inside the text
        if word.split("<")[0] != "[&nbsp;__&nbsp;]":  # If "[&nbsp;__&nbsp;]" is detected as a word, then don't include it
            word_list.append(word.split("<")[0])  # Add each word, that is now separated from the timestamps that were inside the text, to the word list
    output[last_line[0]-1][2] += " " + " ".join(word_list)  # Join each word in the word list together to a string and add it to the last line where it belongs
    return output


def extractProvidedSubs(id, folder_path):
    # Open the downloaded vtt file, given folder path and video id
    with open(folder_path + findvttFile(id, folder_path), 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Add the .vtt output to lines
    output = []  # Initiate a new output list
    
    # Initiate variables to be used for loop below
    timestamp = False
    previous_was_timestamp = False
    time = ""
    text = ""
    # Iterate over each line
    for line in lines:
        if "-->" in line:  # If the line contains "-->", it is a timestamp
            timestamp = True
            previous_was_timestamp = True
            time = line[:-1]  # Set time variable equal to the timestamp
            continue  # and move on to the next line
        if timestamp:  # If the line is associated with a timestamp
            if line[-7:] == "&nbsp;\n":  # If the last part of the line is "&nbsp;\n"
                modified_line = line.replace("&nbsp;", "")  # Then remove "&nbsp;\n" from the line
                text = addText(modified_line[:-1], text, previous_was_timestamp)  # Add the line to text
                previous_was_timestamp = False
            elif line != "\n":  # If the line is not just "\n"
                text = addText(line[:-1], text, previous_was_timestamp)  # Add the line to text
                previous_was_timestamp = False
            elif line == "\n":  # If the line is just "\n", then it is the last line associated to the timestamp that the loop is at
                output.append([id, time, text])  # Then add id, timestamp and the associated text to the output list
                # Reset the loop variables
                timestamp = False
                previous_was_timestamp = False
                time = ""
                text = ""
    return output


def extractGeneratedSubs(id, folder_path):
    # Open the downloaded vtt file, given folder path and video id
    with open(folder_path + findvttFile(id, folder_path), 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Add the .vtt output to lines
    output = []  # Initiate a new output list
    
    # Initiate variables to be used for loop below
    counter = 0
    timestamp = False
    first_line = False
    second_line = False
    third_line = False
    save_text = False
    time = ""
    # Iterate over each line
    for line in lines:
        if "-->" in line:  # If the line contains "-->", it is a timestamp
            if time == "":  # If no timestamp is currently saved
                time = line[:-25]  # Save the timestamp
            timestamp = True
            first_line = True  # Specify that the next line will be the first line after timestamp
            continue  # and move on to the next line
        if timestamp:  # If the line is associated with a timestamp
            if first_line:  # If the loop is at the first line after timestamp
                if save_text:  # If the text should be saved with the associated timestamp that is saved
                    output.append([id, time, line[:-1].replace("[&nbsp;__&nbsp;] ", "")])  # Then add id, timestamp and the associated text (without [&nbsp;__&nbsp;]) to the output list
                    save_text = False  # Reset save_text variable
                    counter += 1  # Note that another output has been added
                first_line = False
                second_line = True  # Specify that the next line will be the second line after timestamp
            elif second_line:  # If the loop is at the second line after timestamp
                if line == " \n":  # If the text of the line is just " \n"
                    time = ""  # Then reset the time variable, as the timestamp should be updated
                else:  # If the text of the line is not just " \n"
                    save_text = True  # Then specify that the next text on the first line should be saved with the current saved timestamp
                    last_line = [counter, line[:-1]]  # Keep track of what and where the last second line was, to be added at the end. If not kept track of, then a line will be missing
                second_line = False
                third_line = True  # Specify that the next line will be the third line after timestamp (last line)
            elif third_line:  # If the loop is at the third line after timestamp
                # Skip, since it is always just "\n"
                third_line = False
                timestamp = False  # Set that there is no longer an associated timestamp to the text and start over
    output = addLastLineToOutput(last_line, output)  # Add the last second line to the last output, since it for some reason is never printed on the first line to be added normally
    return output


def extractTextFromvtt(row, folder_path, subtitle_list):
    id = row["video_id"]  # Find the video id of the video that has been inputted
    subtitles_are_provided = row["subtitles_are_provided"]  # Find whether or not that the subtitles are provided for the video
    
    if subtitles_are_provided:  # If subtitles are provided from YouTube / or if it is a transcription from Whisper
        provided_subs = extractProvidedSubs(id, folder_path)  # Use the extractProvidedSubs-function
        subtitle_list.append(provided_subs)
    if not subtitles_are_provided:  # If subtitles are auto-generated from YouTube
        generated_subs = extractGeneratedSubs(id, folder_path)  # Use the extractGeneratedSubs-function
        subtitle_list.append(generated_subs)


def createDataFrame(subtitle_list, from_YouTube=False):
    # Initiate lists for storing the data that will be used for creating the transcription dataframe
    video_id_list = []
    start_time_list = []
    end_time_list = []
    text_list = []

    # Iterate over transcriptions
    for transcription in subtitle_list:
        # Iterate over lines in transcriptions
        for line in transcription:
            # Add the data to the lists
            video_id_list.append(line[0])
            if line[1][:12][-1] == "-":  # If last character in start time is "-", then the hour is missing
                start_time_list.append("00:" + line[1][:9])
            else:
                start_time_list.append(line[1][:12])
            if line[1][17:][2] == ".":  # If the third character in end time is ".", then the hour is missing
                end_time_list.append("00:" + line[1][14:])
            else:
                end_time_list.append(line[1][17:])
            text_list.append(line[2])

    # Create the transcription dataframe from the lists that store the data
    transcriptions = pd.DataFrame({
        "id": video_id_list,
        "start_time": start_time_list,
        "end_time": end_time_list,
        "text": text_list
    })
    transcriptions["whisper_generated"] = not from_YouTube

    return transcriptions


def vttToTranscriptions(metadata, transcription_folder_path, from_YouTube=False, save_dataframe=True):
    """
    This function creates a dataframe of transcriptions from either the transcription files or the subtitle files.
    --- args ---
    metadata: pandas.DataFrame
    transcription_folder_path: string  # folder where transcription/subtitle files are located (.vtt)

    --- kwargs ---
    from_YouTube: bool    |  default: False  # assumes Whisper transcriptions; change to True if YouTube subtitles are being used as input
    save_dataframe: bool  |  default: True

    --- output ---
    Outputs from function
    transcriptions: pandas.DataFrame

    Outputs to current directory (if save_dataframe=True)
    transcriptions: .csv
    """

    video_ids = [file[:11] for file in os.listdir(transcription_folder_path) if file.endswith(".vtt")]

    # Get whether or not subtitles are provided for each YouTube video where subtitles have been downloaded
    subset_df = metadata[metadata["video_id"].isin(video_ids)][["video_id", "subtitles_are_provided"]].drop_duplicates(subset="video_id")
    if not from_YouTube:
        subset_df["subtitles_are_provided"] = True  # For Whisper Transcripts

    subtitle_list = []  # Initiate a list for storing the subtitles
    # Call the extractTextFromvtt-function on each row of the dataframe containing the downloaded video ids
    subset_df.apply(extractTextFromvtt, folder_path=transcription_folder_path, subtitle_list=subtitle_list, axis=1)
    clear_output()  # Call clear_output(), or else it will print None many times, since the extractTextFromvtt-function is not outputting anything

    transcriptions = createDataFrame(subtitle_list, from_YouTube=from_YouTube)
    if save_dataframe:
        transcriptions.to_csv("transcriptions.csv", index=False)

    return transcriptions