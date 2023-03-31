import os
import datetime
import time
from _thread import start_new_thread

from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

import mutagen
import wave


def get_bundle_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_date():
    d = datetime.datetime.now()
    return '{}-{}-{}'.format(d.year, d.month, d.day)


def get_device_name():
    if Window.height == 1136:
        device = "iPhone 5/5S/5C"

    elif Window.height == 1334:
        device = "iPhone 6/6S/7/8"

    elif Window.height in (1920, 2208):
        device = "iPhone 6+/6S+/7+/8+"

    elif Window.height == 2436:
        device = "X/XS/11 Pro/12 Mini/13 Mini"

    elif Window.height == 2532:
        device = "12/12 Pro/13/13 Pro"

    elif Window.height == 2688:
        device = "XS Max/11 Pro Max"

    elif Window.height == 2778:
        device = "12 Pro Max/13 Pro Max"

    elif Window.height == 1792:
        device = "iPhone XR/ 11"

    else:
        device = "Unknown"

    return device


def get_padding_y(iphone):
    ips = iphone.split('/')

    for ip in ips:
        if ip in ('X', 'XS', 'XS Max', '11 Pro', '11 Pro Max'):
            padding_y = (44, 34)
            break
        elif ip in ('12', '12 Pro', '12 Pro Max', '13', '13 Pro', '13 Pro Max'):
            padding_y = (47, 34)
            break
        elif ip in ('XR', '11'):
            padding_y = (48, 34)
            break
        elif ip in ('12 Mini', '13 Mini'):
            padding_y = (50, 34)
            break
        else:
            padding_y = (0, 0)

    return padding_y


def get_scale(iphone):
    ips = iphone.split('/')

    for ip in ips:
        if ip in ('X', 'XS', 'XS Max', '11 Pro', '11 Pro Max', '12', '12 Mini', '12 Pro', '12 Pro Max'):
            in_scale = 3
            break
        elif ip in ('11', 'XR', '6', '6S', '7', '8', '5', '5S', '5C', 'SE', '4', '4S'):
            in_scale = 2
            break
        elif ip in ('6+', '6S+', '7+', '8+'):
            in_scale = 2.61
            break
        else:
            in_scale = 1
            break

    return in_scale


device = get_device_name()
padding_y = get_padding_y(device)
scale = get_scale(device)
element_sep = dp(8)
bottom_sep = dp(12)
rounded_radius = dp(5)
animation_time = .003
is_animation_in_progress = False
pnl_search_height = 56 * scale
txt_search_height = 44 * scale
lbl_search_cancel_height = 56 * scale
icon_height = 24 * scale
default_bgr = '4.png'


def get_image_path(filename, image_type='icon'):
    global scale

    if image_type == 'icon':
        head, tail = os.path.splitext(filename)
        if scale == 1:
            return os.path.join(get_bundle_dir(), 'assets', filename)
        elif scale == 2:
            return os.path.join(get_bundle_dir(), 'assets', ''.join((head, '@2x', tail)))
        else:
            return os.path.join(get_bundle_dir(), 'assets', ''.join((head, '@3x', tail)))
    elif image_type == 'background':
        return os.path.join(get_bundle_dir(), 'assets', 'background', filename)


