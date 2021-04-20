#!/usr/bin/env python3

import json
import pandas as pd
import datetime as dt
from os import system
from sys import argv

get_hist = False
refresh_channel_info = False

combined_data_url = 'https://github.com/onecalfman/youtube_trends_stats_de/blob/main/combined_data.json?raw=true'
combined_data = pd.read_json(combined_data_url)

for arg in argv:
    if arg == 'channel_hist':
        get_hist = True
    elif arg == 'refresh_channel_info':
        refresh_channel_info = True

api_key = '' # needs api key here

from apiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=api_key)

time_string =  str(dt.datetime.now()).replace(' ', '_')[:-7]
time =  pd.to_datetime(dt.datetime.now())
region = 'DE'

trends_snippet = youtube.videos().list(part='snippet', chart='mostPopular', regionCode='DE', maxResults=50)
trends_stats = youtube.videos().list(part='statistics', chart='mostPopular', regionCode='DE', maxResults=50)
trends_snippet_res = trends_snippet.execute()
trends_stats_res = trends_stats.execute()

trends_snippet = pd.DataFrame(trends_snippet_res['items'])[['id', 'snippet']]
trends_stats = pd.DataFrame(trends_stats_res['items'])[['id', 'statistics']]

keys_snippet = ['title', 'description', 'publishedAt','channelTitle', 'channelId', 'categoryId', 'tags']
keys_stats = ['viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'favoriteCount']
keys_int = ['categoryId', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'favoriteCount', 'channelViewCount', 'subscriberCount', 'videoCount']

def extractor(x, key):
    try:
        return x[key]
    except:
        if key == 'tags':
            return []
        elif key == 'likeCount' or key == 'dislikeCount':
            return 0
        else:
            return pd.NA

trends = pd.DataFrame()

trends['id'] = trends_stats['id']
for key in keys_snippet:
    trends[key] = trends_snippet['snippet'].map(lambda x : extractor(x, key))
    
for key in keys_stats:
    trends[key] = trends_stats['statistics'].map(lambda x : extractor(x, key))

channels = {}
for channel_id in trends['channelId']:
    if refresh_channel_info or not channel_id in combined_data.channelId:
        channel_info = youtube.channels().list(part='statistics', id=channel_id, maxResults=1)
        channel_info = channel_info.execute()
        channels[channel_id] = channel_info['items'][0]['statistics']
        channel_info = youtube.channels().list(part='snippet', id=channel_id, maxResults=1)
        channel_info = channel_info.execute()
        channels[channel_id]['channelPublishedAt'] = channel_info['items'][0]['snippet']['publishedAt']
        try:
            channels[channel_id]['customUrl'] = channel_info['items'][0]['snippet']['customUrl']
        except:
            channels[channel_id]['customUrl'] = ''
        channels[channel_id]['channelDescription'] = channel_info['items'][0]['snippet']['description']
    else:
        channel_keys = ['channelViewCount', 'subscriberCount', 'hiddenSubscriberCount', 'videoCount', 'channelPublishedAt', 'customUrl', 'channelDescription']
        source = combined_data.loc[combined_data.channelId == channel_id].sort_values(by='publishedAt').iloc[-1]
        for key in channel_keys:
            channels[channel_id][key] = source[key]
    
    if get_hist:
        channel_content = youtube.channels().list(part='contentDetails', id=channel_id, maxResults=50)
        channel_content = channel_content.execute()

        uploads_playlist_id = channel_content['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        channels[channel_id]['last_50_videos'] = []
        playlist = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=50)
        try:
            playlist = playlist.execute()
            ids = []
        
            for item in playlist['items']:
                video_id = item['snippet']['resourceId']['videoId']
                vid = youtube.videos().list(part='statistics', id=video_id, maxResults=1)
                vid = vid.execute()
                vid_dict = vid['items'][0]['statistics']
                vid_dict['id'] = vid['items'][0]['id']
                channels[channel_id]['last_50_videos'].append(vid_dict)
        except:
            print('last uploads failed')


channels = pd.DataFrame(channels).transpose().rename(columns = {'viewCount': 'channelViewCount'}).fillna('0')
channels['channelId'] = channels.index
trends = pd.merge(trends, channels, on='channelId')

for key in keys_int:
    trends[key] = trends[key].fillna(0).astype(int)

trends.index += 1
trends['rank'] = trends.index

trends.publishedAt = trends.publishedAt.map(lambda x : pd.to_datetime(x))
trends.channelPublishedAt = trends.channelPublishedAt.map(lambda x : pd.to_datetime(x))
trends['dataTakenAt'] = time

print('df len: ' + str(trends.size))

folder = 'youtube_trends_stats_de/single_'
file_format = 'json'
trends.to_json(folder + file_format + '/' + time_string + '.' + file_format)
file_format = 'csv'
trends.to_csv(folder + file_format + '/' + time_string + '.' + file_format)

system('youtube_trends_commit')
