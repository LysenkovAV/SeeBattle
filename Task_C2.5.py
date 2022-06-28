import copy # для использования функции копирования классов и списков
from random import randint # функция генерирует случайные целые числа в заданном диапазоне

BOARD_SIZE = 6 # размер игрового поля

EMP = 'O' # символ пустой клетки на поле
SHP = chr(9632) # символ корабля на поле
MIS = 'T' # символ промаха
HIT = 'X' # символ попадания в корабль
CON = '-' # символ контура вокруг корабля (по правилам там не может быть другого корабля)
SEC = chr(9671) # символ скрытой клетки на поле (поле противника еще не открыто)

BOAT = 1 # длина катера
CRUISER = 2 # длина крейсера
BATTLESHIP = 3 # длина линкора

NUMBER_BOAT = 4 # количество катеров на поле
NUMBER_CRUISER = 2 # количество крейсеров на поле
NUMBER_BATTLESHIP = 1 # количество линкоров на поле

CYCLE_ATTEMPT = 1000 # количество попыток

# собственный класс исключений - выход координат точки за пределы поля
class BoardOutException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'BoardOutException, {0} '.format(self.message)
        else:
            return 'Координаты выходят за границы доски!\n' # текст, который выводится по умолчанию

# собственный класс исключений - неправильно выбранная точка на поле
# (в эту точку либо уже был ход, либо там не может быть корабля по правилам игры)
class WrongDotException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'WrongDotException, {0} '.format(self.message)
        else:
            return 'Выберите другую точку для хода!\n' # текст, который выводится по умолчанию

# класс точек на поле
class Dot:
    def __init__(self, x=1, y=1):
        self.x = x
        self.y = y

    # метод сравнения двух точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# класс кораблей
class Ship:
    def __init__(self, len=1, start_dot=Dot(), dir=0, lives=1):
        self.len = len # длина корабля
        self.start_dot = copy.deepcopy(start_dot) # точка "носа" корабля
        self.dir = dir # направление корабля: 0 - горизонтальное, 1 - вертикальное
        self.lives = lives # количество неподбитых точек корабля

    # метод возвращения всех точек корабля в виде списка
    def dots(self):
        if self.dir:
            return [Dot(self.start_dot.x + i, self.start_dot.y) for i in range(self.len)]
        else:
            return [Dot(self.start_dot.x, self.start_dot.y + i) for i in range(self.len)]


