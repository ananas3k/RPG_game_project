import pygame
import os
import sys
import csv
import random

# barcadebrawlregular - font

# constants

mixer = pygame.mixer

SPRITE_LIST = {'.': 'grass1.png',
               ',': 'grass2.png',
               '#': 'wall1.png', }

pygame.font.init()
font_name = pygame.font.match_font("barcadebrawlregular")
Font = pygame.font.Font(font_name, 30)


# functions
def get_cell(pos):
    if 474 < pos[1] < 548:
        if 485 < pos[0] < 561:
            return 'slot1'
        elif 562 < pos[0] < 638:
            return 'slot2'
        elif 639 < pos[0] < 715:
            return 'slot3'
    elif 549 < pos[1] < 625:
        if 485 < pos[0] < 561:
            return 'slot4'
        elif 562 < pos[0] < 638:
            return 'slot5'
        elif 639 < pos[0] < 715:
            return 'slot6'
    return None


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def get_lvl(name):
    fullname = os.path.join('data', name)

    with open(fullname, newline='') as csv_lvl:
        data = list(csv.reader(csv_lvl, delimiter=';', quotechar='\n'))
        return data


def get_sprite(sprite_name):
    sprite = pygame.sprite.Sprite()
    sprite.image = load_image(f"sprites\\{sprite_name}")
    sprite.rect = sprite.image.get_rect()
    return sprite


# classes
class AnimatedText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color=(0,0,0)):
        super().__init__()
        self.x = x
        self.y = y
        self.count = 0
        self.text = Font.render(text, 0, color)
        screen.blit(self.text, (x, y))


    def update(self):
        self.count += 4
        screen.blit(self.text, (self.x, self.y - self.count))
        if self.count > 35:
            self.kill()

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation_name, w, h, scale=1, flip=False):
        super().__init__()
        self.animation_frames = []
        full_name = os.path.join('data\\sprites', animation_name)
        animation_list = pygame.image.load(full_name).convert_alpha()
        width, height = animation_list.get_size()
        if scale != 1:
            animation_list = pygame.transform.scale(animation_list, (width * scale, height * scale))
            width, height = animation_list.get_size()
            w = w * scale
            h = h * scale
        if flip:
            for j in range(int(height / h)):
                for i in range(int(width / w)):
                    self.animation_frames.append(pygame.transform.flip(animation_list.subsurface(i * w, j * h, w, h), True, False))
        else:
            for j in range(int(height / h)):
                for i in range(int(width / w)):
                    self.animation_frames.append(animation_list.subsurface(i * w, j * h, w, h))
        self.frames = len(self.animation_frames)
        self.frame_counter = 0
        self.image = self.animation_frames[self.frame_counter]
        self.rect = self.image.get_rect()

    def update(self):
        self.frame_counter = (self.frame_counter + 1) % self.frames
        self.image = self.animation_frames[self.frame_counter]


