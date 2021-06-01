# Make sure you pip install these modules:
# pygame, gpiozero, psutil, requests
from config import *
import pygame
from gpiozero import CPUTemperature, LoadAverage
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
        self.image = pygame.image.load(f"images/{self.name}.png")
    
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
        self.connected = False
        self.icon_id = "01d"
        for root, dirs, files in os.walk("./images/"):
            for file in files:
                self.images.append(Image(file.replace(".png", "")))
        self.image_width = self.images[0].image.get_rect().size[0] * 0.98
        self.image_height = self.images[0].image.get_rect().size[1]
        if DEBUG_MODE:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.get_weather(force=True)
        while self.running:
            self.update()
            self.draw()
    
    def get_image(self, id):
        for image in self.images:
            if image.name == id:
                return image.image
        return None
    
    def draw_weather_icon(self, left_index, right_index):
        cell = self.image_width / 3
        self.cell_size = cell
        rect = (cell * left_index + 16, cell * right_index + 16, cell, cell)
        self.screen.blit(self.get_image(self.icon_id), (self.screen_width - cell * 2, 128), rect)
    
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
    
    def draw_dev_info(self):
        return
        if not DEBUG_MODE:
            return
        start_x = 0
        start_y = self.screen_height - 300
        CPU_temp = CPUTemperature().temperature
        CPU_percentage = psutil.cpu_percent()
        used_ram = round(psutil.virtual_memory()[3] / 1024 / 1024, 2)
        self.draw_text("Temp: " + str(int(CPU_temp)) + "C", start_x, start_y)
        self.draw_text("CPU:  " + str(CPU_percentage) + "%", start_x, start_y + 40)
        self.draw_text("RAM:  " + str(used_ram) + "MB (" + str(psutil.virtual_memory()[2]) + "%)", start_x, start_y + 80)
    
    def draw_weather(self):
        #Draw your town's name
        self.draw_text(self.town_name, 0, self.screen_height - self.largeFont.size(self.town_name)[0], font=self.largeFont)
        #Draw the weather icon
        self.screen.blit(self.get_image(self.icon_id), (128, self.screen_height - self.image_width))
        return
        if self.main_weather == "Clouds":
            self.draw_weather_icon(0, 0)
        elif self.main_weather == "Rain":
            self.draw_weather_icon(0, 2)
        else:
            self.draw_weather_icon(0, 0)
        self.draw_text(f"{self.temperature}°F", 1720, 128, font=self.largeFont)
        to_draw = self.weather_description
        if not self.connected:
            to_draw = "Please connect to the internet"
        self.draw_text(to_draw, self.screen_width - self.cell_size, 128 + self.cell_size)
    
    def draw_time(self):
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
        self.draw_dev_info()
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