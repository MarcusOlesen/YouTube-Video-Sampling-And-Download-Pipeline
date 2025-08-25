import pandas as pd
import os
import numpy as np

def mergeWatchHistoryWithMetadata(watch_history, data):
    metadata = pd.merge(watch_history, data, on="video_id", how="left")
    return metadata


def getMetadata(watch_history, info_folder_path, save_dataframe=True):
    """
    This function creates a dataframe of metadata from the downloaded info files and combines it with the watch history dataframe.
    --- args ---
    watch_history: pandas.DataFrame
    info_folder_path: string  # folder where info files are located (.json)

    --- kwargs ---
    save_dataframe: bool  |  default: True

    --- output ---
    Outputs from function
    metadata: pandas.DataFrame

    Outputs to current directory (if save_dataframe=True)
    metadata: .csv
    """
    files = [file for file in os.listdir(info_folder_path) if file.endswith(".info.json")]
    
    # Initiate empty lists for storing file info
    ids = []
    titles = []
    upload_dates = []
    channel_ids = []
    channel_titles = []
    channel_subscriber_counts = []
    channel_is_verifieds = []
    video_view_counts = []
    video_like_counts = []
    video_comment_counts = []
    duration_secondss = []
    descriptions = []
    tagss = []
    categoriess = []
    subtitles_are_provideds = []
    subtitless = []
    age_limits = []
    is_lives = []
    was_lives = []
    privacy_settings = []
    fpss = []
    audio_sampling_rates = []
    audio_channelss = []
    heights = []
    widths = []
    resolutions = []
    dynamic_ranges = []
    aspect_ratios = []

    # Iterate over info files and add their contents to the lists
    for file in files:
        file_info = pd.read_json(info_folder_path + file)
        ids.append(file_info["id"][0])
        titles.append(file_info["title"][0])
        upload_dates.append(file_info["upload_date"][0])
        channel_ids.append(file_info["channel_id"][0])
        channel_titles.append(file_info["channel"][0])
        try:
            channel_subscriber_counts.append(file_info["channel_follower_count"][0])
        except KeyError:
            channel_subscriber_counts.append(0)
        try:
            channel_is_verifieds.append(bool(file_info["channel_is_verified"][0]))
        except KeyError:
            channel_is_verifieds.append(False)
        try:
            video_view_counts.append(file_info["view_count"][0])
        except KeyError:
            video_view_counts.append(0)
        try:
            video_like_counts.append(file_info["like_count"][0])
        except KeyError:
            video_like_counts.append(0)
        try:
            video_comment_counts.append(file_info["comment_count"][0])
        except KeyError:
            video_comment_counts.append(0)
        duration_secondss.append(file_info["duration"][0])
        descriptions.append(file_info["description"][0])
        tagss.append(file_info["tags"][0])
        categoriess.append(file_info["categories"][0])
        subtitles_are_provideds.append(file_info["subtitles_are_provided"][0])
        age_limits.append(file_info["age_limit"][0])
        is_lives.append(file_info["is_live"][0])
        was_lives.append(file_info["was_live"][0])
        privacy_settings.append(file_info["availability"][0])
        fpss.append(file_info["fps"][0])
        try:
            audio_sampling_rates.append(file_info["asr"][0])
        except KeyError:
            audio_sampling_rates.append(np.nan)
        try:
            audio_channelss.append(file_info["audio_channels"][0])
        except KeyError:
            audio_channelss.append(np.nan)
        heights.append(file_info["height"][0])
        widths.append(file_info["width"][0])
        resolutions.append(file_info["format_note"][0])
        dynamic_ranges.append(file_info["dynamic_range"][0])
        aspect_ratios.append(file_info["aspect_ratio"][0])

    # Create a metadata dataframe from the lists with the info file content
    data = pd.DataFrame({
        "video_id": ids,
        "title": titles,
        "upload_date": upload_dates,
        "channel_id": channel_ids,
        "channel_title": channel_titles,
        "channel_subscriber_count": channel_subscriber_counts,
        "channel_is_verified": channel_is_verifieds,
        "video_view_count": video_view_counts,
        "video_like_count": video_like_counts,
        "video_comment_count": video_comment_counts,
        "duration_seconds": duration_secondss,
        "description": descriptions,
        "tags": tagss,
        "categories": categoriess,
        "subtitles_are_provided": subtitles_are_provideds,
        "age_limit": age_limits,
        "is_live": is_lives,
        "was_live": was_lives,
        "privacy_setting": privacy_settings,
        "fps": fpss,
        "audio_sampling_rate": audio_sampling_rates,
        "audio_channels": audio_channelss,
        "height": heights,
        "width": widths,
        "resolution": resolutions,
        "dynamic_range": dynamic_ranges,
        "aspect_ratio": aspect_ratios
    })

    metadata = mergeWatchHistoryWithMetadata(watch_history, data)
    if save_dataframe:
        metadata.to_csv("metadata.csv", index=False)

    return metadata