import os
import platform
import re
import time
from _thread import start_new_thread

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Rotate
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import (ListProperty, ColorProperty, NumericProperty, BooleanProperty,
                             StringProperty, ObjectProperty, ReferenceListProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.stencilview import StencilView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from plyer import vibrator

import common


class HorizontalSeparator(FloatLayout):

    def __init__(self, height=common.element_sep * common.scale, **kwargs):
        super(HorizontalSeparator, self).__init__(**kwargs)
        self.height = height


class VerticalSeparator(FloatLayout):

    def __init__(self, width=common.element_sep * common.scale, **kwargs):
        super(VerticalSeparator, self).__init__(**kwargs)
        self.width = width


class RoundedButton(Button):
    value = NumericProperty(-1)
    radius = ListProperty([0, ])
    background_color_display = ColorProperty([0, 0, 1, 1])
    icon = StringProperty('')
    icon_display = BooleanProperty(False)
    icon_pos_hint = StringProperty('center')
    icon_pos_x = NumericProperty()
    is_touched_down = False

    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.remove_rect()
            offset = .4
            fade_color = (min(self.background_color_display[0] + offset, 1),
                          min(self.background_color_display[1] + offset, 1),
                          min(self.background_color_display[2] + offset, 1),
                          .5)
            with self.canvas:
                Color(*fade_color)
                self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)

            self.bind(size=self.update_rect, pos=self.update_rect)

            self.is_touched_down = True                 # Turn on touch down flag

    def on_touch_up(self, touch):
        self.remove_rect()
        self.is_touched_down = False                    # Turn off touch down flag

    def update_rect(self, *args):
        if hasattr(self, 'rect') and self.rect in self.canvas.children:
            self.rect.size = self.size
            self.rect.pos = self.pos

    def remove_rect(self):
        if hasattr(self, 'rect') and self.rect in self.canvas.children:
            self.canvas.remove(self.rect)


class RoundedImageButton(ButtonBehavior, FloatLayout):
    text = StringProperty('')
    font_size = NumericProperty(15)
    color = ColorProperty([1, 1, 1, 1])
    source = StringProperty('')
    radius = ListProperty([0, ])
    background_color_display = ColorProperty([0, 0, 1, 1])
    icon_pos_hint = StringProperty('center')
    icon_pos_x = NumericProperty()
    halign = StringProperty('center')
    valign = StringProperty('middle')
    padding_x = NumericProperty(0)
    padding_y = NumericProperty(0)
    padding = ReferenceListProperty(padding_x, padding_y)
    is_touched_down = False
    tooltip_text = StringProperty('')

    def __init__(self, **kwargs):
        super(RoundedImageButton, self).__init__(**kwargs)
        self.tooltip = Tooltip()
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        self.tooltip.pos = pos
        Clock.unschedule(self.display_tooltip) # cancel scheduled event since I moved the cursor
        self.close_tooltip() # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 1)

    def close_tooltip(self, *args):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        self.tooltip.text = self.tooltip_text
        Window.add_widget(self.tooltip)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.remove_rect()
            offset = .4
            fade_color = (min(self.background_color_display[0] + offset, 1),
                          min(self.background_color_display[1] + offset, 1),
                          min(self.background_color_display[2] + offset, 1),
                          .5)
            with self.canvas:
                Color(*fade_color)
                self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)

            self.bind(size=self.update_rect, pos=self.update_rect)

            self.is_touched_down = True                 # Turn on touch down flag

    def on_touch_up(self, touch):
        self.remove_rect()
        self.is_touched_down = False                    # Turn off touch down flag

    def update_rect(self, *args):
        if hasattr(self, 'rect') and self.rect in self.canvas.children:
            self.rect.size = self.size
            self.rect.pos = self.pos

    def remove_rect(self):
        if hasattr(self, 'rect') and self.rect in self.canvas.children:
            self.canvas.remove(self.rect)


class BorderedButton(Button):
    select = NumericProperty(-1)
    background_color_border = ColorProperty([1, 1, 1, 1])
    background_color_display = ColorProperty([0, 0, 1, 1])
    border_width = NumericProperty(2)
    radius = ListProperty([0,])

    def __init__(self, **kwargs):
        super(BorderedButton, self).__init__(**kwargs)
        self.saved_background_color_display = self.background_color_display

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            offset = .4
            fade_color = (min(self.background_color_display[0] + offset, 1),
                          min(self.background_color_display[1] + offset, 1),
                          min(self.background_color_display[2] + offset, 1),
                          .5)
            with self.canvas:
                Color(*fade_color)
                self.rect = RoundedRectangle(size=(self.width - self.border_width, self.height - self.border_width),
                                             pos=(self.x + self.border_width / 2, self.y + self.border_width / 2),
                                             radius=self.radius)

    def on_touch_up(self, touch):
        if hasattr(self, 'rect') and self.rect in self.canvas.children:
            self.canvas.remove(self.rect)


