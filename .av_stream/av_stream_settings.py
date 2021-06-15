# Web streaming example

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import os
import datetime as dt
import time
from resources.lib.systeminfo import SystemInfo
from resources.lib import commontasks

si = SystemInfo()
audio_codecs = ['aac', 'mp2', 'mp3']
audio_bitrates = ['32k', '64k', '96k', '128k']
audio_sample_rates = ['44100', '48000']
video_fps = ['15', '20', '25', '30']
video_resolutions = ['480x270','960x540', '1280x720', '1920x1080']
video_codecs = ['mp4', 'mpegts']
offset_types = ['audio', 'video', 'none']
update_intervals = ['1', '7', '30']
logging_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
settings_dict = {}
hidden_form_elements = '<br>'

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
    logging.getLogger().disable(level=CRITICAL)
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
    audio_out_codec_txt = options(settings_dict['audio_out_codec'],audio_codecs)
    audio_out_bitrate_txt = options(settings_dict['audio_out_bitrate'], audio_bitrates)
    audio_out_sample_rate_txt = options(settings_dict['audio_out_sample_rate'], audio_sample_rates)
    video_in_frames_per_second_txt = options(settings_dict['video_in_frames_per_second'], video_fps)
    video_resolution_txt = options(settings_dict['video_in_width'] + "x" + settings_dict['video_in_height'], video_resolutions)
    video_out_codec_txt = options(settings_dict['video_out_codec'], video_codecs)
    itsoffset_txt = options(settings_dict['itsoffset'], offset_types)
    update_interval_days_txt = options(settings_dict['update_interval_days'], update_intervals)
    logging_level_txt = options(settings_dict['logging_level'], logging_levels)
    hostname = si.hostname
    enable_speaker_txt = ''
    startup_udp_txt = ''
    update_os_txt = ''
    upgrade_os_txt = ''
    disable_form_elements = ''
    # HTML form checkboxes
    if settings_dict['enable_speaker'] == 'True':
        enable_speaker_txt = 'checked="True"'
    if settings_dict['startup_udp'] == 'True':
        startup_udp_txt = 'checked="True"'
        disable_form_elements = 'disabled'
    if settings_dict['update_os'] == 'True':
        update_os_txt = 'checked="True"'
    if settings_dict['upgrade_os'] == 'True':
        upgrade_os_txt = 'checked="True"'

    # other HTML form elemets
    tags = {"<!--hidden-->": hidden_form_elements,
            "<!--startup_enabled-->": disable_form_elements,
            "<!--audio_out_codec_txt-->": audio_out_codec_txt,
            "<!--audio_out_bitrate_txt-->": audio_out_bitrate_txt,
            "<!--audio_out_sample_rate_txt-->": audio_out_sample_rate_txt,
            "<!--video_in_frames_per_second_txt-->": video_in_frames_per_second_txt,
            "<!--video_resolution_txt-->": video_resolution_txt,
            "<!--video_out_codec_txt-->": video_out_codec_txt,
            "<!--itsoffset_txt-->": itsoffset_txt,
            "<!--enable_speaker_txt-->": enable_speaker_txt,
            "<!--startup_udp_txt-->": startup_udp_txt,
            "<!--update_os_txt-->": update_os_txt,
            "<!--upgrade_os_txt-->": upgrade_os_txt,
            "<!--update_interval_days_txt": update_interval_days_txt,
            "<!--facebook_url-->": settings_dict['facebook_url'],
            "<!--facebook_stream_key-->": settings_dict['facebook_stream_key'],
            "<!--video_in_bitrate-->": settings_dict['video_in_bitrate'],
            "<!--video_out_overlay_text-->": settings_dict['video_out_overlay_text'].replace('"', "'").replace('~', '%'),
            "<!--itsoffset_seconds-->": settings_dict['itsoffset_seconds'],
            "<!--metadata_title-->": settings_dict['metadata_title'],
            "<!--metadata_year-->": settings_dict['metadata_year'],
            "<!--metadata_description-->": settings_dict['metadata_description'],
            "<!--logging_level_txt-->": logging_level_txt}
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
            "<!--wan_ip-->": si.wan_ip_addr.decode('utf-8'),
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
        page = page.replace(tag, "<b>%s</b>" % cmd)

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
            logging.info('Manual update started')
            response = os.popen('python %s/updateWorker.py' % WORK_DIR).read()
            if settings_dict['update_os'] == 'True':
                os.popen('sudo apt-get update')
                logging.info('OS updated manually')
            if settings_dict['upgrade_os'] == 'True':
                os.popen('sudo apt-get upgrade')
                logging.info('OS upgraded manually')
            settings_dict.update({'last_updated':
                                  dt.date.today().strftime('%d/%m/%Y')})
        else:
            if str(post_data).find('enable_speaker') < 0:
                settings_dict.update({'enable_speaker': 'False'})
            if str(post_data).find('startup_udp') < 0:
                settings_dict.update({'startup_udp': 'False'})
            if str(post_data).find('update_os') < 0:
                settings_dict.update({'update_os': 'False'})
            if str(post_data).find('upgrade_os') < 0:
                settings_dict.update({'upgrade_os': 'False'})
        set_settings()
        self.do_GET()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    global hidden_form_elements
    allow_reuse_address = True
    daemon_threads = True

try:
    with picamera.PiCamera(resolution='480x270', framerate=24) as camera:
        txt = settings_dict['video_out_overlay_text'].replace('~','%')
        txt = commontasks.regex_from_to(txt, ' "', '" ')
        camera.annotate_text = dt.datetime.now().strftime(txt)
        camera.annotate_text_size = 12
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()
except:
    output = StreamingOutput()
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        hidden_form_elements = ('<center><b><p style="color: #8b0000;">Preview'
                                ' unavailable during a live stream.</p></b>'
                                '</center>')
        server.serve_forever()
    except:
        pass