class Enemy(AnimatedSprite):
    def __init__(self, animation_name, w, h, x, y, name='enemy', attack_list=None, agility=0, armor=0, health_regen=0,
                 bounty=0, keys=0, item=None, escape_chance=100, health=100, max_health=100, need_to_flip=False):
        super().__init__(animation_name, w, h)
        self.animation_name = animation_name
        self.w = w
        self.h = h
        self.ntf = need_to_flip
        self.x = x
        self.y = y
        self.effects = []
        self.name = name
        self.bounty = bounty
        self.keys = keys
        self.item = item
        self.agility = agility
        self.armor = armor
        self.health_regen = health_regen
        self.attack_list = attack_list
        self.escape_chance = escape_chance
        self.health = health
        self.max_health = max_health

    def fight(self, board, player):
        board.is_fight = True
        background = get_sprite('fight_scene.png')
        background.image = pygame.transform.scale(background.image, (750, 450))
        background.rect.x = 0
        background.rect.y = 0
        board.fight_sprites.add(background)
        self.player_agility = player.get_agility()
        self.player_armor = player.get_armor()
        self.player_health_regen = player.get_health_regen()
        self.player_effects = []

        self.escape_btn = get_sprite('escape_button.png')
        self.escape_btn.rect.x = 30
        self.escape_btn.rect.y = 370
        board.fight_sprites.add(self.escape_btn)

        self.punch_btn = get_sprite('attack_button.png')
        self.punch_btn.rect.x = 210
        self.punch_btn.rect.y = 370
        board.fight_sprites.add(self.punch_btn)

        self.block_btn = get_sprite('block_button.png')
        self.block_btn.rect.x = 390
        self.block_btn.rect.y = 370
        board.fight_sprites.add(self.block_btn)

        self.dodge_btn = get_sprite('dodge_button.png')
        self.dodge_btn.rect.x = 570
        self.dodge_btn.rect.y = 370
        board.fight_sprites.add(self.dodge_btn)

        enemy_sprite = AnimatedSprite(self.animation_name, self.w, self.h, scale=5, flip=self.ntf)
        enemy_sprite.rect.x = 450
        enemy_sprite.rect.y = 110
        board.fight_sprites.add(enemy_sprite)
        board.animated_sprites.add(enemy_sprite)

        player_sprite = get_sprite('player_r.png')
        player_sprite.rect.x = 50
        player_sprite.rect.y = 110
        player_sprite.image = pygame.transform.scale(player_sprite.image, (250, 250))
        board.fight_sprites.add(player_sprite)
        board.animated_sprites.add(player_sprite)

        board.render(screen)

    def win(self, board):
        board.is_fight = False
        if self.item:
            self.item.rect = self.item.image.get_rect()
            self.item.rect.x = self.x * 50 - board.camera.x
            self.item.rect.y = self.y * 50 - board.camera.y
            board.all_sprites.add(self.item)
            board.game_sprites.add(self.item)
            board.item_sprites.add(self.item)
        board.player.money += self.bounty
        for sprite in board.fight_sprites:
            sprite.kill()
        self.kill()

    def click(self, pos, board):
        if self.dodge_btn.rect.collidepoint(pos):
            self.player_effects.append(['agility', 10, 1])
            self.attack(board.player, attacked=False)
        elif self.punch_btn.rect.collidepoint(pos):
            self.attack(board.player, damage=15)
        elif self.escape_btn.rect.collidepoint(pos):
            if random.randint(1, 100) <= self.escape_chance:
                self.escape(board)
            else:
                self.attack(board.player, attacked=False)
        elif self.block_btn.rect.collidepoint(pos):
            self.player_effects.append(['armor', 10, 1])
            self.attack(board.player, attacked=False)

    def attack(self, player, damage=0, effect_list=None, on_enemy=True, attacked=True):

        player_stats = {'agility': self.player_agility,
                        'armor': self.player_armor,
                        'health_regen': self.player_health_regen}

        self_stats = {'agility': self.agility,
                      'armor': self.armor,
                      'health_regen': self.health_regen}

        if on_enemy:
            if effect_list:
                for effect in effect_list:
                    self.effects.append(effect)
        else:
            if effect_list:
                for effect in effect_list:
                    self.player_effects.append(effect)
        for effect in self.effects:
            effect[2] -= 1
            self_stats[effect[0]] += effect[1]

        for effect in self.player_effects:
            effect[2] -= 1
            player_stats[effect[0]] += effect[1]

        for i in range(len(self.effects) - 1, -1, -1):
            if self.effects[i][2] <= 0:
                del self.effects[i]

        for i in range(len(self.player_effects) - 1, -1, -1):
            if self.player_effects[i][2] <= 0:
                del self.player_effects[i]

        self.health += self_stats['health_regen']
        if self_stats['health_regen'] > 0:
            text = AnimatedText(str(self_stats['health_regen']), 450, 100, color=(50, 200, 50))
            player.board.animated_sprites.add(text)
        elif self_stats['health_regen'] < 0:
            text = AnimatedText(str(self_stats['health_regen'] * -1), 450, 100, color=(200, 0, 0))
            player.board.animated_sprites.add(text)

        if attacked:
            if on_enemy:
                if random.randint(1, 100) > 5 * (self_stats['agility'] - player_stats['agility']):
                    if damage - self_stats['armor'] > 0:
                        self.health -= (damage - self_stats['armor'])
                        mixer.Sound(os.path.join('data\\sounds\\attack_sound.mp3')).play()
                        text = AnimatedText(str(damage - self_stats['armor']), 530, 100, color=(200, 0, 0))
                        player.board.animated_sprites.add(text)
                    else:
                        mixer.Sound(os.path.join('data\\sounds\\block_sound.mp3')).play()
                        text = AnimatedText('block', 530, 100, color=(50, 50, 50))
                        player.board.animated_sprites.add(text)
                else:
                    mixer.Sound(os.path.join('data\\sounds\\miss_sound.mp3')).play()
                    text = AnimatedText('miss', 530, 100, color=(150, 200, 200))
                    player.board.animated_sprites.add(text)
            else:
                if damage:
                    player.hp += damage
                    text = AnimatedText(str(damage), 150, 100, color=(50, 200, 50))
                    player.board.animated_sprites.add(text)


        if self.health <= 0:
            self.win(player.board)
        else:
            pygame.time.wait(250)
            attack_chance = random.randint(1, 100)
            for attack in self.attack_list:
                # chance, damage, effect_list
                if attack[0] > attack_chance:
                    break
            damage = attack[1]
            player.hp += player_stats['health_regen']

            if player_stats['health_regen'] > 0:
                text = AnimatedText(str(player_stats['health_regen']), 50, 100, color=(50, 200, 50))
                player.board.animated_sprites.add(text)
            elif player_stats['health_regen'] < 0:
                text = AnimatedText(str(player_stats['health_regen'] * -1), 50, 100, color=(200, 0, 0))
                player.board.animated_sprites.add(text)

            if random.randint(1, 100) > 5 * (player_stats['agility'] - self_stats['agility']):
                if damage - player_stats['armor'] > 0:
                    player.hp -= (damage - player_stats['armor'])
                    player.count_update()
                    mixer.Sound(os.path.join('data\\sounds\\attack_sound.mp3')).play()
                    text = AnimatedText(str(damage - player_stats['armor']), 130, 100, color=(200, 0, 0))
                    player.board.animated_sprites.add(text)
                else:
                    mixer.Sound(os.path.join('data\\sounds\\block_sound.mp3')).play()
                    text = AnimatedText('block', 130, 100, color=(50, 50, 50))
                    player.board.animated_sprites.add(text)
            else:
                mixer.Sound(os.path.join('data\\sounds\\miss_sound.mp3')).play()
                text = AnimatedText('miss', 130, 100, color=(150, 200, 200))
                player.board.animated_sprites.add(text)
            if attack[2]:
                for effect in attack[2]:
                    self.player_effects.append(effect)

    def escape(self, board):
        board.is_fight = False
        for sprite in board.fight_sprites:
            sprite.kill()