class PopMenu(object):

    def __init__(self, touch, content, type='menu', pos_hint={'center_x': .5, 'center_y': .5}, auto_dismiss=True):
        self.content = content
        self.touch = touch

        if type == 'menu':
            # Used for popup menu
            self.popup = ModalView(size_hint=(None, None),
                                   width=self.content.width,
                                   height=self.content.height,
                                   pos_hint={'x': touch.spos[0], 'top': touch.spos[1]})
        elif type == 'window':
            # Used for popup window
            self.popup = ModalView(size_hint=(None, None),
                                   width=self.content.width,
                                   height=self.content.height,
                                   pos_hint=pos_hint)

        self.content.bind(size=self.on_content_size, pos=self.on_content_size)
        self.popup.add_widget(self.content)

        self.popup.auto_dismiss = auto_dismiss
        self.popup.bind(on_dismiss=self.on_dismiss)

    def on_content_size(self, instance, value):
        self.popup.size = self.content.size
        self.popup.pos = self.content.pos

    def open(self, animated=True, *args):

        if not animated:
            # Open then do nothing else if no animation requested
            self.popup.open()  # Open popup
            self.adjust_position()  # Update correct popup position
            return

        self.popup.opacity = 0                                      # Set opacity to 0 for hiding

        self.popup.open()                                           # Open popup

        # Save destination position
        self.adjust_position()                                      # Update expected popup position
        self.saved_pos = tuple(self.popup.pos)                      # Save expected pos
        self.saved_pos_hint_x = self.popup.pos[0] / Window.width    # Calculate expected pos_hint_x
        self.saved_pos_hint_y = self.popup.pos[1] / Window.height   # Calculate expected pos_hint_y

        # Assign center point to temporary pos
        self.tmp_pos = tuple(self.popup.center)
        self.tmp_pos_hint = {'x': self.tmp_pos[0] / Window.width, 'y': self.tmp_pos[1] / Window.height}

        # Save size
        self.saved_size = tuple(self.popup.size)

        self.popup.opacity = 1                                      # Set opacity to 1 for display

        # Minimize sizes of popup and its content
        self.popup.size = 0, 0
        self.content.size = 0, 0

        self.popup.pos_hint = self.tmp_pos_hint                     # Set temporary pos_hint

        self.animate_popup()                                        # Animate

    def animate_popup(self):
        """ Animate popup menu and its content """

        consumed_pixels = 8
        sleep_time = .0008

        start_new_thread(common.slide_attribute, (self.popup, 'width', self.popup.width, self.saved_size[0], consumed_pixels, None, sleep_time, False))
        start_new_thread(common.slide_attribute, (self.popup, 'height', self.popup.height, self.saved_size[1], consumed_pixels, None, sleep_time, False))
        start_new_thread(common.slide_attribute, (self.content, 'width', self.content.width, self.saved_size[0], consumed_pixels, None, sleep_time, False))
        start_new_thread(common.slide_attribute, (self.content, 'height', self.content.height, self.saved_size[1], consumed_pixels, None, sleep_time, False))

        # Animate menu items
        for item in self.content.items:
            old_width = item.width
            old_height = item.height
            item.size = 0, 0
            start_new_thread(common.slide_attribute, (item, 'width', item.width, old_width, consumed_pixels, None, sleep_time, False))
            start_new_thread(common.slide_attribute, (item, 'height', item.height, old_height, consumed_pixels, None, sleep_time, False))

        # Animate menu pos_hint{x,y} from temporary postion (center point) to desired bottom left point
        start_new_thread(self.slide_pos_hint_x, (self.popup.pos_hint['x'], self.saved_pos_hint_x, ))
        start_new_thread(self.slide_pos_hint_y, (self.popup.pos_hint['y'], self.saved_pos_hint_y))

    def slide_pos_hint_x(self, start, end, increment=.01):
        """ Animate pos_hint['x'] of popup menu """

        sleep_time = .003

        self.popup.pos_hint = {'x': start, 'y': self.popup.pos_hint['y']}
        if start < end:
            while self.popup.pos_hint['x'] < end:
                new_x = self.popup.pos_hint['x'] + increment
                self.popup.pos_hint = {'x': new_x, 'y': self.popup.pos_hint['y']}
                time.sleep(sleep_time)
        else:
            while self.popup.pos_hint['x'] > end:
                new_x = self.popup.pos_hint['x'] - increment
                self.popup.pos_hint = {'x': new_x, 'y': self.popup.pos_hint['y']}
                time.sleep(sleep_time)

    def slide_pos_hint_y(self, start, end, increment=.01):
        """ Animate pos_hint['y'] of popup menu """

        sleep_time = .002

        self.popup.pos_hint = {'x': self.popup.pos_hint['x'], 'y': start}
        if start < end:
            while self.popup.pos_hint['y'] < end:
                new_y = self.popup.pos_hint['y'] + increment
                self.popup.pos_hint = {'x': self.popup.pos_hint['x'], 'y': new_y}
                time.sleep(sleep_time)
        else:
            while self.popup.pos_hint['y'] > end:
                new_y = self.popup.pos_hint['y'] - increment
                self.popup.pos_hint = {'x': self.popup.pos_hint['x'], 'y': new_y}
                time.sleep(sleep_time)

    def adjust_position(self):
        # Adjust pos_hint constraints to fix overlap off screen
        if self.popup.x + self.popup.width > Window.width:
            self.popup.pos_hint = {'right': 1, 'top': self.popup.pos_hint['top']}
        elif self.popup.x < 0:
            self.popup.pos_hint = {'left': 0, 'top': self.popup.pos_hint['top']}

        if self.popup.y < 0:
            # Keep old contraints
            if 'right' in self.popup.pos_hint.keys():
                kept = 'right'
            elif 'left' in self.popup.pos_hint.keys():
                kept = 'left'
            elif 'x' in self.popup.pos_hint.keys():
                kept = 'x'

            self.popup.pos_hint = {kept: self.popup.pos_hint[kept], 'y': 0}

    def dismiss(self):
        self.popup.dismiss()

    def on_dismiss(self, instance):
        pass