def hide_widget(wid, dohide=True):
    if hasattr(wid, 'saved_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


def appear_widget(wid, doappear=True):
    global is_animation_in_progress

    # Do nothing if another process of animation in progress
    if is_animation_in_progress:
        print('slide in progress')
        return

    if hasattr(wid, 'saved_attrs'):
        if doappear:
            # Load saved attributes
            saved_height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            # Delete saved attributes
            del wid.saved_attrs
            # Increase height from 0 to saved height
            start_new_thread(slide_attribute, (wid, 'height', 0, saved_height, 10))

    elif not doappear:
        # Disappear widget
        # Save current attributes
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        # Set invisible attributes
        wid.size_hint_y, wid.opacity, wid.disabled = None, 0, True
        # Decrease height to 0
        start_new_thread(slide_attribute, (wid, 'height', wid.height, 0, 5))   # Opacity is turned to 0 after this thread finishes


def is_point_inside_rectangle(x1, y1, x2, y2, x, y) :
    if x1 < x < x2 and y1 < y < y2:
        return True
    else:
        return False


def is_widget_touched(wid, touch, offset=12):
    # Calculate the space triggering show search box action
    x, y = touch.pos
    x1 = wid.x
    y1 = wid.y
    x2 = x1 + wid.width
    y2 = x1 + wid.height

    # Offset
    x1 -= offset
    y1 -= offset
    x2 += offset
    y2 += offset

    if is_point_inside_rectangle(x1, y1, x2, y2, x, y):
        return True
    else:
        return False


def fade_widget(wid, dofade=True):
    if hasattr(wid, 'fade_rect'):
        if not dofade:
            wid.canvas.after.remove(wid.fade_rect)
            del wid.fade_rect
    elif dofade:
        fade_color = (0.9529411764705882, 0.9450980392156862, 0.9607843137254902, .7)
        with wid.canvas.after:
            Color(*fade_color)
            wid.fade_rect = RoundedRectangle(size=(wid.width + element_sep * scale,
                                                   wid.height + element_sep * scale),
                                             pos=(wid.x - element_sep * scale,
                                                  wid.y - element_sep * scale),
                                             radius=((wid.width + element_sep * scale) / 2,
                                                     (wid.height + element_sep * scale) / 2))


def is_touch_around_label(wid, touch, around_space=12*scale):
    """
    Judge whether user touches around Done label
    :param wid: widget to check around touch
    :param touch: touch object including pos, spos
    :param around_space: offset from widget's boundaries
    :return: True if touch inside, otherwise False
    """

    # Calculate rectangle of texture
    x1 = wid.x + (wid.width - wid.texture_size[0]) / 2
    y1 = wid.y + (wid.height - wid.texture_size[1]) / 2
    x2 = x1 + wid.texture_size[0]
    y2 = y1 + wid.texture_size[1]

    # Plus offsets
    x1 -= around_space
    y1 -= around_space
    x2 += around_space
    y2 += around_space

    return is_point_inside_rectangle(x1, y1, x2, y2, *touch.pos)


def is_touch_around_wid(wid, touch, around_space=12*scale):
    """
    Judge whether user touches around Done label
    :param wid: widget to check around touch
    :param touch: touch object including pos, spos
    :param around_space: offset from widget's boundaries
    :return: True if touch inside, otherwise False
    """

    # Calculate rectangle of texture
    x1 = wid.x
    y1 = wid.y
    x2 = x1 + wid.width
    y2 = y1 + wid.height

    # Plus offsets
    x1 -= around_space
    y1 -= around_space
    x2 += around_space
    y2 += around_space

    return is_point_inside_rectangle(x1, y1, x2, y2, *touch.pos)


def is_widgets_overlap(widget1, widget2):
    rect1 = [widget1.x, widget1.y, widget1.x + widget1.width, widget1.y + widget1.height]
    rect2 = [widget2.x, widget2.y, widget2.x + widget2.width, widget2.y + widget2.height]
    return is_rectangles_overlap(rect1, rect2)


def is_rectangles_overlap(R1, R2):
    if (R1[0] >= R2[2]) or (R1[2] <= R2[0]) or (R1[3] <= R2[1]) or (R1[1] >= R2[3]):
        return False
    else:
        return True


def get_color_from_string(color):
    """
    Transform a color string (eg. 1,1,1,1) to color of kivy
    :param color: 4 element color string
    :return: list of 4 flost values accordingly
    """
    return [float(ele) for ele in color.split(',')]


def get_gesture_type(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    if y2 > y1:
        return 'swipe_up'
    else:
        return 'swipe_down'


def get_gesture_type_horizontal(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    if x2 > x1:
        return 'swipe_right'
    else:
        return 'swipe_left'


def get_move_distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(y2 - y1)


def get_move_distance_horizontal(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x2 - x1)


def slide_attribute(wid, attribute, start, end, increment=1*scale, callback=None, animation_time=.003, check_conflict=True):
    """

    :param wid:
    :param attribute:
    :param start:
    :param end:
    :param increment:
    :param callback: a tuple of (callback, tuple of args)
    :param animation_time: default .003s
    :return:
    """
    global is_animation_in_progress

    if is_animation_in_progress and check_conflict:
        print('Slide conflict, omit.')
        return

    is_animation_in_progress = True

    if start < end:
        while getattr(wid, attribute) < end:
            setattr(wid, attribute, min(getattr(wid, attribute) + increment, end))
            time.sleep(animation_time)
    else:
        while getattr(wid, attribute) > end:
            setattr(wid, attribute, max(getattr(wid, attribute) - increment, end))
            time.sleep(animation_time)

    # Turn off animation flag
    is_animation_in_progress = False

    if callback:
        callback[0](*callback[1])


def is_valid_audio(audio_path):
    """
    :param audio_path:
    :return: either of 'mp3', 'audio', or None
    """

    try:
        with wave.open(audio_path, 'rb') as f:
            print('A wav file')
            return 'wav'
    except wave.Error:
        print('Not a wav file')

    try:
        f = mutagen.File(audio_path)
    except mutagen.MutagenError:
        print('A directory dropped')
        return None

    if not f:
        print('Not a valid audio file dropped')
        return None
    if 'mpeg-4' in f.info.pprint().lower() or 'MPEG 1 layer 3'.lower() in f.info.pprint().lower():
        print('A mp3 file dropped')
        return 'mp3'
    elif f:
        print('An audio file dropped')
        return 'audio'
