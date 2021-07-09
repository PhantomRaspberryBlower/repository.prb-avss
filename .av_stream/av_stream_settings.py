#!/usr/bin/env python3

'''
Written by: Phantom Raspberry Blower
Date: 21-04-2021
Description: Creates a web page on port 8000 for changing settings needed to
stream video & audio to a live streaming providers:- facebook, periscope,
twitch, ustream, vimeo and youtube or broadcast via udp on port 4569.
'''

import io
import picamera
import logging
import socketserver
import os
import datetime as dt
import time
import math
from http import server
from threading import Condition
from resources.lib.systeminfo import SystemInfo
from resources.lib import commontasks

si = SystemInfo()
audio_codecs = ['aac', 'mp2', 'mp3']
audio_bitrates = ['32k', '64k', '96k', '128k']
audio_sample_rates = ['44100', '48000']
logging_levels = ['NONE' ,'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
offset_types = ['none', 'audio', 'video']
update_intervals = ['1', '7', '30']
video_codecs = ['flv', 'mp4', 'mpegts']
video_fps = ['15', '20', '25', '30']
video_image_automatic_white_balances = ['off', 'auto', 'cloudy', 'flash',
                                        'fluorescent', 'horizon','incandescent',
                                        'sunlight', 'shade', 'tungsten']
video_image_dynamic_range_compressions = ['off', 'low', 'med', 'high']
video_image_effects = ['none', 'blur', 'cartoon', 'colorbalance', 'colorswap',
                       'colorpoint', 'deinterlace1', 'deinterlace2', 'denoise',
                       'emboss', 'film', 'gpen', 'hatch', 'negative', 'oilpaint',
                       'pastel', 'posterise', 'saturation', 'sketch', 'solarize',
                       'watercolor', 'washedout']
video_image_exposures = ['auto', 'antishake', 'backlight', 'beach', 'fireworks',
                         'fixedfps', 'night', 'nightpreview', 'spotlight',
                         'sports', 'snow', 'verylong']
video_image_flicker_avoidances = ['off', 'auto', '50hz', '60hz']
video_image_profiles = ['baseline', 'main', 'high']
video_image_rotations = ['0', '90', '180', '270']
video_out_overlay_text_sizes = ['18', '20', '22', '24', '26', '28', '30', '32',
                                '34', '36', '38', '40', '42', '44', '46', '48',
                                '50', '52', '54', '56', '58', '60', '62', '64']
video_resolutions = ['480x270','960x540', '1280x720', '1920x1080']
settings_dict = {}
hidden_form_elements = '<br>'

PORT_NUMBER = 8000 # Can't be port 80 unless run as root
WORK_DIR = os.path.abspath(os.path.dirname(__file__))
HTML_DIR = WORK_DIR + '/resources/templates'

logging.basicConfig(format='%(asctime)s - %(message)s',
                    filename='%s/avss.log' % WORK_DIR,
                    level=logging.DEBUG)

def get_settings():
    global settings_dict
    settings_dict = commontasks.get_settings(WORK_DIR + '/config.ini')

get_settings()

if settings_dict['logging_level'] == 'NONE':
    logging.disable(level=logging.CRITICAL)
elif settings_dict['logging_level'] == 'DEBUG':
    logging.getLogger().setLevel(logging.DEBUG)
elif settings_dict['logging_level'] == 'INFO':
    logging.getLogger().setLevel(logging.INFO)
elif settings_dict['logging_level'] == 'WARNING':
    logging.getLogger().setLevel(logging.WARNING)
elif settings_dict['logging_level'] == 'ERROR':
    logging.getLogger().setLevel(logging.ERROR)
elif settings_dict['logging_level'] == 'CRITICAL':
    logging.getLogger().setLevel(logging.CRITICAL)

def set_settings():
    global settings_dict
    commontasks.save_settings(settings_dict, WORK_DIR + '/config.ini')


def options(opt, lst):
  txt = ''
  for item in lst:
    if opt == item:
      txt += '\n  <option selected="selected" value="' + item + '">' + item + '</option>'
    else:
      txt += '\n  <option value="' + item + '">' + item + '</option>'
  return txt


def INDEX_PAGE():
    checkbox_items = ['enable_speaker', 'startup_udp', 'update_os', 'upgrade_os',
                      'stream_to_facebook', 'stream_to_periscope', 'stream_to_twitch',
                      'stream_to_ustream', 'stream_to_vimeo', 'stream_to_youtube',
                      'video_out_overlay_bg_color_enabled', 'video_image_horizontal_flip',
                      'video_image_vertical_flip', 'video_stabilisation']
    audio_out_codec_txt = options(settings_dict['audio_out_codec'],audio_codecs)
    audio_out_bitrate_txt = options(settings_dict['audio_out_bitrate'], audio_bitrates)
    audio_out_sample_rate_txt = options(settings_dict['audio_out_sample_rate'], audio_sample_rates)
    video_in_frames_per_second_txt = options(settings_dict['video_in_frames_per_second'], video_fps)
    video_resolution_txt = options(settings_dict['video_in_width'] + "x" + settings_dict['video_in_height'], video_resolutions)
    video_out_codec_txt = options(settings_dict['video_out_codec'], video_codecs)
    itsoffset_txt = options(settings_dict['itsoffset'], offset_types)
    update_interval_days_txt = options(settings_dict['update_interval_days'], update_intervals)
    logging_level_txt = options(settings_dict['logging_level'], logging_levels)
    video_out_overlay_text_size_txt = options(settings_dict['video_out_overlay_text_size'], video_out_overlay_text_sizes)
    video_image_rotation_txt = options(settings_dict['video_image_rotation'], video_image_rotations)
    video_image_exposure_txt = options(settings_dict['video_image_exposure'], video_image_exposures)
    video_image_profile_txt = options(settings_dict['video_image_profile'], video_image_profiles)
    video_image_automatic_white_balance_txt = options(settings_dict['video_image_automatic_white_balance'], video_image_automatic_white_balances)
    video_image_dynamic_range_compression_txt = options(settings_dict['video_image_dynamic_range_compression'], video_image_dynamic_range_compressions)
    video_image_flicker_avoidance_txt = options(settings_dict['video_image_flicker_avoidance'], video_image_flicker_avoidances)
    video_image_effect_txt = options(settings_dict['video_image_effect'], video_image_effects)
    hostname = si.hostname
    enable_speaker_txt = ''
    startup_udp_txt = ''
    update_os_txt = ''
    upgrade_os_txt = ''
    stream_to_facebook_txt = ''
    stream_to_periscope_txt = ''
    stream_to_twitch_txt = ''
    stream_to_ustream_txt = ''
    stream_to_vimeo_txt = ''
    stream_to_youtube_txt = ''
    video_out_overlay_bg_color_enabled_txt = ''
    video_image_horizontal_flip_txt = ''
    video_image_vertical_flip_txt = ''
    video_stabilisation_txt = ''
    disable_form_elements = ''
    disable_background_color = ''
    # HTML form checkboxes
    ldic=locals()
    for item in checkbox_items:
        if settings_dict[item] == 'True':
            exec("%s_txt = '%s'" % (item,' checked="True"'), globals(), ldic)
            if item == 'startup_udp':
                disable_form_elements = 'disabled'
        elif settings_dict[item] == 'False':
            if item == 'video_out_overlay_bg_color_enabled':
                disable_background_color = 'disabled'
    enable_speaker_txt = ldic['enable_speaker_txt']
    startup_udp_txt = ldic['startup_udp_txt']
    update_os_txt = ldic['update_os_txt']
    upgrade_os_txt = ldic['upgrade_os_txt']
    stream_to_facebook_txt = ldic['stream_to_facebook_txt']
    stream_to_periscope_txt = ldic['stream_to_periscope_txt']
    stream_to_twitch_txt = ldic['stream_to_twitch_txt']
    stream_to_ustream_txt = ldic['stream_to_ustream_txt']
    stream_to_vimeo_txt = ldic['stream_to_vimeo_txt']
    stream_to_youtube_txt = ldic['stream_to_youtube_txt']
    video_out_overlay_bg_color_enabled_txt = ldic['video_out_overlay_bg_color_enabled_txt']
    video_image_horizontal_flip_txt = ldic['video_image_horizontal_flip_txt']
    video_image_vertical_flip_txt = ldic['video_image_vertical_flip_txt']
    video_stabilisation_txt = ldic['video_stabilisation_txt']
    tags = {"<!--hidden-->": hidden_form_elements,
            "<!--startup_enabled-->": disable_form_elements,
            "<!--startup_bg_color_enabled-->": disable_background_color,
            "<!--audio_out_codec_txt-->": audio_out_codec_txt,
            "<!--audio_out_bitrate_txt-->": audio_out_bitrate_txt,
            "<!--audio_out_sample_rate_txt-->": audio_out_sample_rate_txt,
            "<!--enable_speaker_txt-->": enable_speaker_txt,
            "<!--facebook_url-->": settings_dict['facebook_url'],
            "<!--facebook_stream_key-->": settings_dict['facebook_stream_key'],
            "<!--itsoffset_seconds-->": settings_dict['itsoffset_seconds'],
            "<!--itsoffset_txt-->": itsoffset_txt,
            "<!--metadata_title-->": settings_dict['metadata_title'],
            "<!--metadata_year-->": settings_dict['metadata_year'],
            "<!--metadata_description-->": settings_dict['metadata_description'],
            "<!--logging_level_txt-->": logging_level_txt,
            "<!--periscope_url-->": settings_dict['periscope_url'],
            "<!--periscope_stream_key-->": settings_dict['periscope_stream_key'],
            "<!--startup_udp_txt-->": startup_udp_txt,
            "<!--stream_to_facebook_txt-->": stream_to_facebook_txt,
            "<!--stream_to_periscope_txt-->": stream_to_periscope_txt,
            "<!--stream_to_twitch_txt-->": stream_to_twitch_txt,
            "<!--stream_to_ustream_txt-->": stream_to_ustream_txt,
            "<!--stream_to_vimeo_txt-->": stream_to_vimeo_txt,
            "<!--stream_to_youtube_txt-->": stream_to_youtube_txt,
            "<!--twitch_url-->": settings_dict['twitch_url'],
            "<!--twitch_stream_key-->": settings_dict['twitch_stream_key'],
            "<!--update_os_txt-->": update_os_txt,
            "<!--upgrade_os_txt-->": upgrade_os_txt,
            "<!--update_interval_days_txt": update_interval_days_txt,
            "<!--ustream_url-->": settings_dict['ustream_url'],
            "<!--ustream_stream_key-->": settings_dict['ustream_stream_key'],
            "<!--video_in_bitrate-->": settings_dict['video_in_bitrate'],
            "<!--video_in_frames_per_second_txt-->": video_in_frames_per_second_txt,
            "<!--video_image_automatic_white_balance_txt-->": video_image_automatic_white_balance_txt,
            "<!--video_image_brightness-->": settings_dict['video_image_brightness'],
            "<!--video_image_contrast-->": settings_dict['video_image_contrast'],
            "<!--video_image_dynamic_range_compression_txt-->": video_image_dynamic_range_compression_txt,
            "<!--video_image_effect_txt-->": video_image_effect_txt,
            "<!--video_image_exposure_txt-->": video_image_exposure_txt,
            "<!--video_image_flicker_avoidance_txt-->": video_image_flicker_avoidance_txt,
            "<!--video_image_horizontal_flip_txt-->": video_image_horizontal_flip_txt,
            "<!--video_image_profile_txt-->": video_image_profile_txt,
            "<!--video_image_rotation_txt-->": video_image_rotation_txt,
            "<!--video_image_saturation-->": settings_dict['video_image_saturation'],
            "<!--video_image_sharpness-->": settings_dict['video_image_sharpness'],
            "<!--video_image_vertical_flip_txt-->": video_image_vertical_flip_txt,
            "<!--video_out_codec_txt-->": video_out_codec_txt,
            "<!--video_out_overlay_text-->": settings_dict['video_out_overlay_text'].replace('"', "'").replace('~', '%'),
            "<!--video_out_overlay_text_size_txt-->": video_out_overlay_text_size_txt,
            "<!--video_out_overlay_text_color-->": settings_dict['video_out_overlay_text_color'],
            "<!--video_out_overlay_bg_color_enabled_txt-->": video_out_overlay_bg_color_enabled_txt,
            "<!--video_out_overlay_bg_color-->": settings_dict['video_out_overlay_bg_color'],
            "<!--video_resolution_txt-->": video_resolution_txt,
            "<!--video_stabilisation_txt-->": video_stabilisation_txt,
            "<!--vimeo_url-->": settings_dict['vimeo_url'],
            "<!--vimeo_stream_key-->": settings_dict['vimeo_stream_key'],
            "<!--youtube_url-->": settings_dict['youtube_url'],
            "<!--youtube_stream_key-->": settings_dict['youtube_stream_key']}
    f = open(HTML_DIR + "/index.html", "r")
    page = f.read()
    for tag, cmd in tags.items():
        page = page.replace(tag, cmd)
    return page


def HELP_PAGE():
    f = open(HTML_DIR + "/help.html", "r")
    page = f.read()
    return page


def INFO_PAGE():
    f = open(HTML_DIR + "/info.html", "r")
    page = f.read()
    disk_info_txt = '<b>Storage:</b>'
    for item in si.disk_info:
        disk_info_txt = disk_info_txt + ('\n  Path: %s\n'
                                         '  Total: %sGB\n'
                                         '  Used: %sGB\n'
                                         '  Free: %sGB\n') % (item.path,
                                                              round(item.total / (1024**3), 2),
                                                              round(item.used / (1024**3), 2),
                                                              round(item.free / (1024**3), 2))
    tags = {"<!--username-->": si.username,
            "<!--hostname-->": si.hostname,
            "<!--platform-->": si.os_platform,
            "<!--distribution-->": si.platform_linux_distribution[0],
            "<!--dist_version-->": si.platform_linux_distribution[1],
            "<!--platform_system-->": si.platform_system,
            "<!--platform_node-->": si.platform_node,
            "<!--platform_release-->": si.platform_release,
            "<!--platform_version-->": si.platform_version,
            "<!--platform_machine-->": si.platform_machine,
            "<!--cpu_model-->": si.cpu_model,
            "<!--cpu_cores-->": str(si.cpu_cores),
            "<!--cpu_temp-->": si.cpu_temp,
            "<!--cpu_clock_speed-->": si.cpu_clock_speed,
            "<!--cpu_max_clock_speed-->": si.cpu_max_clock_speed,
            "<!--cpu_hardware-->": si.cpu_hardware,
            "<!--cpu_revision-->": si.cpu_revision,
            "<!--cpu_serial_number-->": si.cpu_serial_number,
            "<!--gpu_temp-->": si.gpu_temp,
            "<!--gpu_clock_speed-->": si.gpu_clock_speed,
            "<!--gpu_memory-->": si.gpu_memory,
            "<!--total_mem-->": str(int(si.ram_info.total / 1024)),
            "<!--used_mem-->": str(int(si.ram_info.used / 1024)),
            "<!--free_mem-->": str(int(si.ram_info.free / 1024)),
            "<!--disk_info_txt-->": disk_info_txt,
            "<!--eth0_lan_ip-->": si.get_lan_ip_addr('eth0'),
            "<!--wlan0_lan_ip-->": si.get_lan_ip_addr('wlan0'),
            "<!--gateway_ip-->": si.default_gateway,
            "<!--wan_ip-->": si.wan_ip_addr,
            "<!--camera_supported-->": si.camera_available['supported'],
            "<!--camera_detected-->": si.camera_available['detected'],
            "<!--usb_sound_card_detected-->": si.usb_sound_card_detected,
            "<!--network_detected-->": si.network_detected,
            "<!--internet_detected-->": si.internet_detected}

    for key, value in settings_dict.items():
        if len(str(value)) > 50:
            value = value[:50].replace('~', '%') + "..."
        tags.update({"<!--%s-->" % key: str(value)})

    for tag, cmd in tags.items():
        page = page.replace(tag, "<b>%s</b>" % cmd.replace('©', '&#169;'))

    return page


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Redirect to the defalt settings page
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            # Display settings page
            content = INDEX_PAGE().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/help.html':
            # Display help page
            content = HELP_PAGE().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/info.html':
            # Display information page
            content = INFO_PAGE().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/no_preview.png':
            # Display no prview image
            self.send_response(200)
            file = open(HTML_DIR + '/no_preview.png', 'rb')
            img = file.read()
            size = str(os.stat(HTML_DIR + '/no_preview.png').st_size)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', size)
            self.end_headers()
            self.wfile.write(img)
        elif self.path == '/favicon.ico':
            # Display no prview image
            self.send_response(200)
            file = open(HTML_DIR + '/favicon.ico', 'rb')
            img = file.read()
            size = str(os.stat(HTML_DIR + '/favicon.ico').st_size)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', size)
            self.end_headers()
            self.wfile.write(img)
        elif self.path == '/stream.mjpg':
            # Video stream
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type',
                             'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        # Post the settings to commit any changes
        import urllib.parse
        global settings_dict
        boolean_options = ['enable_speaker', 'startup_udp',
                           'stream_to_facebook', 'stream_to_periscope',
                           'stream_to_twitch', 'stream_to_ustream',
                           'stream_to_vimeo', 'stream_to_youtube', 'update_os',
                           'upgrade_os', 'video_out_overlay_bg_color_enabled',
                           'video_image_horizontal_flip', 'video_stabilisation',
                           'video_image_vertical_flip']
        content_length = int(self.headers['Content-Length']) # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8") # Get the data
        post_data = urllib.parse.unquote(str(post_data))
        post_data = post_data.split("&")
        for item in post_data:
            items = item.split("=")
            if items[0] == 'video_res':
                item = items[1].split('x')
                settings_dict.update({'video_in_width': item[0]})
                settings_dict.update({'video_in_height': item[1]})
            elif items[1] == 'on':
                settings_dict.update({items[0]:items[1].replace('on', 'True')})
            else:
                settings_dict.update({items[0]:items[1]
                                     .replace("'", '"')
                                     .replace('+', ' ')
                                     .replace('%', '~')})
        if post_data[0]=='update=update':
            post_data = str(post_data).replace('update=update', '')
            commontasks.check_for_updates(WORK_DIR, 'Manual update started')
        else:
            for item in boolean_options:
                if str(post_data).find(item) < 0:
                    settings_dict.update({item: 'False'})

        set_settings()
        set_camera_settings()
        self.do_GET()

    def log_message(self, format, *args):
        # Create a log when changing settings
        if args[1] == '301': # POST
            txt = '%s @ %s Changed Settings' % (self.address_string(),
                                                dt.date.today()
                                                .strftime('%d/%m/%Y'))
            commontasks.write_to_file(WORK_DIR + '/settings.log', txt, True)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    global hidden_form_elements
    allow_reuse_address = True
    daemon_threads = True


def round_to_even(f):
    a = math.floor(f / 2.) * 2
    b = math.ceil(f / 2.) * 2
    if (f-a) < (b-f):
        return a
    else:
        return b


def set_camera_settings():
    try:
        MAX_RES = 1080
        PREVIEW_RES = 270
        txt = settings_dict['video_out_overlay_text'].replace('~','%')
        font_size = settings_dict['video_out_overlay_text_size']
        camera.annotate_text = dt.datetime.now().strftime(txt)
        camera.annotate_foreground = picamera.color.Color(settings_dict['video_out_overlay_text_color'])
        if settings_dict['video_out_overlay_bg_color_enabled'] == 'True':
            camera.annotate_background = picamera.color.Color(settings_dict['video_out_overlay_bg_color'])
        else:
            camera.annotate_background = None
        ratio = PREVIEW_RES / MAX_RES
        camera.annotate_text_size = round_to_even((int(font_size) * ratio))
        if settings_dict['video_image_automatic_white_balance'] != 'off':
            camera.awb_mode = settings_dict['video_image_automatic_white_balance']
        camera.brightness = int(settings_dict['video_image_brightness'])
        camera.contrast = int(settings_dict['video_image_contrast'])
        camera.saturation = int(settings_dict['video_image_saturation'])
        camera.sharpness = int(settings_dict['video_image_sharpness'])
        camera.drc_strength = settings_dict['video_image_dynamic_range_compression']
        camera.exposure_mode = settings_dict['video_image_exposure']
        if settings_dict['video_image_horizontal_flip'] == 'True':
            camera.hflip = True
        else:
            camera.hflip = False
        if settings_dict['video_image_vertical_flip'] == 'True':
            camera.vflip = True
        else:
            camera.vflip = False
        camera.image_effect = settings_dict['video_image_effect']
        camera.rotation = int(settings_dict['video_image_rotation'])
        if settings_dict['video_stabilisation'] == 'True':
            camera.video_stabilization = True
        else:
            camera.video_stabilization = False
    except:
        pass


try:
    with picamera.PiCamera(resolution='480x270', framerate=24) as camera:
        set_camera_settings()
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', PORT_NUMBER)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()
            camera.close()
except:
    output = StreamingOutput()
    try:
        address = ('', PORT_NUMBER)
        server = StreamingServer(address, StreamingHandler)
        hidden_form_elements = ('<center><b><p style="color: #8b0000;">Preview'
                                ' unavailable during a live stream.</p></b>'
                                '</center>')
        server.serve_forever()
    except:
        pass
