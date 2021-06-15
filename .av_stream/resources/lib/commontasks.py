#!/bin/python

'''
Written by: Phantom Raspberry Blower
Date: 21-08-2017
Description: Common Tasks
'''

import os
import re
import time
from datetime import date
from configparser import ConfigParser

config_object = ConfigParser()

INVALID_FILENAME_CHARS = '\/:*?"<>|'

todays_date = date.today()

def get_settings(path="~/.av_stream/config.ini"):
    # Open config settings
    config_object.read(path)
    # Get the SETTINGS section
    settings = config_object['SETTINGS']
    settings_dict = {'audio_hardware': settings['audio_hardware'],
                     'audio_in_channels': settings['audio_in_channels'],
                     'audio_in_codec': settings['audio_in_codec'],
                     'audio_in_sample_rate': settings['audio_in_sample_rate'],
                     'audio_out_bitrate': settings['audio_out_bitrate'],
                     'audio_out_codec': settings['audio_out_codec'],
                     'audio_out_sample_rate': settings['audio_out_sample_rate'],
                     'broadcast_url': settings['broadcast_url'],
                     'broadcast_port': settings['broadcast_port'],
                     'enable_speaker': settings['enable_speaker'],
                     'facebook_url': settings['facebook_url'],
                     'facebook_stream_key': settings['facebook_stream_key'],
                     'gpio_led_pin': settings['gpio_led_pin'],
                     'gpio_switch_pin': settings['gpio_switch_pin'],
                     'gpio_spkr_pin': settings['gpio_spkr_pin'],
                     'itsoffset_seconds': settings['itsoffset_seconds'],
                     'itsoffset': settings['itsoffset'],
                     'last_updated': settings['last_updated'],
                     'metadata_comment': settings['metadata_comment'],
                     'metadata_copyright': settings['metadata_copyright'],
                     'metadata_description': settings['metadata_description'],
                     'metadata_title': settings['metadata_title'],
                     'metadata_year': settings['metadata_year'],
                     'startup_udp': settings['startup_udp'],
                     'update_interval_days': settings['update_interval_days'],
                     'update_os': settings['update_os'],
                     'upgrade_os': settings['upgrade_os'],
                     'video_in_bitrate': settings['video_in_bitrate'],
                     'video_in_codec': settings['video_in_codec'],
                     'video_in_frames_per_second': settings['video_in_frames_per_second'],
                     'video_in_intra_refresh_period': settings['video_in_intra_refresh_period'],
                     'video_in_height': settings['video_in_height'],
                     'video_in_width': settings['video_in_width'],
                     'video_out_codec': settings['video_out_codec'],
                     'video_out_overlay_text': settings['video_out_overlay_text']}
    return settings_dict


def save_settings(settings_dict, path='~/.av_stream/config.ini'):
    for item in settings_dict:
        config_object.set('SETTINGS', item, settings_dict[item])
    # Writing our configuration file to 'config.ini'
    with open(path, 'w') as configfile:
        config_object.write(configfile)


def regex_from_to(text, from_string, to_string, excluding=True):
    if excluding:
        r = re.search("(?i)" + from_string +
                      "([\S\s]+?)" +
                      to_string, text).group(1)
    else:
        r = re.search("(?i)(" +
                      from_string +
                      "[\S\s]+?" +
                      to_string +
                      ")", text).group(1)
    return r


def remove_from_list(list, file):
    index = find_list(list, file)
    if index >= 0:
        content = read_from_file(file)
        lines = content.split('\n')
        lines.pop(index)
        s = ''
        for line in lines:
            if len(line) > 0:
                s = s + line + '\n'
        write_to_file(file, s)


def find_list(query, search_file):
    try:
        content = read_from_file(search_file)
        lines = content.split('\n')
        index = lines.index(query)
        return index
    except:
        return -1


def add_to_list(list, file, refresh):
    if find_list(list, file) >= 0:
        return
    if os.path.isfile(file):
        content = read_from_file(file)
    else:
        content = ""

    lines = content.split('\n')
    s = '%s\n' % list
    for line in lines:
        if len(line) > 0:
            s = s + line + '\n'
    write_to_file(file, s)


def read_from_file(path):
    try:
        f = open(path, 'r')
        r = f.read()
        f.close()
        return str(r)
    except:
        return None


def write_to_file(path, content, append=False):
    try:
        if append:
            f = open(path, 'a')
        else:
            f = open(path, 'w')
        f.write(content)
        f.close()
        return True
    except:
        return False


def create_directory(dir_path, dir_name=None):
    if dir_name:
        dir_path = os.path.join(dir_path, dir_name)
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def create_file(dir_path, file_name=None):
    if file_name:
        file_path = os.path.join(dir_path, file_name)
    file_path = file_path.strip()
    if not os.path.exists(file_path):
        f = open(file_path, 'w')
        f.write('')
        f.close()
    return file_path


def remove_old_temp_files(file_path, days=28):
    '''
    Remove temp files from directory that are older
    than the specified number of days
    '''
    SECONDS_PER_HOUR = 3600
    current_time = time.time()
    for f in os.listdir(file_path):
        creation_time = os.path.getctime(file_path + '/' + f)
        if ((current_time - creation_time) // (24 * SECONDS_PER_HOUR)) >= int(days):
            os.unlink(file_path + '/' + f)


def validate_filename(filename):
    # Remove invalid characters from file name
    valid_filename = dict((ord(char), None) for char in INVALID_FILENAME_CHARS)
    file_name = filename.decode("ascii", errors="ignore")
    return file_name.translate(valid_filename)