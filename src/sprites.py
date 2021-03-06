import pygame
import random
import public
import dictionaries
import functions


class Ox(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.regenables)

        self.image = dictionaries.IMAGES['Idle']
        self.invert = dictionaries.I_IMAGES['Idle']
        self.rect = self.image[0].get_rect(topleft=pos)

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2()

        self.layer = 4
        self.won = False
        self.died = False
        self.type = 'Player'
        self.init_pos = pos
        self.collided = None
        self.on_ground = True
        self.jumping = False
        self.flip_cooldown = 0
        self.super_jump = False
        self.accelerating = False
        self.flipped_horizontal = flipped
        self.velocities = dict(right=[0.1, 0], left=[-0.1, 1])

        self.anim_index = 0
        self.anim_type = 'Idle'
        self.anim_ticks = 0
        self.anim_caps = dict(
            Idle=75,
            Walk=10,
            Jump=25,
            Fall=25,
            Die=13,
            Win=20
        )

    def update(self):

        # -- Position Management --

        self.pos.x += self.vel.x
        self.rect.x = self.pos.x
        self.super_jump = False

        self.collided = pygame.sprite.spritecollide(self, public.blocks, False)
        for block in self.collided:

            if block.color != public.bg_type:

                if self.vel.x > 0 and functions.block_check(block, 4):
                    self.rect.right = block.rect.left

                elif self.vel.x < 0 and functions.block_check(block, 4):
                    self.rect.left = block.rect.right

                if functions.block_check(block, 2):
                    self.accelerating = False

                self.pos.x = self.rect.x

                if block.type in ['Pit', 'KillBlock'] and not self.died:
                    self.died = True
                    self.anim_ticks = 0
                    self.anim_index = 0
                    dictionaries.MEDIA['died'].play()

                elif block.type == 'Exit' and not self.died:
                    public.level += 1

                    if public.level == public.level_max:
                        pass

                    elif public.level != public.level_max:
                        functions.generate_level(True)
                        dictionaries.MEDIA['finish'].play()

                        self.kill()

                elif block.type == 'Breakable':
                    if not block.dead and not block.recovering:
                        dictionaries.MEDIA['crumble'].play()
                        block.broken = True

                elif block.type == 'Jumpad' and not (
                        self.died and self.super_jump):

                    if not self.super_jump:
                        dictionaries.MEDIA['jumpad'].play()
                        self.super_jump = True

                    self.vel.y = -4.5
                    self.on_ground = False

                elif block.type == 'RGBSphere':
                    dictionaries.MEDIA['collect'].play()
                    block.rect.y -= 10
                    self.won = True

        self.pos.y += self.vel.y
        self.rect.y = self.pos.y
        self.super_jump = False

        self.collided = pygame.sprite.spritecollide(self, public.blocks, False)
        for block in self.collided:

            if block.color != public.bg_type:

                if self.vel.y > 0 and functions.block_check(block, 4):
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.vel.y = 0

                elif self.vel.y < 0 and functions.block_check(block, 4):
                    self.rect.top = block.rect.bottom
                    self.on_ground = True
                    self.vel.y = 0

                if functions.block_check(block, 2):
                    self.super_jump = False
                    self.jumping = False

                self.pos.y = self.rect.y

                if block.type in ['Pit', 'KillBlock'] and not self.died:
                    self.died = True
                    self.anim_ticks = 0
                    self.anim_index = 0
                    dictionaries.MEDIA['died'].play()

                elif block.type == 'Pit' and not self.died:
                    self.died = True
                    self.anim_ticks = 0
                    self.anim_index = 0
                    dictionaries.MEDIA['died'].play()

                elif block.type == 'Breakable':
                    if not block.dead and not block.recovering:
                        dictionaries.MEDIA['crumble'].play()
                        block.broken = True

        if public.wrapping:
            if self.rect.right >= public.SWIDTH + 10:
                self.rect.left = 1
                self.pos.x = self.rect.left

            elif self.rect.right <= 0:
                self.rect.right = public.SWIDTH - 1
                self.pos.x = self.rect.left

        elif not public.wrapping:
            if self.rect.right >= public.SWIDTH:
                self.rect.right = public.SWIDTH
                self.accelerating = False
                self.pos.x = self.rect.left

            elif self.rect.left <= 0:
                self.rect.left = 0
                self.accelerating = False
                self.pos.x = self.rect.left

        if self.rect.top >= public.SHEIGHT and not self.died:
            self.died = True
            self.anim_ticks = 0
            self.anim_index = 0
            dictionaries.MEDIA['died'].play()

        self.vel.y += public.GRAVITY

        if self.vel.y < -0.5 or self.vel.y > 0.5 and not self.jumping:
            self.on_ground = False

        if public.level == 0:
            public.player.vel.x = functions.clamp(public.player.vel.x, -5.0, 5.0)

        else:
            public.player.vel.x = functions.clamp(public.player.vel.x, -10.0, 10.0)

        public.player.pos.x += public.player.vel.x
        public.player.vel.x *= 0.925

        # -- Animation --

        self.anim_ticks += 1

        if self.anim_ticks == self.anim_caps[self.anim_type]:
            self.anim_index = (self.anim_index + 1) % 4
            self.anim_ticks = 0

        else:
            if self.anim_ticks > self.anim_caps[self.anim_type]:
                self.anim_ticks = 0

        self.anim_type = functions.anim_check(self)

        if self.died and self.anim_index == 3:
            if public.level == 0:
                raise Exception('@!^& // Sometimes its better to let secrets be secrets. // %$#&')

            functions.generate_level(False)
        self.image = dictionaries.IMAGES[self.anim_type]
        self.invert = dictionaries.I_IMAGES[self.anim_type]

        if self.flip_cooldown > 0:
            self.flip_cooldown -= public.dt

    def draw(self):
        prep_surf = self.image[self.anim_index]
        if public.bg_type == public.WHITE:
            prep_surf = self.invert[self.anim_index]

        if self.flipped_horizontal:
            prep_surf = pygame.transform.flip(prep_surf, 1, 0)

        public.screen.blit(prep_surf, self.rect)

    def jump(self):
        if self.on_ground and not self.died and not self.won:

            self.vel.y = -3
            self.jumping = True
            self.on_ground = False
            self.anim_type = 'Jump'
            dictionaries.MEDIA['jump'].play()

    def flip(self):
        if self.flip_cooldown <= 0 and not self.died and not self.won and not public.level == 0:
            inside = False

            for sprite in public.blocks:
                if sprite.rect.colliderect(self.rect) and not (sprite.type == 'Breakable' and sprite.dead == True):
                    inside = True

            if not inside:
                dictionaries.MEDIA['flip'].play()

                if public.bg_type == public.WHITE:
                    public.bg_type = public.BLACK

                elif public.bg_type == public.BLACK:
                    public.bg_type = public.WHITE

            else:
                dictionaries.MEDIA['denied'].play()

            self.flip_cooldown = 1

        elif public.level == 0:
            dictionaries.MEDIA['denied'].play()

    def move(self, direction):
        self.accelerating = True
        self.vel.x += self.velocities[direction][0]
        self.flipped_horizontal = self.velocities[direction][1]

        if public.player.vel.x < 0.04 and direction == 'right' and self.velocities['right'][0] == 0.1:
            public.player.pos.x += 1