# класс игровых полей
class Board:
    # задание начального состояния массива точек поля
    _dots_status = [[EMP for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
    # инициализация поля
    def __init__(self, hid=False, living_ships=0, ships_list=[], dots_status=_dots_status):
        self.hid = hid # скрыть/показать поле
        self.living_ships = living_ships # количество живых кораблей
        self.ships_list = copy.deepcopy(ships_list)  # список кораблей на поле
        self.dots_status = copy.deepcopy(dots_status) # массив с состояниями точек поля

    # метод установки корабля на поле
    def add_ship(self, ship):
        dots_list = copy.deepcopy(ship.dots()) # получение координат всех точек корабля на поле в виде списка
        if dots_list[0].x > 1:
            x_1 = dots_list[0].x - 1
        else:
            x_1 = dots_list[0].x
        if dots_list[0].y > 1:
            y_1 = dots_list[0].y -1
        else:
            y_1 = dots_list[0].y
        if dots_list[-1].x < BOARD_SIZE:
            x_2 = dots_list[-1].x + 1
        else:
            x_2 = dots_list[-1].x
        if dots_list[-1].y < BOARD_SIZE:
            y_2 = dots_list[-1].y + 1
        else:
            y_2 = dots_list[-1].y
        for i in range(x_1, x_2+1):
            for j in range(y_1, y_2+1):
                if self.dots_status[i-1][j-1] == SHP:
                    return False
        # изменение состояния точек поля - установка корабля на поле
        for i in range(len(dots_list)):
            self.dots_status[dots_list[i].x-1][dots_list[i].y-1] = SHP
        self.living_ships += 1 # количество кораблей увеличилось на 1
        self.ships_list.append(ship)  # добавление корабля к списку кораблей поля
        return True # корабль успешно установлен на поле

    # метод вывода поля в консоль (в зависимости от свойства hid)
    def output_board(self):
        print("           ", end='')
        for c in range(BOARD_SIZE): print(c+1, end=' ')
        print()
        # если поле не должно быть скрыто (поле пользователя), то выводим все точки как есть
        if not self.hid:
            for i in range(BOARD_SIZE):
                print("        ", i+1, '', end='')
                for j in range(BOARD_SIZE):
                    print(self.dots_status[i][j], end=' ')
                print()
            print()
        # если поле должно быть скрыто (доска ИИ), то выводим только открытые точки
        else:
            for i in range(BOARD_SIZE):
                print("        ", i+1, '', end='')
                for j in range(BOARD_SIZE):
                    if self.dots_status[i][j] not in [MIS, HIT, CON]:
                        print(SEC, end=' ')
                    else:
                        print(self.dots_status[i][j], end=' ')
                print()
            print()

    # метод прорисовки контрура вокруг корабля на поле
    def contour(self, ship, set=True):
        dots_list = ship.dots() # получение координат всех точек корабля на поле в виде списка
        current_state = CON if set else EMP # с помощью этого флага контур либо прорисовывается, либо убирается
        # цикл прорисовки контура вокруг каждой точки корабля
        for i in range(len(dots_list)):
            x = dots_list[i].x - 1 # координата точки по горизонтали
            y = dots_list[i].y - 1 # координата точки по вертикали
            # прорисовка контура вокруг точки с координатами x, y
            # с проверкой выхода за пределы поля и с проверкой статуса точек
            if x > 0 and y > 0 and self.dots_status[x-1][y-1] in [EMP, CON]:
                self.dots_status[x-1][y-1] = current_state
            if y > 0 and self.dots_status[x][y-1] in [EMP, CON]:
                self.dots_status[x][y-1] = current_state
            if x < BOARD_SIZE-1 and y > 0 and  self.dots_status[x+1][y-1] in [EMP, CON]:
                self.dots_status[x+1][y-1] = current_state
            if x > 0 and self.dots_status[x-1][y] in [EMP, CON]:
                self.dots_status[x-1][y] = current_state
            if x < BOARD_SIZE-1 and self.dots_status[x+1][y] in [EMP, CON]:
                self.dots_status[x+1][y] = current_state
            if x > 0 and y < BOARD_SIZE-1 and self.dots_status[x-1][y+1] in [EMP, CON]:
                self.dots_status[x-1][y+1] = current_state
            if y < BOARD_SIZE-1 and self.dots_status[x][y+1] in [EMP, CON]:
                self.dots_status[x][y+1] = current_state
            if x < BOARD_SIZE-1 and y < BOARD_SIZE-1 and self.dots_status[x+1][y+1] in [EMP, CON]:
                self.dots_status[x+1][y+1] = current_state

    # метод проверки выхода точки за пределы поля
    def out(self, checked_dot):
        if (1 <= checked_dot.x <= BOARD_SIZE) and (1 <= checked_dot.y <= BOARD_SIZE):
            return False # если проверяемая точка в пределах поля
        else:
            return True # если проверяемая точка за пределами поля

    # метод выстрела
    def shot(self, checked_dot):
        x = checked_dot.x - 1 # координата точки по горизонтали
        y = checked_dot.y - 1 # координата точки по вертикали
        if self.out(checked_dot): # если координаты выходят за пределы поля
            raise BoardOutException # вызов соответствующего исключения
        elif self.dots_status[x][y] == EMP: # если точка пустая
            self.dots_status[x][y] = MIS # установка статуса промаха
            return False
        elif self.dots_status[x][y] == SHP: # если был корабль
            for i in range(len(self.ships_list)):
                if checked_dot in self.ships_list[i].dots():
                    self.ships_list[i].lives -= 1 # уменьшение количества жизней корабля
                    self.dots_status[x][y] = HIT  # установка статуса попадания в корабль
                    if self.ships_list[i].lives == 0: # если у корабля не осталось жизней
                        self.living_ships -= 1 # уменьшение количества живых кораблей на доске
                        self.contour(self.ships_list[i], True) # прорисовка контура вокруг подбитого корабля
                        self.ships_list.pop(i) # исключение корабля из списка кораблей поля
                    break
            return True
        elif self.dots_status[x][y] in [MIS, HIT, CON]: # если в эту точку уже был ход или туда ходить нельзя
            raise WrongDotException # вызов соответствующего исключения


# класс игроков
class Player:
    def __init__(self, own_board=Board(), enemy_board=Board(True)):
        self.own_board = copy.deepcopy(own_board) # собственное поле
        self.enemy_board = copy.deepcopy(enemy_board) # поле ИИ

    # метод запроса точки на поле для хода
    def ask(self):
        return Dot()

    # метод хода игрока
    def move(self):
        try:
            checked_dot = self.ask()  # запрос точки для хода
            if self.enemy_board.shot(checked_dot): # выстрел
                print("Точное попадание!\n")
                return (True, "") # было попадание в корабль противника
            else:
                print("Мимо!\n")
                return (False, "") # не было попадания в корабль противника
        except BoardOutException as b: # если координаты точки выходят за пределы поля
            print(b)
            return (True, b)
        except WrongDotException as w: # если ход в указанную точку не допутим по правилам игры
            print(w)
            return (True, w)
        except ValueError as v: # если введен неверный формат координат точки
            print("Введен неверный формат координат точки!\n")
            return (True, v)


# класс игрока-компьютера (ИИ)
class AI(Player):
    def ask(self):
        temp_dot = copy.deepcopy(Dot(randint(1, BOARD_SIZE), randint(1, BOARD_SIZE))) # генерация случайных координат
        print("ИИ делает ход в точку с координатами:", temp_dot.x, temp_dot.y, '\n')
        return temp_dot


# класс игрока-пользователя
class User(Player):
    def ask(self):
        x, y = map(int, list(input(f'Введите координаты: ').split(' '))) # пользователь вводит координаты через пробел
        print('')
        return Dot(x, y)


# класс игры
class Game:
    def __init__(self, user_1=User(), user_2=AI()):
        self.user_1 = copy.deepcopy(user_1) # игрок 1 - пользователь
        self.user_1.own_board = copy.deepcopy(self.random_board()) # генерация поля пользователя
        self.user_2 = copy.deepcopy(user_2) # игрок 2 - ИИ
        self.user_2.own_board = copy.deepcopy(self.random_board()) # генерация поля ИИ

    # метод формирования случайного поля
    def random_board(self):
        temp_board = copy.deepcopy(Board())
        f = CYCLE_ATTEMPT # если количество попыток установки корабля превышает это число, то цикл начинается сначала
        while f > 0:
            num_boat = NUMBER_BOAT # количество катеров на поле
            num_cruiser = NUMBER_CRUISER # количество крейсеров на поле
            num_battleship = NUMBER_BATTLESHIP # количетсво линкоров на поле
            # цикл установки линкоров (самых длинных кораблей)
            while num_battleship > 0 and f > 0:
                len = BATTLESHIP
                dir = randint(0, 1) # случайный выбор ориентации корабля (0 - горизонтальная; 1 - вертикальная)
                if dir: # если корабль нужно расположить вертикально
                    x = randint(1, BOARD_SIZE-BATTLESHIP+1)
                    y = randint(1, BOARD_SIZE)
                else: # если корабль нужно расположить горизонтально
                    x = randint(1, BOARD_SIZE)
                    y = randint(1, BOARD_SIZE-BATTLESHIP+1)
                start_dot = copy.deepcopy(Dot(x, y)) # координаты начальной точки корабля
                lives = BATTLESHIP # количество жизней корабля
                battleship = Ship(len, start_dot, dir, lives) # создание корабля с сгенерированными параметрами
                f -= 1 # уменьшение переменной количества попыток
                if temp_board.add_ship(battleship): # установка корабля на поле
                    temp_board.contour(battleship) # прорисовка контура вокруг корабля, чтобы следующий не стоял рядом
                    num_battleship -= 1 # уменьшение количества кораблей этого типа, которые нужно установить
            # цикл установки крейсеров
            while num_cruiser > 0 and f > 0:
                len = CRUISER
                dir = randint(0, 1) # случайный выбор ориентации корабля (0 - горизонтальная; 1 - вертикальная)
                if dir: # если корабль нужно расположить вертикально
                    x = randint(1, BOARD_SIZE-CRUISER+1)
                    y = randint(1, BOARD_SIZE)
                else: # если корабль нужно расположить горизонтально
                    x = randint(1, BOARD_SIZE)
                    y = randint(1, BOARD_SIZE-CRUISER+1)
                start_dot = copy.deepcopy(Dot(x, y)) # координаты начальной точки корабля
                lives = CRUISER # количество жизней корабля
                cruiser = Ship(len, start_dot, dir, lives) # создание корабля с сгенерированными параметрами
                f -= 1 # уменьшение переменной количества попыток
                if temp_board.add_ship(cruiser): # установка корабля на поле
                    temp_board.contour(cruiser) # прорисовка контура вокруг корабля, чтобы следующий не стоял рядом
                    num_cruiser -= 1 # уменьшение количества кораблей этого типа, которые нужно установить
            # цикл установки катеров
            while num_boat > 0 and f > 0:
                len = BOAT
                dir = randint(0, 1) # случайный выбор ориентации корабля (0 - горизонтальная; 1 - вертикальная)
                if dir: # если корабль нужно расположить вертикально
                    x = randint(1, BOARD_SIZE-BOAT+1)
                    y = randint(1, BOARD_SIZE)
                else: # если корабль нужно расположить горизонтально
                    x = randint(1, BOARD_SIZE)
                    y = randint(1, BOARD_SIZE-BOAT+1)
                start_dot = copy.deepcopy(Dot(x, y)) # координаты начальной точки корабля
                lives = BOAT # количество жизней корабля
                boat = Ship(len, start_dot, dir, lives) # создание корабля с сгенерированными параметрами
                f -= 1 # уменьшение переменной количества попыток
                if temp_board.add_ship(boat): # установка корабля на поле
                    temp_board.contour(boat) # прорисовка контура вокруг корабля, чтобы следующий не стоял рядом
                    num_boat -= 1 # уменьшение количества кораблей этого типа, которые нужно установить
            if f == 0: # если количетсво попыток обнулилось, то генерация новой доски
                f = CYCLE_ATTEMPT
                temp_board = copy.deepcopy(Board())
            else: # иначе - все корабли успешно установлены на поле
                for i in range(temp_board.living_ships):
                    temp_board.contour(temp_board.ships_list[i], False) # убирание контуров вокруг кораблей
                return temp_board

    # метод вывода приветствия
    def greet(self):
        print("*************************************************************************************")
        print("                                     МОРСКОЙ БОЙ                                     ")
        print("*************************************************************************************")
        print("                                    ПРАВИЛА ИГРЫ:                                    ")
        print(f" 1) Размеры полей игроков: {BOARD_SIZE} х {BOARD_SIZE} клеток.")
        print(" 2) Корабли игроков устанавливаются на поля с помощью генератора случайных чисел.")
        print(" 3) Между кораблями должна быть хотя бы одна свободная клетка (включая диагонали).")
        print(" 4) Количество кораблей у каждого игрока:")
        print(f"    - катеры (одна клетка) - {NUMBER_BOAT} шт.")
        print(f"    - крейсеры (две клетки) - {NUMBER_CRUISER} шт.")
        print(f"    - линкоры (три клетки) - {NUMBER_BATTLESHIP} шт.")
        print(" 5) Переход хода происходит в случае промаха.")
        print(" 6) Если корабль противника потоплен (поражены все клетки корабля), то вокруг него")
        print(f"    автоматически прорисовывается контур знаками '{CON}'.")
        print(" 7) Формат ввода координат: х y")
        print("    x - номер строки")
        print("    y - номер столбца")
        print("*************************************************************************************")
        print()

    # метод игрового цикла
    def loop(self):
        self.user_1.enemy_board = self.user_2.own_board # доска противника для пользователя
        self.user_2.enemy_board = self.user_1.own_board # доска противника для ИИ
        self.user_1.enemy_board.hid = True # скрыть поле ИИ, чтобы пользователь не видел его корабли
        print("         Ваша доска:")
        self.user_1.own_board.output_board() # вывод поля пользователя
        print("         Доска ИИ:")
        self.user_2.own_board.output_board() # вывод поля ИИ
        current_user = True # вспомогательная переменная для смены ходов пользователя и ИИ
        result_user_1 = (False, "") # результат хода пользователя, второй элемент кортежа - сообщение об ошибке
        result_user_2 = (False, "") # результат хода ИИ, второй элемент кортежа - сообщение об ошибке
        # цикл поочередных ходов, пока у обоих игроков есть живые корабли игра не заканчивается
        while self.user_1.own_board.living_ships > 0 and self.user_2.own_board.living_ships > 0:
            if current_user:
                result_user_1 = self.user_1.move() # ход пользователя
                if not result_user_1[0]:
                    current_user = False
            else:
                result_user_2 = self.user_2.move() # ход ИИ
                if not result_user_2[0]:
                    current_user = True
            if not result_user_1[1] and not result_user_2[1]: # поля не обновляются, если не было сообщений об ошибках
                print("         Ваша доска:")
                self.user_1.own_board.output_board()
                print("         Доска ИИ:")
                self.user_2.own_board.output_board()
        if self.user_1.own_board.living_ships: # если у пользователя остались корабли, то он победил
            print("Вы победили!")
        else:
            print("В этот игре Искуственный Интеллект оказался сильнее!")

    # метод начала игры
    def start(self):
        self.greet() # запуск приветствия
        self.loop()  # запуск игрового цикла


while True:
    game_01 = Game() # создание игры
    game_01.start() # запуск игры
    repeat_game = input("Продолжить игру? (Выход - N; Продолжить - любой символ): ")
    print("")
    if repeat_game == "N":
        print("До встречи!")
        break