class PopupMenuContent(FloatLayout):
    radius = ListProperty([dp(common.rounded_radius), dp(common.rounded_radius)])

    def __init__(self, **kwargs):
        super(PopupMenuContent, self).__init__(**kwargs)
        self.items = []
        self.pnl_items.bind(size=self.on_pnl_items_size, pos=self.on_pnl_items_size)

    def on_pnl_items_size(self, instance, value):
        self.refresh()

    def add_menu_item(self, item):
        # Store item to a list
        self.items.append(item)

        # Add item to popup menu content
        self.pnl_items.add_widget(item)

        # Set width of popup menu content equal to the widest item
        self.width = max([item.width for item in self.items])

        # set height equal to total height of all items
        self.height = sum([item.height for item in self.items])

    def refresh(self):
        # Set width of popup menu content equal to the widest item
        self.width = max([item.width for item in self.items])

        # set height equal to total height of all items
        self.height = sum([item.height for item in self.items])


class MessageInfo(FloatLayout):
    text = StringProperty('')
    radius = ListProperty([0, 0, 0, 0])
    font_size = NumericProperty(15)


class MessagePanel(FloatLayout):
    radius = ListProperty([0, 0, 0, 0])


class PopupMessage(PopMenu):

    response = None

    def __init__(self, message, width=None, height=dp(44 * 2), action='ok'):
        radius_val = dp(common.rounded_radius * 3)
        sep = 1 * common.scale

        content = PopupMenuContent(radius=[radius_val, radius_val])
        lbl_notification = MessageInfo(text=message,
                                       size_hint=(None, None),
                                       width=(Window.width * .618) if width is None else width,
                                       height=height,
                                       radius=[radius_val, radius_val, 0, 0],
                                       font_size=17 * common.scale)
        self.btn_ok = RoundedButton(text='OK', size_hint=(None, None),
                                    width=lbl_notification.width, height=56 * common.scale,
                                    radius=[(0, 0), (0, 0),
                                            (radius_val, radius_val),
                                            (radius_val, radius_val)],
                                    font_size=21 * common.scale,
                                    bold=True,
                                    halign='center',
                                    color=get_color_from_hex('#0165ff'),
                                    background_color_display=get_color_from_hex('#ebebeb'))

        self.btn_ok.bind(on_touch_up=lambda x, y: self.on_btn_up(x, y))

        content.add_menu_item(lbl_notification)
        content.add_menu_item(HorizontalSeparator(height=sep))
        if action == 'ok':
            content.add_menu_item(self.btn_ok)
        elif action == 'ok_cancel':
            self.btn_ok.width = (lbl_notification.width - sep) / 2
            self.btn_ok.radius = [(0, 0), (0, 0),
                                  (radius_val, radius_val),
                                  (0, 0)]
            self.btn_cancel = RoundedButton(text='Cancel', size_hint=(None, None),
                                            width=self.btn_ok.width, height=self.btn_ok.height,
                                            radius=[(0, 0), (0, 0), (0, 0),
                                                    (radius_val, radius_val)],
                                            font_size=21 * common.scale,
                                            halign='center',
                                            color=get_color_from_hex('#0165ff'),
                                            background_color_display=get_color_from_hex('#ebebeb'))
            pnl_buttons = BoxLayout(orientation='horizontal', size_hint=(None, None),
                                    width=lbl_notification.width, height=self.btn_ok.height)

            self.btn_cancel.bind(on_touch_up=lambda x, y: self.on_btn_up(x, y))

            pnl_buttons.add_widget(self.btn_cancel)
            pnl_buttons.add_widget(VerticalSeparator(width=sep))
            pnl_buttons.add_widget(self.btn_ok)

            content.add_menu_item(pnl_buttons)
        else:
            content.add_menu_item(self.btn_ok)

        super(PopupMessage, self).__init__(None, content, 'window', auto_dismiss=False)

    def on_btn_up(self, instance, value):
        """ Handle user's response """
        if not instance.collide_point(*value.pos):
            return

        if instance is self.btn_ok:
            self.response = 'ok'
        elif instance is self.btn_cancel:
            self.response = 'cancel'

        self.popup.dismiss()

    def bind_dismiss(self, callback):
        # Bind callback to dismiss event of popup
        self.callback_dismiss = callback

    def on_dismiss(self, instance):
        # Call callback function on dismiss, can get response code then
        try:
            self.callback_dismiss(self)
        except AttributeError:
            # No callback specified
            pass


