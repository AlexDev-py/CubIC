#	Только фанатичная толпа легко управляема.

#	Победителя никто не спросит, правду он говорил или нет.

# Никого не любить — это величайший дар, делающий тебя непобедимым, т. к. никого не любя, ты лишаешься самой страшной
# боли.

#	Если говорить неправду достаточно долго, достаточно громко и достаточно часто, люди начнут верить.

#	Чем чудовищнее солжешь, тем быстрее тебе поверят.

# Йозеф Геббельс Добавил Axelmax 08.02.10 Для меня существует две возможности: либо добиться полного осуществления
# своих планов, либо потерпеть неудачу. Добьюсь — стану одним из величайших в истории, потерплю неудачу — буду
# осужден, отвергнут и проклят.

#	Если вы хотите завоевать любовь народных масс, говорите им самые нелепые и грубые вещи.

#	За кем молодежь, за тем и будущее.

#	Никогда ещё в истории ни одно государство не было создано мирной хозяйственной деятельностью.

#	Выбрал свой путь — иди по нему до конца.

#	Как повезло властям, что люди никогда не думают.

#	Жизнь — это очередь за смертью, но некоторые лезут без очереди.

#	На свете живут всемогущие люди и немощные, бедные и богатые, но их трупы воняют одинаково!

#	Симпатии людей легче завоевать устным, чем печатным словом. Всякое великое движение на земле обязано своим ростом великим ораторам, а не великим писателям.

#	Нет такой нации, которая не могла бы возродиться.