class Item(pygame.sprite.Sprite):
    def __init__(self, name='item', effect_list=None, passive_effect_list=None, damage=0, reusable=True, on_enemy=True,
                 miss_chance=-1, step=0, use_in_fight=True):
        super().__init__()
        self.ask_to_drop = False
        self.step = step
        self.slot = 0
        self.active = False
        self.sprites = pygame.sprite.Group()
        self.name = name
        self.damage = damage
        self.reusable = reusable
        self.on_enemy = on_enemy
        self.miss_chance = miss_chance
        self.use_in_fight = use_in_fight
        self.effect_list = {'agility': None,
                            'armor': None,
                            'health_regen': None}
        self.passive_effect_list = {'agility': None,
                                    'armor': None,
                                    'health_regen': None}
        if effect_list:
            for i in effect_list:
                # name power time
                self.effect_list[i[0]] = [i[1], i[2]]
        self.passive_effect_list = passive_effect_list

    def take(self, board):
        board.is_paused = True
        self.active = True
        self.window = get_sprite('dialogue_window.png')
        self.window.rect.x = 225
        self.window.rect.y = 100
        self.sprites.add(self.window)
        fnt = pygame.font.Font(font_name, 16)
        text = fnt.render(f'подобрать {self.name}?', 0, (0, 0, 0))
        self.text_sprite = pygame.sprite.Sprite()
        self.text_sprite.image = text
        self.text_sprite.rect = self.text_sprite.image.get_rect()
        self.text_sprite.rect.x = 280 - len(self.name) * 8
        self.text_sprite.rect.y = 150
        self.sprites.add(self.text_sprite)
        self.no_btn = get_sprite('no.png')
        self.no_btn.rect.x = 250
        self.no_btn.rect.y = 300
        self.sprites.add(self.no_btn)
        self.yes_btn = get_sprite('yes.png')
        self.yes_btn.rect.x = 425
        self.yes_btn.rect.y = 300
        self.sprites.add(self.yes_btn)
        self.sprites.draw(screen)

    def drop(self, board):
        board.is_paused = True
        self.ask_to_drop = True
        self.active = True
        self.window = get_sprite('dialogue_window.png')
        self.window.rect.x = 225
        self.window.rect.y = 100
        self.sprites.add(self.window)
        fnt = pygame.font.Font(font_name, 16)
        text = fnt.render(f'выкинуть {self.name}?', 0, (0, 0, 0))
        self.text_sprite = pygame.sprite.Sprite()
        self.text_sprite.image = text
        self.text_sprite.rect = self.text_sprite.image.get_rect()
        self.text_sprite.rect.x = 290 - len(self.name) * 8
        self.text_sprite.rect.y = 150
        self.sprites.add(self.text_sprite)
        self.no_btn = get_sprite('no.png')
        self.no_btn.rect.x = 250
        self.no_btn.rect.y = 300
        self.sprites.add(self.no_btn)
        self.yes_btn = get_sprite('yes.png')
        self.yes_btn.rect.x = 425
        self.yes_btn.rect.y = 300
        self.sprites.add(self.yes_btn)
        self.sprites.draw(screen)

    def use(self, board):
        if self.use_in_fight:
            effect_list = []
            if self.effect_list['agility']:
                effect_list.append(['agility'] + self.effect_list['agility'])
            if self.effect_list['armor']:
                effect_list.append(['armor'] + self.effect_list['armor'])
            if self.effect_list['health_regen']:
                effect_list.append(['health_regen'] + self.effect_list['health_regen'])
            board.player.enemy.attack(board.player, self.damage, effect_list, self.on_enemy)
            if not self.reusable:
                board.player.del_item(self.slot)
                self.kill()

    def click(self, pos, board):
        if self.active:
            if self.yes_btn.rect.collidepoint(pos):
                self.yes(board)
            elif self.no_btn.rect.collidepoint(pos):
                self.no(board)

    def yes(self, board):
        board.is_paused = False
        self.active = False
        self.yes_btn.kill()
        self.no_btn.kill()
        self.window.kill()
        self.text_sprite.kill()
        if self.ask_to_drop:
            mixer.Sound(os.path.join('data\\sounds\\drop_sound.mp3')).play()
            board.player.del_item(self.slot)
            self.kill()
        else:
            mixer.Sound(os.path.join('data\\sounds\\take_sound.mp3')).play()
            board.player.add_item(self)
            self.remove(board.game_sprites)

    def no(self, board):
        board.is_paused = False
        self.active = False
        self.yes_btn.kill()
        self.no_btn.kill()
        self.window.kill()
        self.text_sprite.kill()


