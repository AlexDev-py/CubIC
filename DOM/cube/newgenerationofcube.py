import random
from random import randint

import numpy
import pygame as pg
import sys
import math

import pygame.draw

W = 400
H = 400
WHITE = (255, 255, 255)


class Dice(pg.sprite.Sprite):
    def __init__(self, start_pos, dice_size, filenames):
        super(Dice, self).__init__()
        self.dice_size = dice_size
        self.start_pos = start_pos
        self.image = pg.Surface((dice_size, dice_size))
        self.rect = self.image.get_rect()
        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]

        self.filenames = filenames
        self.rotations_trigers = [False, False, False, False]
        self.counters = [0, 0]

        self._reconers()

        self.speed = 10

        self.visible_coners = [self.all_coners[0].copy()]

        self.graph = [[4, 1, 3, 2],
                      [0, 5, 3, 2],
                      [4, 1, 0, 5],
                      [4, 1, 5, 0],
                      [5, 0, 3, 2],
                      [1, 4, 3, 2]]

        self.visible_images = [0]

        self._prerender()

        self.move_stack = []

    def _reconers(self):
        ul, ur, dl, dr = self.start_pos, [self.start_pos[0] + self.dice_size, self.start_pos[1]], [self.start_pos[0],
                                                                                                   self.start_pos[
                                                                                                       1] + self.dice_size], [
                             self.start_pos[0] + self.dice_size, self.start_pos[1] + self.dice_size]
        self.all_coners = [[ul.copy(), dl.copy(), dr.copy(), ur.copy()],
                           [ul.copy(), dl.copy(), dl.copy(), ul.copy()],
                           [ur.copy(), dr.copy(), dr.copy(), ur.copy()],
                           [ul.copy(), ul.copy(), ur.copy(), ur.copy()],
                           [dl.copy(), dl.copy(), dr.copy(), dr.copy()]]

    def _prerender(self):
        self.dices = []
        for i in self.filenames:
            img = pg.image.load(i)
            self.dices.append(img)

    def key_event(self, event):
        if event.key == pg.K_LEFT and not (any(self.rotations_trigers)):
            self.move_left()
        if event.key == pg.K_RIGHT and not (any(self.rotations_trigers)):
            self.move_right()
        if event.key == pg.K_UP and not (any(self.rotations_trigers)):
            self.move_up()
        if event.key == pg.K_DOWN and not (any(self.rotations_trigers)):
            self.move_down()

        if event.key == pygame.K_SPACE:
            self.randome_moving(10)

    def move_left(self):
        self.visible_coners.append(self.all_coners[2].copy())
        self.rotations_trigers[1] = True
        self.visible_images.append(self.graph[self.visible_images[0]][1])
        arr = self.graph[self.graph[self.visible_images[0]][1]]
        curindex = self.visible_images[0]
        step = arr.index(curindex)

        nym = numpy.array(arr)

        arr = list(numpy.roll(nym, 1 - curindex))

    def move_right(self):
        self.visible_coners.append(self.all_coners[1].copy())
        self.rotations_trigers[0] = True
        self.visible_images.append(self.graph[self.visible_images[0]][0])
        arr = self.graph[self.graph[self.visible_images[0]][1]]
        curindex = self.visible_images[0]
        step = arr.index(curindex)

        nym = numpy.array(arr)

        arr = list(numpy.roll(nym, 0 - curindex))

    def move_up(self):
        self.visible_coners.append(self.all_coners[4].copy())
        self.rotations_trigers[3] = True
        self.visible_images.append(self.graph[self.visible_images[0]][3])
        arr = self.graph[self.graph[self.visible_images[0]][1]]
        curindex = self.visible_images[0]
        step = arr.index(curindex)

        nym = numpy.array(arr)

        arr = list(numpy.roll(nym, 2 - curindex))

    def move_down(self):
        self.visible_coners.append(self.all_coners[3].copy())
        self.rotations_trigers[2] = True
        self.visible_images.append(self.graph[self.visible_images[0]][2])
        arr = self.graph[self.graph[self.visible_images[0]][1]]
        curindex = self.visible_images[0]
        step = arr.index(curindex)

        nym = numpy.array(arr)

        arr = list(numpy.roll(nym, 3 - curindex))

    def update(self):
        if self.rotations_trigers[0]:
            if self.counters[0] < self.dice_size / 2:
                self.visible_coners[0][2][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][3][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][0][0] += 1 * self.speed
                self.visible_coners[0][1][0] += 1 * self.speed
                self.visible_coners[1][0][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][1][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][2][0] += 1 * self.speed
                self.visible_coners[1][3][0] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.dice_size / 2 and self.counters[0] < self.dice_size:
                self.visible_coners[0][2][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][3][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][0][0] += 1 * self.speed
                self.visible_coners[0][1][0] += 1 * self.speed
                self.visible_coners[1][0][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][1][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][2][0] += 1 * self.speed
                self.visible_coners[1][3][0] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] == self.dice_size:
                self.rotations_trigers[0] = False
                self.visible_coners = self.visible_coners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._reconers()

        if self.rotations_trigers[1]:
            if self.counters[0] < self.dice_size / 2:
                self.visible_coners[0][0][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][1][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][2][0] -= 1 * self.speed
                self.visible_coners[0][3][0] -= 1 * self.speed
                self.visible_coners[1][2][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][3][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][0][0] -= 1 * self.speed
                self.visible_coners[1][1][0] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.dice_size / 2 and self.counters[0] < self.dice_size:
                self.visible_coners[0][0][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][1][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][2][0] -= 1 * self.speed
                self.visible_coners[0][3][0] -= 1 * self.speed
                self.visible_coners[1][2][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][3][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][0][0] -= 1 * self.speed
                self.visible_coners[1][1][0] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] == self.dice_size:
                self.rotations_trigers[1] = False
                self.visible_coners = self.visible_coners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._reconers()
        if self.rotations_trigers[2]:
            if self.counters[0] < self.dice_size / 2:
                self.visible_coners[0][1][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][2][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][0][1] += 1 * self.speed
                self.visible_coners[0][3][1] += 1 * self.speed
                self.visible_coners[1][0][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][3][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][1][1] += 1 * self.speed
                self.visible_coners[1][2][1] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.dice_size / 2 and self.counters[0] < self.dice_size:
                self.visible_coners[0][1][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][2][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][0][1] += 1 * self.speed
                self.visible_coners[0][3][1] += 1 * self.speed
                self.visible_coners[1][0][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][3][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][1][1] += 1 * self.speed
                self.visible_coners[1][2][1] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] == self.dice_size:
                self.rotations_trigers[2] = False
                self.visible_coners = self.visible_coners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._reconers()
        if self.rotations_trigers[3]:
            if self.counters[0] < self.dice_size / 2:
                self.visible_coners[0][0][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][3][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][1][1] -= 1 * self.speed
                self.visible_coners[0][2][1] -= 1 * self.speed
                self.visible_coners[1][1][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][2][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][0][1] -= 1 * self.speed
                self.visible_coners[1][3][1] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.dice_size / 2 and self.counters[0] < self.dice_size:
                self.visible_coners[0][0][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][3][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_coners[0][1][1] -= 1 * self.speed
                self.visible_coners[0][2][1] -= 1 * self.speed
                self.visible_coners[1][1][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][2][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_coners[1][0][1] -= 1 * self.speed
                self.visible_coners[1][3][1] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] == self.dice_size:
                self.rotations_trigers[3] = False
                self.visible_coners = self.visible_coners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._reconers()
        if self.rotations_trigers == [False, False, False, False] and len(self.move_stack) > 0:
            self.next_moving()

    def randome_moving(self, x):
        self.move_stack = [[[True, False, False, False],
                            [False, True, False, False],
                            [False, False, True, False],
                            [False, False, False, True]][random.randint(0, 3)] for _ in range(x)]

    def next_moving(self):
        current = self.move_stack.pop(0)
        if current[0]:
            self.move_right()
        if current[1]:
            self.move_left()
        if current[2]:
            self.move_down()
        if current[3]:
            self.move_up()

    def display(self, sc):
        for i in range(len(self.visible_coners)):
            polygon = self.visible_coners[i]
            dsize = (round(abs(polygon[0][0] - polygon[2][0])) + 1, round(abs(polygon[0][1] - polygon[2][1])) + 1)
            sc.blit(pg.transform.scale(self.dices[self.visible_images[i]], dsize), polygon[0])
        print("")


sc = pg.display.set_mode((W, H))

# координата x будет случайна
dices = [Dice([100, 100], 200, [f"{k}.png" for k in range(1, 7)]) for i in range(1) for j in range(1)]

while 1:
    for i in pg.event.get():
        if i.type == pg.QUIT:
            sys.exit()
        if i.type == pg.KEYDOWN:
            [dice.key_event(i) for dice in dices]

    sc.fill("cyan")
    [dice.display(sc) for dice in dices]
    pg.display.update()
    pg.time.delay(20)

    [dice.update() for dice in dices]