class PopupWindow(PopMenu):

    response = None

    def __init__(self, panel, width=Window.width * .618, height=44 * 2 * common.scale, radius_val=dp(common.rounded_radius), use_buttons=True):
        sep = dp(1)

        panel.bind(size=self.refresh, pos=self.refresh)

        if use_buttons:
            self.content = PopupMenuContent(radius=[radius_val, radius_val])
        else:
            self.content = PopupMenuContent(radius=[radius_val, radius_val, radius_val, radius_val])
        self.btn_ok = RoundedButton(text='OK', size_hint=(None, None),
                                width=(panel.width - sep) / 2, height=56 * common.scale,
                                radius=[(0, 0), (0, 0),
                                        (radius_val, radius_val),
                                        (0, 0)],
                                font_size=21 * common.scale,
                                bold=True,
                                halign='center',
                                color=get_color_from_hex('#0165ff'),
                                background_color_display=get_color_from_hex('#ebebeb'))

        self.btn_cancel = RoundedButton(text='Cancel', size_hint=(None, None),
                                        width=self.btn_ok.width, height=self.btn_ok.height,
                                        radius=[(0, 0), (0, 0), (0, 0),
                                                (radius_val,
                                                 radius_val)],
                                        font_size=21 * common.scale,
                                        halign='center',
                                        color=get_color_from_hex('#0165ff'),
                                        background_color_display=get_color_from_hex('#ebebeb'))

        pnl_buttons = BoxLayout(orientation='horizontal', size_hint=(None, None),
                                width=panel.width, height=self.btn_ok.height)

        self.btn_ok.bind(on_touch_up=lambda x, y: self.on_btn_up(x, y))
        self.btn_cancel.bind(on_touch_up=lambda x, y: self.on_btn_up(x, y))

        pnl_buttons.add_widget(self.btn_cancel)
        pnl_buttons.add_widget(VerticalSeparator(width=sep))
        pnl_buttons.add_widget(self.btn_ok)

        self.content.add_menu_item(panel)
        if use_buttons:
            self.content.add_menu_item(HorizontalSeparator(height=dp(1)))
            self.content.add_menu_item(pnl_buttons)

        super(PopupWindow, self).__init__(None, self.content, 'window', auto_dismiss=False)

    def refresh(self, instance, value):
        self.content.refresh()

    def on_btn_up(self, instance, value):
        """ Handle user's response """
        if not instance.collide_point(*value.pos):
            return

        if instance is self.btn_ok and self.btn_ok.is_touched_down:
            self.response = 'ok'
            self.popup.dismiss()
        elif instance is self.btn_cancel and self.btn_cancel.is_touched_down:
            self.response = 'cancel'
            self.popup.dismiss()

    def bind_dismiss(self, callback):
        # Bind callback to dismiss event of popup
        self.callback_dismiss = callback

    def on_dismiss(self, instance):
        # Call callback function on dismiss, can get response code then
        try:
            self.callback_dismiss(self)
        except AttributeError:
            # No callback specified
            pass


class Tag(FloatLayout):
    value = NumericProperty(-1)
    color = ColorProperty(get_color_from_hex('#ffffff'))
    background_color = ColorProperty(get_color_from_hex('#5C7AEA'))
    radius = ListProperty([0, ])
    size_hint = ListProperty([1, 1])
    text = StringProperty('')
    font_size = NumericProperty(15)
    dots_opacity = BooleanProperty(1)
    dots_disabled = BooleanProperty(False)
    select = BooleanProperty(False)
    use_select = BooleanProperty(False)
    is_touched_down = False
    is_animation_progress = False

    def __init__(self, tag_content=None, **kwargs):
        super(Tag, self).__init__(**kwargs)
        self.tag_content = tag_content
        self.allocate_values()              # Assign tag values to fields
        self.register_event_type('on_popup_menu')
        self.register_event_type('on_tag_select')

    def allocate_values(self):
        self.value = self.tag_content.tag_id
        self.text = self.tag_content.name
        self.background_color = self.tag_content.color
        self.color = self.tag_content.text_color
        self.select = self.tag_content.selected

    def on_touch_down(self, value):
        if not self.collide_point(*value.pos):
            return

        self.is_touched_down = True                     # Turn on touch down flag

    def on_touch_up(self, value):
        if not self.collide_point(*value.pos) or not self.is_touched_down or self.is_animation_progress:
            self.is_touched_down = False                # Turn off touch down flag
            return

        if not self.dots_disabled and common.is_touch_around_wid(self.img_dots, value):
            # Dispatch on_popup_menu event if three dots touched
            self.dispatch('on_popup_menu', value)
        else:
            if self.use_select:
                self.select = not self.select
                # Dispatch on_select event if three dots touched
                self.dispatch('on_tag_select', self.select)

        self.is_touched_down = False                    # Turn off touch down flag

    def on_select(self, instance, value):
        self.is_animation_progress = True

        self.tag_content.selected = value
        if value and self.img_select.width < 24 * common.scale:
            new_width = 24 * common.scale
        else:
            new_width = 0

        anim = Animation(width=new_width, duration=.1)
        anim.bind(on_complete=lambda x, y: self.callback_animation())
        anim.start(self.img_select)

    def callback_animation(self):
        self.is_animation_progress = False

    def on_popup_menu(self, value):
        pass

    def on_tag_select(self, value):
        pass