class Shop(pygame.sprite.Sprite):
    def __init__(self, cost=0, item_name=None, item_sprite=None, effect_list=None, passive_effect_list=None, damage=0, reusable=True,
                 on_enemy=True, miss_chance=-1, step=0, use_in_fight=True):
        super().__init__()
        self.sprites = pygame.sprite.Group()
        self.item = Item(item_name, effect_list, passive_effect_list, damage, reusable, on_enemy, miss_chance, step,
                         use_in_fight)
        self.item.image = load_image(f'sprites\\{item_sprite}')
        self.item.rect = self.item.image.get_rect()
        self.cost = cost
        self.active = False

    def buy(self, board):
        board.is_paused = True
        self.active = True
        self.window = get_sprite('dialogue_window.png')
        self.window.rect.x = 225
        self.window.rect.y = 100
        self.sprites.add(self.window)
        fnt = pygame.font.Font(font_name, 16)
        text = fnt.render(f'купить {self.item.name}', 0, (0, 0, 0))
        self.text_sprite1 = pygame.sprite.Sprite()
        self.text_sprite1.image = text
        self.text_sprite1.rect = self.text_sprite1.image.get_rect()
        self.text_sprite1.rect.x = 320 - len(self.item.name) * 8
        self.text_sprite1.rect.y = 150
        text = fnt.render(f'за {self.cost}$?', 0, (0, 0, 0))
        self.text_sprite2 = pygame.sprite.Sprite()
        self.text_sprite2.image = text
        self.text_sprite2.rect = self.text_sprite2.image.get_rect()
        self.text_sprite2.rect.x = 340 - len(str(self.cost)) * 8
        self.text_sprite2.rect.y = 180
        self.sprites.add(self.text_sprite1)
        self.sprites.add(self.text_sprite2)
        self.no_btn = get_sprite('no.png')
        self.no_btn.rect.x = 250
        self.no_btn.rect.y = 300
        self.sprites.add(self.no_btn)
        if board.player.have_empty_slot() and board.player.money >= self.cost:
            self.yes_btn = get_sprite('yes.png')
        else:
            self.yes_btn = get_sprite('cant.png')
        self.yes_btn.rect.x = 425
        self.yes_btn.rect.y = 300
        self.sprites.add(self.yes_btn)
        self.sprites.draw(screen)

    def click(self, pos, board):
        if self.active:
            if self.yes_btn.rect.collidepoint(pos):
                self.yes(board)
            elif self.no_btn.rect.collidepoint(pos):
                self.no(board)

    def yes(self, board):
        if self.cost <= board.player.money and board.player.have_empty_slot():
            board.is_paused = False
            self.active = False
            mixer.Sound(os.path.join('data\\sounds\\buy.mp3')).play()
            board.player.money -= self.cost
            self.yes_btn.kill()
            self.no_btn.kill()
            self.window.kill()
            self.text_sprite1.kill()
            self.text_sprite2.kill()
            board.item_sprites.add(self.item)
            board.player.add_item(self.item)
            self.kill()

    def no(self, board):
        board.is_paused = False
        self.active = False
        self.yes_btn.kill()
        self.no_btn.kill()
        self.window.kill()
        self.text_sprite1.kill()
        self.text_sprite2.kill()