class Block(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = pygame.Surface((20, 20))
        self.transparent = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)

        self.type = 'Block'
        self.color = color
        self.layer = 3

        self.image.fill([self.color] * 3)
        self.transparent.set_alpha(0)

    def draw(self):
        prep_surf = self.image

        if public.bg_type == self.color:
            prep_surf = self.transparent

        public.screen.blit(prep_surf, self.rect)


class Exit(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = functions.image_return(color, 'Exit')
        self.rect = self.image[0].get_rect(topleft=pos)
        self.transparent = pygame.Surface(self.image[0].get_size())

        self.type = 'Exit'
        self.color = color
        self.layer = 3

        self.anim_index = 0
        self.anim_ticks = 0

        self.transparent.set_alpha(0)

    def update(self):
        self.anim_ticks += 1

        if self.anim_ticks == 10:
            self.anim_ticks = 0
            self.anim_index = (self.anim_index + 1) % 4

    def draw(self):
        prep_surf = self.image[self.anim_index]
        if public.bg_type == self.color:
            prep_surf = self.transparent

        public.screen.blit(prep_surf, self.rect)


class KillBlock(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = pygame.Surface((10, 10))
        self.transparent = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)

        self.rect.x += 5
        self.rect.y += 5

        self.type = 'KillBlock'
        self.color = color
        self.layer = 3

        self.transparent.set_alpha(0)

    def draw(self):
        public.screen.blit(self.transparent, self.rect)


class Pit(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = functions.image_return(color, 'Pit')[0]
        self.transparent = pygame.Surface(self.image[0].get_size())
        self.rect = self.image[0].get_rect(topleft=pos)

        self.type = 'Pit'
        self.color = color
        self.layer = 3
        self.flipped = flipped

        self.anim_index = 0
        self.anim_ticks = 0

        self.transparent.set_alpha(0)
        functions.flip_check(self)

    def update(self):
        self.anim_ticks += 1

        if self.anim_ticks == 10:
            self.anim_ticks = 0
            self.anim_index = (self.anim_index + 1) % 4

    def draw(self):
        prep_surf = self.image[self.anim_index]
        if public.bg_type == self.color:
            prep_surf = self.transparent

        public.screen.blit(prep_surf, self.rect)


class Breakable(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks, public.regenables)

        self.image = pygame.Surface((20, 11))
        self.cover = pygame.Surface((20, 11))
        self.transparent = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2()
        self.init_pos = pygame.math.Vector2(pos)
        self.flipped = flipped
        self.type = 'Breakable'
        self.recovering = False
        self.grace_time = 0.1
        self.dead_timer = 3
        self.cool_time = 3
        self.broken = False
        self.color = color
        self.dead = False
        self.layer = 2
        self.alpha = 0

        self.image.fill([self.color] * 3)

        self.transparent.set_alpha(0)
        self.cover.set_alpha(0)

        if self.flipped:
            self.pos.y += 10
            self.rect.y += 10

    def update(self):
        if self.broken:
            if self.grace_time > 0:
                self.grace_time -= public.dt

            elif self.grace_time < 0:
                if self.alpha != 255:
                    self.alpha += 5

                if not self.vel.y >= 10:
                    if not self.flipped:
                        self.vel.y += public.GRAVITY - 0.01

                    elif self.flipped:
                        self.vel.y -= public.GRAVITY - 0.01

        if self.alpha == 255:
            self.dead = True

        if self.dead:
            if self.dead_timer > 0:
                self.dead_timer -= public.dt

            elif self.dead_timer < 0:
                self.dead = False
                self.broken = False
                self.recovering = True

                pos_ = (self.init_pos.x, self.init_pos.y)
                self.pos.x, self.pos.y = pos_
                self.vel.y = 0
                self.dead_timer = 3

        if self.recovering:
            self.alpha -= 15

            if self.alpha == 0:
                self.recovering = False

        self.pos += self.vel
        self.rect.topleft = self.pos

        if public.bg_type == public.WHITE:
            color = public.WHITE

        else:
            color = public.BLACK

        self.cover.fill([color] * 3)
        self.cover.set_alpha(self.alpha)

    def draw(self):
        prep_surf = self.image

        if public.bg_type == self.color:
            prep_surf = self.transparent

        public.screen.blit(prep_surf, self.rect)
        public.screen.blit(self.cover, self.rect)


class Jumpad(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = functions.image_return(color, 'Jumpad')
        self.transparent = pygame.Surface((20, 10))
        self.rect = self.image[0].get_rect(topleft=pos)

        self.flipped = flipped
        self.type = 'Jumpad'
        self.color = color
        self.layer = 3

        self.anim_index = 0
        self.anim_ticks = 0

        self.transparent.set_alpha(0)
        functions.flip_check(self)

    def update(self):
        self.anim_ticks += 1

        if self.anim_ticks == 10:
            self.anim_ticks = 0
            self.anim_index = (self.anim_index + 1) % 4

    def draw(self):
        prep_surf = self.image[self.anim_index]
        if public.bg_type == self.color:
            prep_surf = self.transparent

        public.screen.blit(prep_surf, self.rect)


class RGBSphere(pygame.sprite.Sprite):
    def __init__(self, pos, color, flipped):
        super().__init__(public.all_sprites, public.blocks)

        self.image = dictionaries.IMAGES['RGBSphere']
        self.rect = self.image[0].get_rect(topleft=pos)
        self.rect.x += 5
        self.rect.y += 5

        self.type = 'RGBSphere'
        self.color = color
        self.layer = 3

        self.anim_index = 0
        self.anim_ticks = 0

    def update(self):
        self.anim_ticks += 1

        if self.anim_ticks == 10:
            self.anim_ticks = 0
            self.anim_index = (self.anim_index + 1) % 24

    def draw(self):
        public.screen.blit(self.image[self.anim_index], self.rect)


class Cloud(pygame.sprite.Sprite):
    def __init__(self, pos, cloud_type):
        super().__init__(public.all_sprites)

        self.image = dictionaries.IMAGES['Decor'][cloud_type]
        self.flipped_horizontal = pygame.transform.flip(self.image, 1, 0)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.math.Vector2(pos)
        self.vel = [0.5, 0.2][cloud_type]
        self.cap = [0.5, 0.2][cloud_type]
        self.skip_pos = None
        self.layer = cloud_type
        self.cloud_type = cloud_type
        self.type = 'Cloud'

        if public.bg_type == public.WHITE:
            self.vel = -self.vel

        if self.layer == 1:
            self.layer = 0

        elif self.layer == 0:
            self.layer = 1

    def update(self):
        self.pos.x += self.vel
        self.rect.center = self.pos

        if public.bg_type == public.WHITE and self.vel != -self.cap:
            self.vel -= 0.1

        elif public.bg_type == public.BLACK and self.vel != self.cap:
            self.vel += 0.1

        if self.skip_pos != None:
            if self.cloud_type == 1:
                if round(self.pos.x - 5) == self.skip_pos[0]:
                    self.pos.x = self.skip_pos[0]
                    self.pos.y = self.skip_pos[1]

            if (self.pos.x - 15) == self.skip_pos[0]:
                self.pos.x = self.skip_pos[0]
                self.pos.y = self.skip_pos[1]

        if self.pos.x < -10:
            generated_int = random.randint(0, 1)
            generated_height = random.randint(0, public.SHEIGHT)

            if public.level != 0:
                cloud = Cloud((810, generated_height), generated_int)

                self.kill()

        elif self.pos.x > public.SWIDTH + 10:
            generated_int = random.randint(0, 1)
            generated_height = random.randint(0, public.SHEIGHT)

            if public.level != 0:
                cloud = Cloud((-10, generated_height), generated_int)

                self.kill()

    def draw(self):
        prep_surf = self.image
        if public.bg_type == public.WHITE:
            prep_surf = self.flipped_horizontal

        public.screen.blit(prep_surf, self.rect)


class Title(pygame.sprite.Sprite):
    def __init__(self, text, is_scrambled):
        super().__init__(public.all_sprites)

        self.image = public.FONT_SM.render(text, False, [public.bg_type] * 3)
        self.rect = self.image.get_rect(topleft=(10, 10))

        self.dt = public.clock.tick(public.FPS) / 1000
        self.timer = 1
        self.layer = 6
        self.alpha = 255
        self.text = text
        self.type = 'Title'
        self.is_scrambled = is_scrambled
        self.scramble_time = 0
        self.scramble_max = 0.20

        if self.is_scrambled:
            self.text = ''.join(
                [random.choice([
                    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
                    ) for i in range(10)])

    def update(self):
        if self.timer > 0:
            self.timer -= self.dt

        elif self.timer <= 0 and self.alpha != 0:
            self.alpha -= 5

            if self.alpha == 0:
                self.kill()

        if self.is_scrambled:
            self.scramble_time += self.dt

            if self.scramble_time >= self.scramble_max:
                self.text = ''.join(
                    [random.choice([
                        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')'
                        ]) for i in range(10)])

                self.scramble_time = 0

        if public.bg_type == public.WHITE:
            color = public.BLACK

        else:
            color = public.WHITE

        self.image = public.FONT_SM.render(self.text, False, [color] * 3)

        self.image.set_alpha(self.alpha)

    def draw(self):
        public.screen.blit(self.image, self.rect)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, button_type):
        super().__init__(public.all_sprites)

        self.image = dictionaries.IMAGES['Buttons'][0]
        self.rect = self.image.get_rect(topleft=pos)
        
        self.type = 'Button'
        self.button_type = button_type
        self.button_state = True
        self.y_pushdown = 0
        self.is_pressing = False

        if self.button_type == 'Music':
            self.image = dictionaries.IMAGES['Buttons'][(1 + int(not public.music))]

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        pointer_is_in = self.rect.collidepoint(mouse_pos)

        if pointer_is_in:
            if self.y_pushdown != 5:
                self.y_pushdown += 1

            if pygame.mouse.get_pressed()[0]:
                if self.button_type == 'Music' and not self.is_pressing:
                    public.music = not public.music
                    self.image = dictionaries.IMAGES['Buttons'][(1 + int(not public.music))]
                    self.is_pressing = True

                elif self.button_type == 'Play':
                    public.end_title = True

            else:
                self.is_pressing = False


        if not pointer_is_in:
            if self.y_pushdown != 0:
                self.y_pushdown -= 1


    def draw(self):
        public.screen.blit(self.image, (self.rect.x, self.rect.y + self.y_pushdown))        


class Wrapping(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(public.all_sprites)

        self.image = dictionaries.IMAGES['Decor'][2]
        self.rect = self.image.get_rect(topleft=pos)

        self.layer = 5
        self.type = 'Wrapping'
        self.color = public.GREY
        self.pos = pygame.math.Vector2(pos)

        if public.bg_type == public.WHITE:
            self.image = dictionaries.IMAGES['Decor'][3]

    def update(self):
        if public.bg_type == public.BLACK:
            self.image = dictionaries.IMAGES['Decor'][2]

        elif public.bg_type == public.WHITE:
            self.image = dictionaries.IMAGES['Decor'][3]

    def draw(self):
        prep_surf = self.image

        if self.pos.x == 780:
            prep_surf = pygame.transform.flip(prep_surf, True, False)

        public.screen.blit(prep_surf, self.rect)

# :^)