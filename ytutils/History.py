import pandas as pd
import os
import numpy as np
from datetime import date
import random

def concatenateDataForEpinion(folder_path, filename, dataframe):
    data = pd.read_json(folder_path + "/" + filename)  # read json files from folder path
    data["Participant ID"] = filename[:-5]
    output_data = pd.concat([dataframe, data], ignore_index=True)  # concatenate the json files
    return output_data

def concatenateData(folder_path, filename, dataframe):
    data = pd.read_json(folder_path + "/" + filename)  # read json files from folder path
    output_data = pd.concat([dataframe, data], ignore_index=True)  # concatenate the json files
    return output_data


def renameColumnsForEpinion(watch_history):
    new_column_names = {
        "title": "watched_title",
        "titleUrl": "url",
    }
    watch_history = watch_history.rename(columns=new_column_names)
    return watch_history


def renameColumns(search_history, watch_history):
    # Move descriptions column to last column
    descriptions = search_history["description"].tolist()
    search_history = search_history.drop("description", axis=1)
    search_history["description"] = descriptions

    # Then specify new column names for both DataFrames and perform the renaming
    new_column_names = {
        "title": "searched_title",
        "titleUrl": "url",
    }
    search_history = search_history.rename(columns=new_column_names)

    new_column_names = {
        "title": "watched_title",
        "titleUrl": "url",
    }
    watch_history = watch_history.rename(columns=new_column_names)

    return search_history, watch_history


def getIds(df):
    urls = df["url"].tolist()  # Turn urls-column into list
    x = len("https://www.youtube.com/watch?v=")  # Find length of the part of the youtube url before the video id
    id_list = [url[x:] if type(url) != type(np.nan) else url for url in urls]  # Remove the youtube url part and only keep the video id's. If url is NaN, then return NaN as video id
    return id_list


def loadEpinionData(folder_path, save_dataframe=False):
    """
    This function creates one watch history dataframe from the inputted watch-history json files.
    --- args ---
    folder_path: string  # folder where watch-history files are located (.json)

    --- kwargs ---
    save_dataframe: bool  |  default: False

    --- output ---
    Outputs from function
    watch_history: pandas.DataFrame

    Outputs to current directory (if save_dataframe=True)
    watch_history: .csv
    """
    files = [file for file in os.listdir(folder_path) if file.endswith(".json")]
    total_files = len(files)
    
    def load_json(file_path, i):
        print(f"\rProcessing file {i + 1}/{total_files}", end="")
        # Load data with only the required columns and add Participant ID
        data = pd.read_json(file_path)
        data = data.drop(columns=[col for col in ["subtitles", "description"] if col in data.columns])
        data["Participant ID"] = os.path.basename(file_path)[:-5]  # Add Participant ID based on filename
        return data

    # Use a generator expression to concatenate dataframes and process files in chunks
    dataframes = (load_json(os.path.join(folder_path, file), i) for i, file in enumerate(files))

    # Concatenate all DataFrames from the generator
    watch_history = pd.concat(dataframes, ignore_index=True)

    # Rename columns and add video ID
    watch_history = renameColumnsForEpinion(watch_history)
    watch_history["video_id"] = getIds(watch_history)

    # Save to CSV if needed
    if save_dataframe:
        watch_history.to_csv("watch_history.csv", index=False)
    
    print("\nProcessing complete.")

    return watch_history


def loadHistoryData(history_folder_path, save_dataframe=False):

    files = [file for file in os.listdir(history_folder_path) if file.endswith(".json")]  # Get all .json files in the specified history_folder_path as a list

    search_history = pd.DataFrame()
    watch_history = pd.DataFrame()  # creates 2 new dataframe, one for search history and one for watch history
    for file in files:
        # Iterate through the filenames and check the following
        if file[0].lower() == "s":
            search_history = concatenateData(history_folder_path, file, search_history)  # If file starts with an "s", use the concatenateData()-function, to add it to the search history dataframe
        if file[0].lower() == "w":
            watch_history = concatenateData(history_folder_path, file, watch_history)  # If file starts with a "w", use the concatenateData()-function, to add it to the watch history dataframe

    # Rename some of the columns in the two dataframes
    search_history, watch_history = renameColumns(search_history, watch_history)

    # Add a search query column to the search history DataFrame using the getIds()-function
    search_history["search_query"] = getIds(search_history)

    # Add video info to the watch_history DataFrame using the add_video_info()-function
    watch_history["video_id"] = getIds(watch_history)
    watch_history = watch_history.drop(["subtitles", "description"], axis=1)

    if save_dataframe:
        search_history.to_csv("search_history.csv", index=False)
        watch_history.to_csv("watch_history.csv", index=False)

    return search_history, watch_history

def loadNewData(existing_dataframe, folder_path ,save_dataframe=True):
    # load the ids from exiting dataframe and add .json to get the file names 
    old_ids = pd.unique(existing_dataframe["Participant ID"])
    old_jsons = [id + ".json" for id in old_ids]

    # Get all new .json files in the specified history_folder_path as a list
    files = [file for file in os.listdir(folder_path) if file.endswith(".json") and file not in old_jsons] 

    watch_history = pd.DataFrame()
    
    for file in files:
        watch_history = concatenateDataForEpinion(folder_path, file, watch_history) # use the concatenateData()-function, to add it to the watch history dataframe

    # Rename some of the columns in the two dataframes
    watch_history = renameColumnsForEpinion(watch_history)

    # Add video info to the watch_history DataFrame using the add_video_info()-function
    watch_history["video_id"] = getIds(watch_history)
    watch_history = watch_history.drop(["subtitles", "description"], axis=1)

    # Add a column for added date 
    watch_history["added_date"] = pd.Timestamp(date.today())

    # concatinate the old and new dataframe
    watch_history = pd.concat([existing_dataframe, watch_history], ignore_index = True)
    
    if save_dataframe:
        # Save new dataframe with time-stamp
        watch_history.to_csv("Saved_dataframes/" + date.today().strftime('%Y-%m-%d') + "-watch_history.csv", index=False)

    return watch_history


def clean_dataframe(dataframe):
    # remove videos that are NaN
    df = dataframe[dataframe["video_id"].notna()]
    # Only keep videos that are not ads
    df = df[df["details"].isna()]
    # Remove music videos (they have url >43)
    df = df[df["url"].apply(str).apply(len) <= 43]
    
    return df

def sampleVids(dataframe, sample_size=10, random_state=42):
    # make it reproducible by setting seed
    random.seed(random_state)
    
    URL_ = set()
    URLs = list()
    
    # remove videos that are ads or that do not exist
    df = clean_dataframe(dataframe)

    # find unique dates
    dates = [x for x in pd.unique(df["Incorporation Date"])]
    
    for date in sorted(dates):
        # find dates that match "date"
        date_df = df[df["Incorporation Date"]==date]

        # find all IDs added at this date
        ids = [x for x in pd.unique(date_df["Participant ID"])]

        for id in ids:
            # find IDs that matches "id"
            id_df = date_df[date_df["Participant ID"] == id]
            urls = pd.unique(id_df["url"]).tolist()

            if len(urls) < sample_size:
                print(f"Skipping Participant ID {id} on date {date} due to insufficient URLs ({len(urls)} available).")
                continue  # Skip to the next participant ID


            for i in range(100000):
                sample = random.sample(urls, sample_size)
                sample_set = set(sample)
                
                if len(URL_&sample_set) == 0:
                    URL_.update(sample)
                    URLs.append((id,sample))
                    break

                if i==100000-1:
                    print("could not find unique samples for"+ id)          
    
    return URLs, URL_ 
    