#!/bin/python

'''
Written by: Phantom Raspberry Blower
Date: 21-08-2017
Description: Common Tasks
'''

import os
import re
import time
import logging
from datetime import date
from configparser import ConfigParser

config_object = ConfigParser()

INVALID_FILENAME_CHARS = '\/:*?"<>|'

todays_date = date.today()

WORK_DIR = '/home/pi/.av_stream'

settings_dict = {}

logging.basicConfig(format='%(asctime)s - %(message)s',
                    filename='%s/avss.log' % WORK_DIR,
                    level=logging.DEBUG)


def check_for_updates(work_dir, msg):
    logging.info(msg)
    response = os.popen('python %s/updateWorker.py' % work_dir).read()
    settings_dict = get_settings(work_dir + '/config.ini')
    if settings_dict['update_os'] == 'True':
        os.popen('sudo apt-get update')
        logging.info('OS updated manually')
    if settings_dict['upgrade_os'] == 'True':
        os.popen('sudo apt-get upgrade')
        logging.info('OS upgraded manually')
    settings_dict.update({'last_updated':
                          date.today().strftime('%d/%m/%Y')})
    save_settings(settings_dict, work_dir + '/config.ini')


def get_settings(path="~/.av_stream/config.ini"):
    global settings_dict
    # Open config settings
    config_object.read(path)
    # Get the SETTINGS section
    for key, value in config_object.items('SETTINGS'):
        settings_dict.update({key: value})
    return settings_dict


def save_settings(settings_dict, path='~/.av_stream/config.ini'):
    for item in settings_dict:
        config_object.set('SETTINGS', item, settings_dict[item])
    # Writing our configuration file to 'config.ini'
    with open(path, 'w') as configfile:
        config_object.write(configfile)
    logging.info('Config Settings Saved')


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