class DropDownButton(FloatLayout):
    select = NumericProperty(-1)
    size_hint = ListProperty()
    text = StringProperty()
    font_size = NumericProperty()
    background_color_display = ColorProperty()
    radius = ListProperty()
    border_width = NumericProperty()
    state = BooleanProperty(False)
    direction = -1

    def on_state(self, instance, value):
        # Rotate dropdown icon
        start_new_thread(self.start_rotation, ())

    def start_rotation(self):
        angle_remain = 180
        angle_pcs = 10
        self.direction *= -1
        angle_rotation = angle_pcs * self.direction     # Apply rotation direction (clockwise or counter-clockwise)
        while angle_remain > 0:
            self.rotate(angle_rotation)                     # Rotate
            angle_remain -= angle_pcs                       # Calculate remaining angle to rotate
            time.sleep(common.animation_time)

    def rotate(self, angle):
        with self.img.canvas.before:
            PushMatrix()
            Rotate(angle=angle, origin=self.img.center)
        with self.img.canvas.after:
            PopMatrix()

    def set_appearance(self, dropdownitem):
        self.text = dropdownitem.text
        self.select = dropdownitem.value
        self.background_color_display = dropdownitem.background_color_display


class RoundedTextInput(TextInput):
    foreground_color = ColorProperty(get_color_from_hex('#000000'))
    border_color = ColorProperty(get_color_from_hex('#3f92db'))
    border_width = NumericProperty(1)
    radius = NumericProperty(0)
    padding_x = ListProperty([0, ])
    padding_y = ListProperty([0, ])
    header_image = StringProperty('')
    header_image_display = BooleanProperty(False)
    delete_display = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(RoundedTextInput, self).__init__(**kwargs)
        self.register_event_type('on_delete')
        self.keyboard_mode = 'managed'
        self.saved_foreground_color = self.foreground_color

    def on_delete(self):
        pass

    def on_touch_up(self, touch):
        # Calculate the space triggering delete action
        if self.delete_display:
            x, y = touch.pos
            x1 = (self.x + self.width
                  - (common.element_sep * common.scale)
                  - 24 * common.scale
                  - common.element_sep * 2 * common.scale)
            x2 = self.x + self.width
            y1 = self.y
            y2 = self.y + self.height

            if common.is_point_inside_rectangle(x1, y1, x2, y2, x, y) and len(self.text):
                self.text = ''
                self.dispatch('on_delete')

    def on_height(self, instance, value):
        if value < common.txt_search_height:
            self.foreground_color = get_color_from_hex('#8e8e9300')
        else:
            if len(self.text):
                self.foreground_color = self.saved_foreground_color
            else:
                self.foreground_color = get_color_from_hex('#8e8e93')


class NumberRoundedTextInput(RoundedTextInput):
    num_type = StringProperty('float')

    def insert_text(self, substring, from_undo=False):
        pat = re.compile('[^0-9]')
        if self.num_type == 'int':
            s = re.sub(pat, '', substring)
        elif self.num_type == 'float':
            if '.' in self.text:
                s = re.sub(pat, '', substring)
            else:
                s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])

        return super(NumberRoundedTextInput, self).insert_text(s, from_undo=from_undo)


class BackgroundOneLineRoundedTextInput(FloatLayout):
    txt = ObjectProperty()
    text = StringProperty('')
    border_width = NumericProperty(1)
    radius = NumericProperty(0)
    foreground_color = ColorProperty(get_color_from_hex('#000000'))
    background_color = ColorProperty(get_color_from_hex('#e8eaefff'))
    border_color = ColorProperty(get_color_from_hex('#0000ffff'))
    hint_text = StringProperty()
    font_size = NumericProperty(15)
    font_name = StringProperty('Roboto')
    font_family = StringProperty('')
    focus = BooleanProperty(False)
    padding_x = ListProperty([0, 0])
    halign = StringProperty('left')
    header_image_display = BooleanProperty(False)
    delete_display = BooleanProperty(False)
    magnifier_opacity = NumericProperty(0)

    def __init__(self, **kwargs):
        super(BackgroundOneLineRoundedTextInput, self).__init__(**kwargs)
        self.register_event_type('on_delete')

    def on_txt_delete(self, instance):
        self.dispatch('on_delete')

    def on_delete(self):
        pass

    def on_txt_focus(self, instance, value):
        self.focus = value

        if value:
            instance.show_keyboard()
        else:
            instance.hide_keyboard()

    def on_txt_text(self, instance, value):
        # Assign value to text attribute of widget
        self.text = value