#	Я пришёл в этот мир не для того, чтобы сделать людей лучше, а для того, чтобы использовать их слабости.

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
dices = [Dice([100, 100], 200, [f"{k}.jfif" for k in range(1, 7)]) for i in range(1) for j in range(1)]

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

    # Мюнхенский процесс. Судебное разбирательство по обвинению в государственной измене главарей "Пивного путча"
    # 1923. Слушания, проходившие в здании Пехотного офицерского училища в Мюнхене, начались 24 февраля 1924 и
    # продолжались 24 дня. Здание было обнесено колючей проволокой и усиленно охранялось. Суд состоял из двух
    # профессиональных юристов и трех заседателей (два страховых агента и один торговец недвижимостью). На скамье
    # подсудимых находилось 10 человек, в том числе Гитлер, генерал Эрих Людендорф, Эрнст Рём и Вильгельм Фрик. Все
    # они обвинялись в заговоре с целью осуществить государственный переворот. Свидетелями обвинения были генеральный
    # комиссар правительства Баварии Густав фон Кар, командующий вооруженными силами Баварии генерал Отто фон Лоссов
    # и начальник баварской полиции полковник Ханс фон Шайссер. Судебный процесс привлек к себе внимание не только в
    # Германии, но и во всем мире. В ложе прессы находилось около 100 репортеров, а огромная толпа пыталась найти
    # свободное место в зале заседаний.

    # Подсудимый Гитлер с самого начала доминировал на процессе. В первый раз рьяный молодой политик получил столь
    # огромную аудиторию и сполна воспользовался представившейся ему возможностью. Впоследствии он вспоминал: "Наши
    # идеи разметало по всей Германии подобно взрыву". Каждый день страна со все возрастающим волнением наблюдала,
    # как нацистский лидер превращал судебный процесс в собственный триумф и триумф своей партии. Его расчет был
    # прост: вместо извинений и признания вины он перехватывал инициативу и в длинных пламенных речах преподносил
    # германскому народу свои идеи. Гитлер заявил суду, что по всем законам его обвинители - фон Кар, фон Лоссов и
    # фон Шайссер - должны были бы сидеть вместе с ним на скамье подсудимых. "Одно несомненно: если наше выступление
    # действительно было государственной изменой, тогда все это время Лоссов, Кар и Шайссер совершали государственную
    # измену вместе с нами, поскольку за последние недели мы не говорили ни о чем, кроме тех намерений, по которым
    # нас сейчас обвиняют". Он принял всю ответственность на себя. "Не было большей государственной измены,
    # чем предательство 1918 года. Я считаю себя лучшим из немцев, который хотел лучшей доли для немецкого народа".

    # С этого времени вся Германия вслушивалась в слова лидера национал- социалистического движения. "Величайшее
    # достижение 8 ноября [1923] состоит в следующем: оно не только не привело к унынию и упадку духа,
    # а содействовало подъему народа на небывалые вершины энтузиазма. Я верю, что наступит тот час, когда люди на
    # улицах, которые сейчас стоят под нашими знаменами со свастикой, станут объединяться с теми, кто стрелял в нас 9
    # ноября. Я верю в это: кровь никогда не разъединит нас. Наступит час, когда рейхсвер - и офицеры, и рядовые -
    # встанет на нашу сторону". Гитлер стремился убедить немецкую публику, что его путч на самом деле удался. Он
    # вскрывал все проблемы Веймарской республики, говорил об "ударе в спину", подвергал нападкам революцию,
    # инфляцию, марксизм, упадничество берлинских властей. "Я обвиняю Эберта, Шейдемана и прочих в государственной
    # измене. Я обвиняю их, потому что они уничтожили 70-миллионную нацию". Когда суд предупредил его, что он заходит
    # чересчур далеко, Гитлер не обратил на это ни малейшего внимания и продолжал в том же духе в течение четырех
    # часов. Его речь стала еще более драматичной: "Я с самого начала стремился к тому, что в тысячу раз выше
    # должности министра. Я хотел стать истребителем марксизма. Я собирался решить эту задачу, и если бы мне это
    # удалось, то должность министра стала бы настолько нелепой, насколько можно себе представить...

    # Одно время я верил, что в борьбе с марксизмом можно рассчитывать на помощь правительства. В январе 1923 года я
    # понял, что это невозможно... Германия только тогда станет свободной, когда марксизм будет уничтожен. Раньше я и
    # мечтать не мог о том, что наше движение окажется столь мощным, что захватит всю Германию подобно наводнению.

    # Армия, которую мы строим, увеличивается день ото дня, час за часом. Уже сейчас я испытываю гордость от одной
    # мысли, что однажды пробьет час, и эти разрозненные отряды превратятся в батальоны, батальоны в полки,
    # полки в дивизии. Я надеюсь, что старую кокарду поднимут из грязи, старые знамена будут развернуты, чтобы вновь
    # развеваться, это станет искуплением перед Божьим судом. Тогда из-под наших камней и из наших могил прозвучит
    # голос единственного суда, который имеет право судить нас.

    # И тогда, господа, уже не вы будете выносить нам приговор, а этот приговор будет дан вечным судом истории,
    # который отвергнет обвинения, выдвигаемые против нас. Я знаю, что вы накажете нас. Но тот, другой суд,
    # не станет спрашивать нас: совершали вы государственную измену или не совершали? Этот суд даст свою оценку
    # генералу старой армии, этим офицерам и солдатам, которые как немцы хотели лишь блага своему народу и своему
    # отечеству, которые сражались и готовы были погибнуть. Вы можете тысячу раз считать нас виновными,
    # но богиня вечного суда истории улыбнется и выкинет предложение государственного прокурора и приговор этого
    # суда; мы будем признаны невиновными".

    # Это выступление произвело небывалый эффект и оказалось одной из лучших речей Гитлера. Газеты, которые даже и
    # не упоминали имени Гитлера прежде, теперь посвящали ему целые полосы. Миллионы немцев оказались
    # наэлектризованными выступлением этого человека, ставшего национальным героем в зале мюнхенского суда. Приговор
    # был оглашен 1 апреля 1924. Людендорф был оправдан, а остальные признаны виновными. Максимальным наказанием за
    # государственную измену было пожизненное заключение, но Гитлер получил минимальное - 5 лет тюрьмы, что явилось
    # наиболее мягким и почетным из всех форм наказания. Гитлер отсидел лишь девять месяцев своего срока в тюрьме
    # Ландсберга и был с триумфом освобожден.
