import os
import sys
import pygame
import time


pygame.init()
size = width, height = 400, 600
screen = pygame.display.set_mode(size)
current_notes = []


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


bad_presses = 0


class Note(pygame.sprite.Sprite):
    def __init__(self, group, n):
        self.n = n
        # загрузка изображения нужной стрелки
        if n == 1:
            self.image = load_image("left.png", (255, 255, 255))
        if n == 2:
            self.image = load_image("down.png", (255, 255, 255))
        if n == 3:
            self.image = load_image("up.png", (255, 255, 255))
        if n == 4:
            self.image = load_image("right.png", (255, 255, 255))
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.x = 100 * n
        self.rect.y = 0

    def update(self):
        global bad_presses
        self.rect = self.rect.move(0, 1)
        if not screen.get_rect().contains(self.rect):
            self.kill()
            # если стрелку не нажимают вовремя, то увеличивается счётчик ошибок и играет звук непопадания
            pygame.mixer.Sound(f"data/badsound{self.n}.wav").play()
            bad_presses += 1
        # добавление себя в список существующих нот
        current_notes.append((self.rect.y, self.n, self))


all_sprites = pygame.sprite.Group()


if __name__ == '__main__':
    pygame.init()
    size = width, height = 550, 400
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Ритм-игра")
    clock = pygame.time.Clock()
    running = True
    fps = 120
    # список нот / стрелок, которым нужно появиться (<> обозначает несколько стрелок, появляющиеся в одно время)
    notes = "1234321<13><24>1234321"
    # создание события спавна стрелки
    NOTESPAWN = pygame.USEREVENT + 1
    note_count = 0
    pygame.time.set_timer(NOTESPAWN, 1000)
    pygame.mixer.music.load("data/testsong.wav")
    all_notes_used = False
    while running:
        current_notes = []
        screen.fill((255, 255, 255))
        # отрисовка полоски, на которой нужно нажимать стрелки
        pygame.draw.rect(screen, "black", (0, 350, width, 5))
        # отрисовка кубика здоровья
        if (width - 50 - bad_presses * 50) // width == 0:
            pygame.draw.rect(screen, "red", ((width - 50 - bad_presses * 50) % 800, 325, 50, 50))
        elif (width - 50 - bad_presses * 50) // width > 0:
            pygame.draw.rect(screen, "red", (width - 50, 325, 50, 50))
        else:
            # экран проигрыша и выход из игры
            screen.fill("black")
            font = pygame.font.Font(None, 50)
            text = font.render("You lost // Вы проиграли", True, "white")
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - text.get_height() // 2
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.display.flip()
            time.sleep(1)
            screen.fill("black")
            running = False
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == NOTESPAWN:
                if note_count == 0:
                    pygame.mixer.music.play()
                if note_count < len(notes):
                    # проверка на то, нужно ли создать одну стрелку или несколько
                    if notes[note_count] != "<" and notes[note_count] != ">":
                        Note(all_sprites, int(notes[note_count]))
                        note_count += 1
                    else:
                        altogether = set()
                        temp_count = 0
                        for i in notes[note_count + 1:]:
                            if i != ">":
                                altogether.add(int(i))
                                temp_count += 1
                            else:
                                note_count += temp_count
                                break
                        for i in altogether:
                            Note(all_sprites, i)
                        note_count += 2
                else:
                    pygame.time.set_timer(NOTESPAWN, 0)
                    all_notes_used = True
            if event.type == pygame.KEYDOWN:
                # проверка на то, правильно ли нажата кнопка, если да,
                # то стрелка уничтожается и, если до этого были ошибки, уменьшает счётчик на 1
                # и играет звук правильного нажатия,
                # а если нет, то добавляет к счётчику 2
                # и играет звук неправильного нажатия.
                if event.key == pygame.K_LEFT:
                    flag = False
                    for i in current_notes:
                        if i[1] == 1 and i[0] > 300:
                            pygame.mixer.Sound("data/goodsound1.wav").play()
                            i[2].kill()
                            if bad_presses >= 1:
                                bad_presses -= 1
                            flag = True
                    if flag is False:
                        pygame.mixer.Sound("data/badsound1.wav").play()
                        bad_presses += 2
                if event.key == pygame.K_DOWN:
                    flag = False
                    for i in current_notes:
                        if i[1] == 2 and i[0] > 300:
                            pygame.mixer.Sound("data/goodsound2.wav").play()
                            i[2].kill()
                            if bad_presses >= 1:
                                bad_presses -= 1
                            flag = True
                    if flag is False:
                        pygame.mixer.Sound("data/badsound2.wav").play()
                        bad_presses += 2
                if event.key == pygame.K_UP:
                    flag = False
                    for i in current_notes:
                        pygame.mixer.Sound("data/goodsound3.wav").play()
                        if i[1] == 3 and i[0] > 300:
                            i[2].kill()
                            if bad_presses >= 1:
                                bad_presses -= 1
                            flag = True
                    if flag is False:
                        pygame.mixer.Sound("data/badsound3.wav").play()
                        bad_presses += 2
                if event.key == pygame.K_RIGHT:
                    flag = False
                    for i in current_notes:
                        if i[1] == 4 and i[0] > 300:
                            pygame.mixer.Sound("data/goodsound4.wav").play()
                            i[2].kill()
                            if bad_presses >= 1:
                                bad_presses -= 1
                            flag = True
                    if flag is False:
                        pygame.mixer.Sound("data/badsound4.wav").play()
                        bad_presses += 2
        if current_notes == [] and all_notes_used is True:
            # экран выигрыша и выход из игры
            screen.fill("white")
            font = pygame.font.Font(None, 50)
            text = font.render("You won // Вы выиграли", True, "black")
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - text.get_height() // 2
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.display.flip()
            time.sleep(1)
            screen.fill("white")
            running = False
        clock.tick(fps)
    pygame.quit()