class SearchBox(BackgroundOneLineRoundedTextInput):
    header_image_display = BooleanProperty(False)
    hint_text = StringProperty('Search')
    magnifier_opacity = NumericProperty(1)

    def on_height(self, instance, value):
        self.magnifier_opacity = 0 if value < common.txt_search_height else 1
        self.delete_display = False if value < common.txt_search_height else True


class BackgroundFloatInput(FloatLayout):
    txt = ObjectProperty()
    text = StringProperty()
    border_width = NumericProperty(1)
    radius = NumericProperty(0)
    foreground_color = ColorProperty(get_color_from_hex('#000000'))
    background_color = ColorProperty(get_color_from_hex('#e8eaefff'))
    border_color = ColorProperty(get_color_from_hex('#0000ffff'))
    hint_text = StringProperty()
    font_size = NumericProperty(15)
    font_name = StringProperty('Roboto')
    font_family = StringProperty('')
    focus = BooleanProperty(False)
    padding_x = ListProperty([0, 0])
    halign = StringProperty('left')
    header_image_display = BooleanProperty(False)
    delete_display = BooleanProperty(False)
    num_type = StringProperty('float')

    def __init__(self, **kwargs):
        super(BackgroundFloatInput, self).__init__(**kwargs)
        self.register_event_type('on_delete')

    def on_txt_delete(self, instance):
        self.dispatch('on_delete')

    def on_delete(self):
        pass

    def on_txt_focus(self, instance, value):
        self.focus = value

        if value:
            instance.show_keyboard()
        else:
            instance.hide_keyboard()

    def on_txt_text(self, instance, value):
        # Assign value to text attribute of widget
        self.text = value


class BackgroundMultilineRoundedTextInput(FloatLayout):
    txt = ObjectProperty()
    text = StringProperty()
    border_width = NumericProperty(1)
    radius = NumericProperty(0)
    foreground_color = ColorProperty(get_color_from_hex('#000000'))
    background_color = ColorProperty(get_color_from_hex('#e8eaefff'))
    border_color = ColorProperty(get_color_from_hex('#0000ffff'))
    hint_text = StringProperty()
    font_size = NumericProperty(15)
    font_name = StringProperty('Roboto')
    font_family = StringProperty('')
    focus = BooleanProperty(False)
    padding_x = ListProperty([0, 0])
    padding_y = ListProperty([0, 0])
    halign = StringProperty('left')
    header_image_display = BooleanProperty(False)
    delete_display = BooleanProperty(False)

    def on_txt_focus(self, instance, value):
        self.focus = value

        if value:
            instance.show_keyboard()
        else:
            instance.hide_keyboard()

    def on_txt_text(self, instance, value):
        # Assign value to text attribute of widget
        self.text = value


class ValueSlider(FloatLayout):
    txt = ObjectProperty()
    slider = ObjectProperty()
    border_width = NumericProperty(1)
    radius = NumericProperty(0)
    foreground_color = ColorProperty(get_color_from_hex('#000000'))
    background_color = ColorProperty(get_color_from_hex('#e8eaefff'))
    border_color = ColorProperty(get_color_from_hex('#0000ffff'))
    hint_text = StringProperty()
    font_size = NumericProperty('17sp')
    font_name = StringProperty('Roboto')
    font_family = StringProperty('')
    focus = BooleanProperty(False)
    padding_x = ListProperty([0, 0])
    step = NumericProperty(1)
    min = NumericProperty(0)
    max = NumericProperty(100)
    value_track = BooleanProperty(False)
    value_track_color = ColorProperty([1, 1, 1, 1])
    num_type = StringProperty('float')
    value = NumericProperty(0)

    def on_txt_text(self, instance, value):
        self.set_values(instance, value)                        # Assign value to value attribute of widget

    def on_txt_focus(self, instance, value):
        self.focus = value

    def set_values(self, instance, value):
        try:
            if self.num_type == 'int':
                val = min(max(int(instance.text), self.min), self.max)
                self.value = val
            elif self.num_type == 'float':
                val = min(max(float(instance.text), self.min), self.max)
                self.value = val
            self.slider.value = self.value

            self.set_txt_text_suitable()

        except ValueError:
            self.value = 0
            self.slider.value = 0

    def set_txt_text_suitable(self):
        if int(self.txt.text) < self.min:
            self.txt.text = str(self.min)
        elif int(self.txt.text) > self.max:
            self.txt.text = str(self.max)

    def on_slider_value(self, instance, value):
        if self.num_type == 'int':
            self.txt.text = str(int(value))
            self.value = int(value)
        elif self.num_type == 'float':
            self.txt.text = str(value)
            self.value = value


