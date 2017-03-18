import datetime
from math import cos, sin, pi
import math
import time

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix import layout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.drag import DragBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line


Builder.load_file('smartmirror.kv')
Builder.load_file('headerspace.kv')
Builder.load_file('bodyspace.kv')
Builder.load_file('footerspace.kv')



class Thermostat(Widget):
    angle = NumericProperty(0)
    minTemp = 20
    maxTemp = 40
    actualTemp = NumericProperty(None)
    tempText = StringProperty(None)
    
    def __init__(self, **kwargs):
        super(Thermostat, self).__init__(**kwargs)
        self.pos_hint= {"center_x":0.5, "center_y":0.5}
        self.actualTemp = 32
        self.tempText = self.getCurrentTempAsString()

    def getCurrentTempAsString(self):
        return str(round(self.actualTemp, 1)) + "\xb0"      

    def on_touch_down(self, touch):
        return super(Thermostat, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            y = (touch.y - self.center_y)
            x = (touch.x - self.center_x)
            
            calc = math.degrees(math.atan2(y, x))
            new_angle = calc if calc > 0 else 360+calc
            
            if new_angle < 180:           
                # Change Color
                self.changeBgColor(new_angle)
                # set new temperature text
                self.tempText = self.getCurrentTempAsString()
                # Move Line
                self.drawTempLines(new_angle)
                
        return super(Thermostat, self).on_touch_move(touch)

    def drawTempLines(self, newAngle):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(1, 1, 1)
            Line(points=[self.center_x+(self.height/2-15)*cos(pi/180*newAngle), self.center_y+(self.width/2-15)*sin(pi/180*newAngle), self.center_x+100*cos(pi/180*newAngle), self.center_y+100*sin(pi/180*newAngle)], width=5, cap="round")
            for i in range(72):
                newAngle += 5
                Line(points=[self.center_x+(self.height/2-15)*cos(pi/180*newAngle), self.center_y+(self.width/2-15)*sin(pi/180*newAngle), self.center_x+110*cos(pi/180*newAngle), self.center_y+110*sin(pi/180*newAngle)], width=2, cap="round")
            
    
    def changeBgColor(self, newAngle):
        newTemp = newAngle / (180 / (self.maxTemp - self.minTemp))
        self.actualTemp = self.maxTemp - newTemp 
        mediumTemp = (self.maxTemp - self.minTemp) / 2 + self.minTemp
        colorRed = 0.3 + ((self.actualTemp - mediumTemp) / (self.maxTemp - mediumTemp) * 0.7)
        belowAv = (self.actualTemp - mediumTemp) *-1
        colorBlue = 0.3 + (belowAv / (mediumTemp - self.minTemp) * 0.7)
        self.color = (colorRed, 0.3, colorBlue, 1)

    def on_touch_up(self, touch):
        pass


class PowerButton(Image):
   
    susi = ObjectProperty(None)
    isOn = True
    susiStartHeight = None
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.susiStartHeight == None:
                self.susiStartHeight = self.susi.height
            if self.isOn:
                Animation(color=(0,0,0,1), size=(self.susi.width, self.susiStartHeight)).start(self.susi)
                self.isOn = False
            else:
                Animation(color=(0,0,0,0), size=(self.susi.width, 0)).start(self.susi)
                self.isOn = True
        return Image.on_touch_down(self, touch)

class SuspendScreen(FloatLayout):
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return True

class ProductImage(Image):
       
    def __init__(self, **kwargs):
        super(ProductImage, self).__init__(**kwargs)
        self.onOff = True
        self.background = None
        self.isOnMove = False

    def on_touch_down(self, event):
        return super(ProductImage, self).on_touch_up(event)
    
    def on_touch_move(self, event):
        if self.collide_point(event.x, event.y) and time.time() - event.time_start > 0.6:
            self.isOnMove = True
            self.center = event.pos
            if self.background:
                self.background.pos = (event.x-self.width/2, event.y-self.height/2)
            return True
        return Image.on_touch_move(self, event)
        
    def on_touch_up(self, event):
        if self.collide_point(*event.pos) and self.isOnMove == False:
            self.toggleImage()
        self.isOnMove = False
        return Image.on_touch_up(self, event)
    
    def toggleImage(self):
        if self.onOff == True:
            self.source = 'img/' + self.filename + '_off.png'
            with self.canvas.before:
                self.background = Ellipse(pos=self.pos, size=self.size)
            self.onOff = False
        else:
            self.source = 'img/' + self.filename + '_on.png'
            self.canvas.before.remove(self.background)
            self.onOff = True

class SimpleClock(Label):
    
    timetext = StringProperty()

    def __init__(self, **kwargs):
        super(SimpleClock, self).__init__(**kwargs)
        self.update()
        Clock.schedule_interval(self.update, 1)
        
    def update(self, *args):
        self.timetext = time.asctime()


class SmartMirror(FloatLayout):
    
    blackScreen = None
    
    def configure(self):
        Window.size = (1920, 1080)
        Window.exit_on_escape = 1
        Window.borderless = True
        
    def hide_screen(self):
        print('asd')


class SmartMirrorApp(App):
    
    def build(self):         
        smartMirror = SmartMirror()
        smartMirror.configure()
        return smartMirror


if __name__ == '__main__':
    SmartMirrorApp().run()