class Portal(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.coords = coords


class Camera:
    def __init__(self, board):
        self.board = board
        self.x = 0
        self.y = 0
        self.max_x = (board.width - board.scr_width) * 50
        self.max_y = (board.height - board.scr_height) * 50

    def move(self, x_cord, y_cord):
        x_old = self.x
        y_old = self.y
        self.x = x_cord - 350
        self.y = y_cord - 200
        if self.x < 0:
            self.x = 0
        elif self.x > self.max_x:
            self.x = self.max_x
        if self.y < 0:
            self.y = 0
        elif self.y > self.max_y:
            self.y = self.max_y
        self.board.sprites_update(self.x - x_old, self.y - y_old)


class Player(pygame.sprite.Sprite):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.x = 0
        self.y = 0

        self.inventory = {'slot1': None,
                          'slot2': None,
                          'slot3': None,
                          'slot4': None,
                          'slot5': None,
                          'slot6': None, }

        self.image = load_image(f"sprites\\player_r.png")
        self.rect = self.image.get_rect()

        health_bar = get_sprite('health_bar.png')
        health_bar.rect.x = 25
        health_bar.rect.y = 500
        self.effects = []
        self.board.all_sprites.add(health_bar)
        self.board.GUI_sprites.add(health_bar)
        self.health_bar_sprite = health_bar

        self.max_x = board.width * 50 - 50
        self.max_y = board.height * 50 - 50
        self.min_y = 0
        self.hp = 100
        self.max_hp = 100
        self.mp = 100
        self.max_mp = 100
        self.keys = 0
        self.max_keys = 9
        self.money = 0
        self.max_money = 99
        self.effects = []
        self.items = []

        self.health_regen = 0
        self.agility = 5
        self.armor = 5
        self.enemy = None

        self.money_count = Font.render(str(self.money), 0, (0, 0, 0))
        self.key_count = Font.render(str(self.keys), 0, (0, 0, 0))
        self.hp_count = Font.render(str(self.hp), 0, (0, 0, 0))

        self.sprites = pygame.sprite.Group()

    def add_item(self, item):
        for i in range(0, 6):
            if not self.inventory[f'slot{i + 1}']:
                item.slot = i + 1
                item.rect.x = 485 + item.step + 15 + 75 * (i % 3)
                item.rect.y = 470 + item.step + 15 + 75 * int(i > 2)
                self.inventory[f'slot{i + 1}'] = item
                self.board.inventory_sprites.add(item)
                break

    def del_item(self, n):
        self.inventory[f'slot{n}'] = None

    def have_empty_slot(self):
        for i in range(1, 7):
            if not self.inventory[f'slot{i}']:
                return True
        return False

    def move(self, x_cord, y_cord, selfmove=True):
        if x_cord == 50:
            self.image = load_image('sprites\\player_r.png')
        elif x_cord == -50:
            self.image = load_image('sprites\\player_l.png')
        elif y_cord == 50:
            self.image = load_image('sprites\\player_d.png')
        else:
            self.image = load_image('sprites\\player_u.png')
        self.rect.x += x_cord
        self.rect.y += y_cord
        if pygame.sprite.spritecollideany(self, self.board.wall_sprites):
            self.rect.x -= x_cord
            self.rect.y -= y_cord
        elif pygame.sprite.spritecollideany(self, self.board.door_sprites) and self.keys == 0:
            self.rect.x -= x_cord
            self.rect.y -= y_cord
        elif selfmove and pygame.sprite.spritecollideany(self, self.board.portal_sprites):
            for portal in self.board.portal_sprites:
                if pygame.sprite.spritecollideany(portal, self.board.player_sprites):
                    self.x += x_cord
                    self.y += y_cord
                    cords = [int(i) for i in portal.coords.split()]
                    self.move(cords[0] * 50, cords[1] * 50, selfmove=False)
                    break
        else:
            if pygame.sprite.spritecollideany(self, self.board.item_sprites) and self.have_empty_slot():
                for item in self.board.item_sprites:
                    if pygame.sprite.spritecollideany(item, self.board.player_sprites):
                        item.take(self.board)
            if pygame.sprite.spritecollideany(self, self.board.enemy_sprites):
                for enemy in self.board.enemy_sprites:
                    if pygame.sprite.spritecollideany(enemy, self.board.player_sprites):
                        self.enemy = enemy
                        enemy.fight(self.board, self)
            if pygame.sprite.spritecollideany(self, self.board.shop_sprites):
                for shop in self.board.shop_sprites:
                    if pygame.sprite.spritecollideany(shop, self.board.player_sprites):
                        shop.buy(self.board)
            elif pygame.sprite.spritecollideany(self, self.board.door_sprites):
                self.keys -= 1
                mixer.Sound(os.path.join('data\\sounds\\door_sound.mp3')).play()
                for door in self.board.door_sprites:
                    if pygame.sprite.spritecollideany(door, self.board.player_sprites):
                        door.kill()
            elif pygame.sprite.spritecollideany(self, self.board.key_sprites) and self.keys < self.max_keys:
                self.keys += 1
                for key in self.board.key_sprites:
                    if pygame.sprite.spritecollideany(key, self.board.player_sprites):
                        key.kill()
            elif pygame.sprite.spritecollideany(self, self.board.coin_sprites) and self.money < self.max_money:
                self.money += 1
                mixer.Sound(os.path.join('data\\sounds\\coin_sound.mp3')).play()
                for coin in self.board.coin_sprites:
                    if pygame.sprite.spritecollideany(coin, self.board.player_sprites):
                        coin.kill()

            self.x += x_cord
            self.y += y_cord
            if self.x < 0:
                self.x = 0
            elif self.x > self.max_x:
                self.x = self.max_x
            if self.y < 0:
                self.y = 0
            elif self.y > self.max_y:
                self.y = self.max_y

            self.rect.x = self.x
            self.rect.y = self.y

            self.board.camera.move(self.x, self.y)

    def get_agility(self):
        a = self.agility
        for i in range(1, 7):
            if self.inventory[f'slot{i}'] and self.inventory[f'slot{i}'].passive_effect_list and\
                    'agility' in self.inventory[f'slot{i}'].passive_effect_list.keys():
                a += self.inventory[f'slot{i}'].passive_effect_list['agility']
        return a

    def get_armor(self):
        a = self.armor
        for i in range(1, 7):
            if self.inventory[f'slot{i}'] and self.inventory[f'slot{i}'].passive_effect_list and\
                    'armor' in self.inventory[f'slot{i}'].passive_effect_list.keys():
                a += self.inventory[f'slot{i}'].passive_effect_list['armor']
        return a


    def get_health_regen(self):
        a = self.health_regen
        for i in range(1, 7):
            if self.inventory[f'slot{i}'] and self.inventory[f'slot{i}'].passive_effect_list and\
                    'health_regen' in self.inventory[f'slot{i}'].passive_effect_list.keys():
                a += self.inventory[f'slot{i}'].passive_effect_list['health_regen']
        return a

    def click(self, mouse):
        if get_cell(mouse) and self.inventory[get_cell(mouse)]:
            if self.board.is_fight:
                self.inventory[get_cell(mouse)].use(self.board)
            else:
                self.inventory[get_cell(mouse)].drop(self.board)

    def count_update(self):
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        elif self.hp <= 0:
            sys.exit()
        self.health_bar_sprite.image = pygame.transform.scale(self.health_bar_sprite.image,
                                                              (self.hp * 250 // self.max_hp, 100))
        self.board.GUI_sprites.draw(screen)

        self.hp_count = Font.render(str(self.hp), 0, (0, 0, 0))
        screen.blit(self.hp_count, (160 - (20 * (len(str(self.hp)))), 535))

        if self.money > self.max_money:
            self.money = self.max_money
        self.money_count = Font.render(str(self.money), 0, (0, 0, 0))
        screen.blit(self.money_count, (400, 495))

        if self.keys > self.max_keys:
            self.keys = self.max_keys
        self.money_count = Font.render(str(self.keys), 0, (0, 0, 0))
        screen.blit(self.money_count, (400, 575))


class Game:
    def __init__(self, width=15, height=9):
        # параметры игрового поля
        self.levels = []
        self.position = 0
        self.lvl_name = None
        self.player_on_board = False
        self.lvl = ''
        self.is_paused = False
        self.is_fight = False
        self.left = 0
        self.top = 0
        self.cell_size = 50
        self.scr_width = width
        self.scr_height = height
        self.width = width
        self.height = height

        # группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.ground_sprites = pygame.sprite.Group()
        self.portal_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()
        self.game_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.key_sprites = pygame.sprite.Group()
        self.coin_sprites = pygame.sprite.Group()
        self.animated_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.shop_sprites = pygame.sprite.Group()
        self.inventory_sprites = pygame.sprite.Group()
        self.GUI_sprites = pygame.sprite.Group()
        self.fight_sprites = pygame.sprite.Group()

        player_panel = get_sprite('player_window.png')
        player_panel.rect.x = 0
        player_panel.rect.y = 450
        self.all_sprites.add(player_panel)
        self.GUI_sprites.add(player_panel)

        # создание игрока и камеры
        self.player = Player(self)
        self.camera = Camera(self)

        # генерация уровня
        self.change_lvl('lvl_40x40.csv')
        self.render(screen)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        screen.fill((0, 0, 0))

    def render(self, scrn):
        for y in range(self.scr_height):
            for x in range(self.scr_width):
                pygame.draw.rect(scrn, (0, 255, 255), (self.left + x * self.cell_size, self.top + y * self.cell_size,
                                                       self.cell_size, self.cell_size), 1)
        self.all_sprites.draw(screen)
        self.player_sprites.draw(screen)
        self.GUI_sprites.draw(screen)
        for item in self.item_sprites:
            item.sprites.draw(screen)
        for shop in self.shop_sprites:
            shop.sprites.draw(screen)
        self.player.count_update()
        self.fight_sprites.draw(screen)
        self.inventory_sprites.draw(screen)

    def sprites_update(self, x, y):
        for sprite in self.game_sprites:
            sprite.rect.x -= x
            sprite.rect.y -= y
        for sprite in self.player_sprites:
            sprite.rect.x = self.player.x - self.camera.x
            sprite.rect.y = self.player.y - self.camera.y
        self.render(screen)

    def change_lvl(self, lvl_name):
        for sprite in self.game_sprites:
            sprite.kill()

        self.lvl_name = lvl_name
        self.lvl = get_lvl(f'{lvl_name}')
        self.height = len(self.lvl)
        self.width = len(self.lvl[0])
        self.player.max_x = self.width * 50 - 50
        self.player.max_y = self.height * 50 - 50
        self.player.min_y = 0

        for y in range(self.height):
            for x in range(self.width):
                if self.lvl[y][x][0] in SPRITE_LIST.keys():
                    sprite = get_sprite(SPRITE_LIST[self.lvl[y][x][0]])
                else:
                    sprite = get_sprite('grass1.png')
                sprite.rect.x = 50 * x
                sprite.rect.y = 50 * y
                self.all_sprites.add(sprite)
                self.game_sprites.add(sprite)
                if self.lvl[y][x] in ['.', ',', 'P', 'K', 'C', 'D', 'p', 's']:
                    self.ground_sprites.add(sprite)
                elif self.lvl[y][x] in ['#']:
                    self.wall_sprites.add(sprite)
                if self.lvl[y][x] == 'P':
                    self.player.rect.x = 50 * x
                    self.player.x = 50 * x
                    self.camera.max_x = (self.width - self.scr_width) * 50
                    self.camera.x = 50 * x - 350
                    self.player.rect.y = 50 * y
                    self.player.y = 50 * y
                    self.camera.max_y = (self.height - self.scr_height) * 50
                    self.camera.y = 50 * y - 200
                    self.all_sprites.add(self.player)
                    self.player_sprites.add(self.player)
                elif self.lvl[y][x] == 'K':
                    key = AnimatedSprite('key_32x32_24f.png', 32, 32)
                    key.rect.x = 50 * x + 9
                    key.rect.y = 50 * y + 9
                    self.key_sprites.add(key)
                    self.all_sprites.add(key)
                    self.game_sprites.add(key)
                    self.animated_sprites.add(key)
                elif self.lvl[y][x] == 'C':
                    coin = AnimatedSprite('coin.png', 32, 32)
                    coin.rect.x = 50 * x + 9
                    coin.rect.y = 50 * y + 9
                    self.coin_sprites.add(coin)
                    self.all_sprites.add(coin)
                    self.game_sprites.add(coin)
                    self.animated_sprites.add(coin)
                elif self.lvl[y][x] == 'D':
                    door = get_sprite('door1.png')
                    door.rect.x = 50 * x
                    door.rect.y = 50 * y
                    self.all_sprites.add(door)
                    self.game_sprites.add(door)
                    self.door_sprites.add(door)
                elif self.lvl[y][x][0] == 'p':
                    portal = Portal(self.lvl[y][x][2:])
                    portal.image = load_image("sprites\\portal.png")
                    portal.rect = portal.image.get_rect()
                    portal.rect.x = 50 * x
                    portal.rect.y = 50 * y
                    self.all_sprites.add(portal)
                    self.game_sprites.add(portal)
                    self.portal_sprites.add(portal)
                elif self.lvl[y][x][0] == 's':
                    sword = Item(name='меч', effect_list=[['health_regen', -5, 3]], damage=25, on_enemy=True)
                    sword.image = load_image("sprites\\sword.png")
                    sword.rect = sword.image.get_rect()
                    sword.rect.x = 50 * x
                    sword.rect.y = 50 * y
                    self.all_sprites.add(sword)
                    self.game_sprites.add(sword)
                    self.item_sprites.add(sword)
                elif self.lvl[y][x][0] == 'h':
                    potion = Item(name='зелье', effect_list=[['health_regen', 5, 5]], damage=50,
                                  on_enemy=False, reusable=False)
                    potion.image = load_image("sprites\\health_potion.png")
                    potion.rect = potion.image.get_rect()
                    potion.rect.x = 50 * x
                    potion.rect.y = 50 * y
                    self.all_sprites.add(potion)
                    self.game_sprites.add(potion)
                    self.item_sprites.add(potion)
                elif self.lvl[y][x][0] == 'a':
                    potion = Item(name='щит', effect_list=[['armor', 15, 1]], damage=0,
                                  on_enemy=False, reusable=True, passive_effect_list={'armor': 5})
                    potion.image = load_image("sprites\\shield.png")
                    potion.rect = potion.image.get_rect()
                    potion.rect.x = 50 * x
                    potion.rect.y = 50 * y
                    self.all_sprites.add(potion)
                    self.game_sprites.add(potion)
                    self.item_sprites.add(potion)
                elif self.lvl[y][x][0] == 'S':
                    shop = Shop(cost=25, item_name='щит', item_sprite='shield.png', effect_list=[['armor', 15, 1]],
                                damage=0,  on_enemy=False, passive_effect_list={'armor': 5})
                    shop.image = load_image("sprites\\shop.png")
                    shop.rect = shop.image.get_rect()
                    shop.rect.x = 50 * x
                    shop.rect.y = 50 * y
                    self.all_sprites.add(shop)
                    self.game_sprites.add(shop)
                    self.shop_sprites.add(shop)
                elif self.lvl[y][x][0] == 'm':
                    reward = Item(name='зелье', effect_list=[['health_regen', 5, 5]], damage=50,
                                  on_enemy=False, reusable=False)
                    reward.image = load_image("sprites\\health_potion.png")
                    monstr = Enemy('monster1_50x50_21f.png', 50, 50, x, y, name='monstr', agility=10, armor=3, bounty=20,
                                   escape_chance=75, need_to_flip=True, item=reward)
                    monstr.attack_list = [[10, 15, [['health_regen', -5, 3]]], [100, 10, None]]
                    monstr.rect = monstr.image.get_rect()
                    monstr.rect.x = 50 * x
                    monstr.rect.y = 50 * y
                    self.all_sprites.add(monstr)
                    self.game_sprites.add(monstr)
                    self.enemy_sprites.add(monstr)
                    self.animated_sprites.add(monstr)
                elif self.lvl[y][x][0] == 'd':
                    reward = Item(name='зелье', effect_list=[['health_regen', 15, 5], ['armor', 15, 5]], damage=100,
                                  on_enemy=False, reusable=False)
                    reward.image = load_image("sprites\\health_potion.png")
                    dragon = Enemy('dragon_32x32_8f.png', 32, 32, x, y, name='monstr', agility=5, armor=10, bounty=100,
                                   escape_chance=50, item=reward, max_health=200, health=200, health_regen=5)
                    dragon.attack_list = [[5, 0, [['health_regen', -20, 3]]], [100, 25, None]]
                    dragon.rect = dragon.image.get_rect()
                    dragon.rect.x = 50 * x
                    dragon.rect.y = 50 * y
                    self.all_sprites.add(dragon)
                    self.game_sprites.add(dragon)
                    self.enemy_sprites.add(dragon)
                    self.animated_sprites.add(dragon)
                elif self.lvl[y][x][0] == 'b':
                    reward = Item(name='кольцо', passive_effect_list={'agility': 10}, use_in_fight=False)
                    reward.image = load_image("sprites\\ring.png")
                    bandit = Enemy('bandit_48x48_16f.png', 48, 48, x, y, name='bandit', agility=15, armor=5, bounty=25,
                                   escape_chance=50, item=reward)
                    bandit.attack_list = [[15, 25, [['armor', -10, 2]]], [100, 15, None]]
                    bandit.rect = bandit.image.get_rect()
                    bandit.rect.x = 50 * x
                    bandit.rect.y = 50 * y
                    self.all_sprites.add(bandit)
                    self.game_sprites.add(bandit)
                    self.enemy_sprites.add(bandit)
                    self.animated_sprites.add(bandit)
        self.sprites_update(self.camera.x, self.camera.y)
        self.camera.move(self.player.x, self.player.y)
        self.render(screen)


if __name__ == '__main__':
    # create window
    pygame.init()
    size = width, height = 750, 650
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
    pygame.display.set_caption('RPG game')
    game = Game()
    # mainloop
    update_animation = pygame.event.EventType(pygame.USEREVENT, attr1='update_animation')
    timer = pygame.time.Clock()
    pygame.time.set_timer(update_animation, 90)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                game.render(screen)
                if not (game.is_paused):
                    game.animated_sprites.update()
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.player.click(event.pos)
                if game.is_paused:
                    for item in game.item_sprites:
                        item.click(event.pos, game)
                    for shop in game.shop_sprites:
                        shop.click(event.pos, game)
                if game.is_fight:
                    game.player.enemy.click(event.pos, game)
            elif event.type == pygame.KEYDOWN:
                if event.key in [119, 97, 115, 100] and not (game.is_paused or game.is_fight):
                    move = {119: (0, -50),
                            97: (-50, 0),
                            115: (0, 50),
                            100: (50, 0)}
                    x, y = move[event.key]
                    game.player.move(x, y)
                elif event.unicode in ['p', '']:
                    game.is_paused = not game.is_paused
                elif event.unicode == 'l':
                    game.change_lvl('lvl_test.csv')
                elif event.unicode in ['+', '=']:
                    game.player.hp += 10
                    game.render(screen)
                elif event.unicode in ['-', '_']:
                    game.player.hp -= 10
                    game.render(screen)

            pygame.display.update()
            pygame.display.flip()
            pygame.display.update()