class Remind(FloatLayout):
    word_id = NumericProperty(-1)
    text = StringProperty('')
    secondary_text = StringProperty('')
    day = StringProperty('')
    tags = ListProperty()
    font_size_title = StringProperty('17sp')
    font_size_secondary = StringProperty('15sp')
    color = ColorProperty(get_color_from_hex('#ffffff'))
    tag_lines = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Remind, self).__init__(**kwargs)
        self.pnl_tags.bind(size=self.redraw, pos=self.redraw)           # Redraw tags

    def insert_tags(self):
        self.pnl_tags.clear_widgets()
        self.tag_objs = []
        for tag_id in self.tags:
            tag_content = App.get_running_app().get_tag_by_id(tag_id)
            tag = MiniTag(text=tag_content.name, background_color=tag_content.color, color=tag_content.text_color)
            self.tag_objs.append(tag)
            self.pnl_tags.add_widget(tag)

    def redraw(self, *args):

        def callback(dt):
            # Check if total width of tags greater than space availability

            total_width = 0                                     # Store total width of tags, including spacing
            is_removed = False                                  # Flag if total width is greater than space available

            for tag in self.tag_objs:
                if is_removed:
                    # If there is tag removed, so continue removing the rest
                    self.pnl_tags.remove_widget(tag)
                    continue

                total_width += tag.width
                total_width += self.pnl_tags.spacing[0]

                if total_width > self.pnl_tags.width * 1.5:
                    # Remove the first tag which make total width larger than space availability (1.5 times of width)
                    self.pnl_tags.remove_widget(tag)
                    is_removed = True

            if is_removed:
                # If there is removal, check availability and add some dots as a signal
                has_dots = False
                for tag in self.pnl_tags.children:
                    if tag.text == '...':
                        has_dots = True
                        break
                if not has_dots:
                    # Add dots if not existed
                    self.pnl_tags.add_widget(MiniTag(text='...', background_color=[0, 0, 0, 0], color=[0, 0, 0, 1]))

        self.insert_tags()
        Clock.schedule_once(callback)


class ContextDialog(FloatLayout):
    background_blur = NumericProperty(.5)
    name = ''

    def __init__(self, dismiss_callback, name, **kwargs):
        super(ContextDialog, self).__init__(**kwargs)
        self.name = name
        # self.btn_done.bind(on_touch_up=self.on_btn_done)
        self.dismiss_callback = dismiss_callback

    def on_btn_done(self, instance, value):
        if instance.collide_point(*value.pos):
            pass

    def dismiss(self):
        return self.dismiss_callback(self)


class MiniTag(Label):
    background_color = ColorProperty(get_color_from_hex('#ffffff'))
    radius = ListProperty([0, 0])


