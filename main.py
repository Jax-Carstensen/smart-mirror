# Make sure you pip install these modules:
# pygame, gpiozero, psutil, requests
from config import *
import pygame
from datetime import datetime
import psutil
import os
from time import time, sleep
from requests import get
import json
import urllib.request

class Image:
    def __init__(self, name):
        self.name = name
        self.image = pygame.image.load("/home/pi/Desktop/MagicMirror/images/" + self.name + ".png")
        self.image = pygame.transform.rotate(pygame.transform.scale(self.image, (200, 200)), 90).convert_alpha()
    
class Mirror:
    def __init__(self):
        self.screen = None
        self.font = None
        self.refresh_rate = 5
        self.clock = None
        self.last_weather_time = 0
        self.time_between_weather_calls = 0.5 # In minutes
        self.main_weather = "Clouds"
        self.url = "http://api.openweathermap.org/data/2.5/weather?zip=" + str(ZIP) + ",us&APPID=" + API_KEY
        self.get_weather()
        self.weather_description = "testing"
        pygame.init()
        self.images = []
        self.screen_width = pygame.display.Info().current_w
        self.screen_height = pygame.display.Info().current_h
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 30)
        self.largeFont = pygame.font.SysFont("Arial", 65)
        self.extraLargeFont = pygame.font.SysFont("Arial", 80)
        self.connected = False
        self.icon_id = "01d"
        if DEBUG_MODE:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.get_weather(force=True)
        for root, dirs, files in os.walk("/home/pi/Desktop/MagicMirror/images/"):
            for file in files:
                self.images.append(Image(file.replace(".png", "")))
        while self.running:
            self.update()
            self.draw()
    
    def get_image(self, id):
        for image in self.images:
            if image.name == id:
                return image.image
        return None
    
    def draw_weather_icon(self, left_index, right_index):
        self.screen.blit(self.get_image(self.icon_id), (self.screen_width - cell * 2, 128))
    
    def connected_to_interwebs(self, host='http://google.com'):
        try:
            urllib.request.urlopen(host) #Python 3.x
            return True
        except:
            return False
    
    def get_weather(self, force=False):
        if not force:
            if time() - self.last_weather_time < self.time_between_weather_calls * 60:
                return
        self.last_weather_time = time()
        self.connected = self.connected_to_interwebs()
        if not self.connected:
            return
        r = get(self.url).json()
        self.weather_description = r["weather"][0]["description"]
        self.main_weather = r["weather"][0]["main"]
        self.icon_id = r["weather"][0]["icon"]
        self.temperature = self.to_fahrenheit(float(r["main"]["temp"]))
        self.min_temperature = self.to_fahrenheit(float(r["main"]["temp_min"]))
        self.max_temperature = self.to_fahrenheit(float(r["main"]["temp_max"]))
        self.town_name = r["name"]
    
    def to_fahrenheit(self, temp):
        return int(round((temp - 273) * 1.8 + 32))
    
    def draw_text(self, text, x=0, y=0, color=(255,255,255), font=None):
        if not font:
            font = self.font
        surface = font.render(text, True, color)
        surface = pygame.transform.rotate(surface, 90)
        self.screen.blit(surface, (x, y))
    
    def draw_weather(self):
        if not self.connected:
            self.draw_text("Please connect to the internet", 0, self.screen_height - self.font.size("Please connect to the internet")[0], font=self.font)
            return
        #Draw your town's name
        self.draw_text(self.town_name, 0, self.screen_height - self.largeFont.size(self.town_name)[0], font=self.largeFont)
        #Draw the weather icon
        img = self.get_image(self.icon_id)
        if img != None:
            self.screen.blit(img, (48, self.screen_height - 200))
        #Draw the temperature
        degree = u"\N{DEGREE SIGN}"
        temp_text = str(self.temperature) + degree + "f"
        min_text = str(self.min_temperature) + degree + "f"
        max_text = str(self.max_temperature) + degree + "f"

        self.draw_text(temp_text, 112, self.screen_height - 200 - self.largeFont.size(temp_text)[0] * 1.25, font=self.largeFont)
        self.draw_text(min_text, 196, self.screen_height - 200 - self.font.size(min_text)[0] * 1.15)
        self.draw_text(max_text, 196, self.screen_height - 200 - self.font.size(min_text)[0] * 2.85)
        y = self.screen_height - 100 - self.font.size(self.weather_description)[0] * 0.5
        if y + self.font.size(self.weather_description)[0] > 1080:
            y = 1080 - self.font.size(self.weather_description)[0]
        self.draw_text(self.weather_description, 256, y)
    
    def draw_time(self):
        rn = datetime.now()
        self.draw_text(rn.strftime("%A"), 0, 0, font=self.largeFont)
        t = int(datetime.now().strftime("%H"))
        extra = "A.M."
        if t > 12:
            t -= 12
            extra = "P.M."
        t = str(t)
        self.draw_text(t + rn.strftime(":%M:%S"), 72, 0, font=self.extraLargeFont)
        self.draw_text(datetime.now().strftime("%m/%d/%Y"), 156, 0)
        #self.draw_text(rn.strftime("%d/%m/%Y"), 72, self.largeFont.size(rn.strftime("%d/%m/%Y"))[0] * 0.55, font=self.largeFont)
        return
        self.draw_text(datetime.now().strftime("%d/%m/%Y"), 40, 40)
        t = int(datetime.now().strftime("%H"))
        extra = "A.M."
        if t > 12:
            t -= 12
            extra = "P.M."
        self.draw_text(str(t) + datetime.now().strftime(":%M:%S"), 100, 95, font=self.largeFont)
        self.draw_text(extra, 130, 30)
    
    def draw(self):
        self.screen.fill((0,0,0))
        self.draw_time()
        self.draw_weather()
        pygame.display.update()
        self.clock.tick(self.refresh_rate)
    #pygame.transform.rotate(surface, angle)
    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()

    def update(self):
        self.manage_events()
        self.get_weather()

mirror = Mirror()
mirror.start()
