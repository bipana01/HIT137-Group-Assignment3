import os

import pygame


BASE_IMG_PATH = 'data/images/'


def load_image(path):
    # make rendering more efficient
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))  # Make pure black transparent
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images



class Animation:
    """
    Animation is all about just showing different 
    images at different times
    """
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        # not a simple frame++
        if self.loop:
            self.frame =(self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
                
    def img(self):
        # will increase by 1 every single time as frames increases
        # division gives us the index of the imag we should have
        return self.images[int(self.frame / self.img_duration)]