class RoundedToggle(FloatLayout):
    background_color = ColorProperty(get_color_from_hex('#919090'))
    background_select_color = ColorProperty(get_color_from_hex('#0000ff'))
    icon_off = StringProperty(common.get_image_path('tag_grey.png'))
    icon_on = StringProperty(common.get_image_path('tag_red.png'))
    toggle_color_value = ColorProperty(get_color_from_hex('#ffffff'))
    value = BooleanProperty(False)
    disabled = BooleanProperty(False)
    old_touch_pos = None
    width = NumericProperty(44 * 2.5 * common.scale)
    height = NumericProperty(44 * common.scale)
    size_hint = ListProperty([None, None])
    is_animation_in_progress = False
    vibrator = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(RoundedToggle, self).__init__(**kwargs)
        self.bind(size=self.redraw, pos=self.redraw)
        self.toggle_img = {False: self.icon_off, True: self.icon_on}

    def on_icon_off(self, instance, value):
        # Set toggle image (False) to icon_off
        self.toggle_img = {False: value, True: self.icon_on}

    def on_icon_on(self, instance, value):
        # Set toggle image (True) to icon_on
        self.toggle_img = {False: self.icon_off, True: value}

    def redraw(self, *args):
        try:
            self.canvas.before.clear()

            with self.canvas.before:
                if not self.value:
                    self.color = Color(rgba=self.background_color)
                    toggle_pos_x = self.x
                else:
                    self.color = Color(rgba=self.background_select_color)
                    toggle_pos_x = self.x + self.width - self.toggle_radius * 2

                self.rect = RoundedRectangle(size=(self.width, self.height / 2),
                                             pos=(self.pos[0], self.pos[1] + self.height / 4),
                                             radius=[self.height / 4,])
                self.toggle_color = Color(rgba=self.toggle_color_value)
                self.toggle_radius = self.height / 2
                self.toggle = RoundedRectangle(size=(self.height, self.height),
                                               pos=(toggle_pos_x, self.y),
                                               radius=[self.toggle_radius,])
                self.img = Rectangle(source=self.toggle_img[self.value],
                                     size=(self.height / 2, self.height / 2),
                                     pos=(self.toggle.pos[0] + self.height / 4, self.toggle.pos[1] + self.height / 4))
        except AttributeError:
            pass

    def on_touch_down(self, value):
        if self.disabled:
            # Do nothing if widget is disabled
            return

        if not self.collide_point(*value.pos):
            return

        self.old_touch_pos = value.pos

        if self.vibrator and 'iphone' in platform.platform().lower():
            vibrator.pattern([0, 2])

    def on_touch_move(self, value):
        if self.disabled:
            # Do nothing if widget is disabled
            return

        if not self.collide_point(*value.pos):
            # Do nothing if touch does not hover over widget
            return

        if not self.old_touch_pos:
            # Initial touch down was outside of this widget
            return

        if common.get_gesture_type_horizontal(self.old_touch_pos, value.pos) == 'swipe_right':
            # Move right according to touch pos
            self.toggle.pos = (min(self.x + self.width - self.toggle_radius * 2,
                                   self.toggle.pos[0] + common.get_move_distance_horizontal(self.old_touch_pos, value.pos)),
                               self.toggle.pos[1])
        elif common.get_gesture_type_horizontal(self.old_touch_pos, value.pos) == 'swipe_left':
            # Move left according to touch pos
            self.toggle.pos = (max(self.x,
                                   self.toggle.pos[0] - common.get_move_distance_horizontal(self.old_touch_pos, value.pos)),
                               self.toggle.pos[1])

        # Set icon position
        self.img.pos = (self.toggle.pos[0] + self.height / 4, self.toggle.pos[1] + self.height / 4)

    def on_touch_up(self, value):
        if self.disabled:
            # Do nothing if widget is disabled
            return

        # Handle when user touch sliderhold instead of sliding
        if self.old_touch_pos:
            if not self.collide_point(*value.pos):
                # Return because touch up outside widget
                self.old_touch_pos = None  # Reset initial touch pos
                self.move_completely()
                return

            if common.get_move_distance_horizontal(self.old_touch_pos, value.pos) < dp(5):
                # Moving in a small distance is considered as a touch only
                # Toggle value
                if not self.is_animation_in_progress:
                    self.value = not self.value
                else:
                    print('omit touch')
            else:
                # Moving distance is long enough to be a slide gesture
                self.move_completely()
        else:
            # A slide gesture
            self.move_completely()

        self.old_touch_pos = None                   # Reset initial touch pos

    def move_completely(self, base='pos'):
        if base == 'pos':
            if self.toggle.pos[0] < self.x + self.width / 2 - self.toggle_radius:
                # Animate to the left
                start_new_thread(self.slide_toggle, (self.toggle.pos[0], self.x))
                self.color.rgba = self.background_color
                self.value = False
            else:
                # Animate to the right
                start_new_thread(self.slide_toggle, (self.toggle.pos[0], self.x + self.width - self.toggle_radius * 2))
                self.color.rgba = self.background_select_color
                self.value = True
        elif base == 'value':
            if self.value:
                # Animate to the right
                start_new_thread(self.slide_toggle, (self.toggle.pos[0], self.x + self.width - self.toggle_radius * 2))
                self.color.rgba = self.background_select_color
            else:
                # Animate to the left
                start_new_thread(self.slide_toggle, (self.toggle.pos[0], self.x))
                self.color.rgba = self.background_color

        self.img.source = self.toggle_img[self.value]
        self.img.pos = (self.toggle.pos[0] + self.height / 4, self.toggle.pos[1] + self.height / 4)

    def on_value(self, instance, value):
        # Set corresponding icon
        self.move_completely(base='value')

    def slide_toggle(self, start, end, increment=10*common.scale, animation_time=.003):
        # Turn animation flag on
        self.is_animation_in_progress = True

        x = None
        if start < end:
            # Animate to the right
            while self.toggle.pos[0] < end:
                new_x = min(self.toggle.pos[0] + increment, end)
                if new_x != x:
                    x = new_x
                else:
                    break

                self.toggle.pos = (x, self.toggle.pos[1])
                self.img.pos = (self.toggle.pos[0] + self.height / 4, self.toggle.pos[1] + self.height / 4)
                time.sleep(animation_time)
        else:
            # Animate to the left
            while self.toggle.pos[0] > end:
                new_x = max(self.toggle.pos[0] - increment, end)
                if new_x != x:
                    x = new_x
                else:
                    break

                self.toggle.pos = (x, self.toggle.pos[1])
                self.img.pos = (self.toggle.pos[0] + self.height / 4, self.toggle.pos[1] + self.height / 4)
                time.sleep(animation_time)

        # Turn animation flag off
        self.is_animation_in_progress = False


class ThumbnailImage(Image):
    select = BooleanProperty(False)
    delete = BooleanProperty(False)
    is_touched_down = False

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return

        self.is_touched_down = True

    def on_touch_up(self, touch):
        self.is_touched_down = False


class BoxStencil(BoxLayout, StencilView):
    pass


class FullImage(Image):
    pass


class Tooltip(Label):
    pass


Builder.load_file(os.path.join(common.get_bundle_dir(), 'newwidgets.kv'))


class NewWidgetsApp(App):
    pass


if __name__ == '__main__':
    NewWidgetsApp().run()
