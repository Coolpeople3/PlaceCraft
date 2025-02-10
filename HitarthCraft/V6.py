from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

block_types = {
    1: ('textures/dirt_texture.png', color.white),
    2: ('textures/grass_texture.png', color.white)
}
weapon_types = {
    3: ('textures/pistol_texture.png', color.white)
}

selected_slot = 1

class Block(Button):
    def __init__(self, position=(0, 0, 0), block_type=1):
        texture, color_value = block_types.get(block_type, ('white_cube', color.white))
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color_value,
            highlight_color=color.lime
        )

class Bullet(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=0.2,
            position=position,
            collider='box'
        )
        self.direction = direction.normalized()
        self.speed = 20
        self.start_timer()

    def update(self):
        self.position += self.direction * self.speed * time.dt
        hit_info = raycast(self.position, self.direction, 1, ignore=(self,))
        if hit_info.hit and isinstance(hit_info.entity, Zombie):
            destroy(self)
            hit_info.entity.hit()

    def start_timer(self):
        destroy(self, delay=2)

class Zombie(Entity):
    def __init__(self, position):
        super().__init__(
            model='models/zombie_model.stl',  # Or a more detailed model if you have one
            color=color.green,
            scale=(0.03, 0.06, 0.03),  # Make it taller
            position=position,
            collider='box',
            health=3
        )
        self.health = 3
        self.walk_speed = 1
        self.player = player
        self.is_alive = True

    def update(self):
        if self.is_alive:
            direction_to_player = self.player.position - self.position
            self.position += direction_to_player.normalized() * self.walk_speed * time.dt
            self.look_at_2d(self.player.position)  # Correct rotation

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        destroy(self)

player = FirstPersonController()

# Inventory UI (Hotbar)
hotbar_bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.12), position=(0, -0.45), color=color.dark_gray)
hotbar = Entity(parent=camera.ui, scale=(0.5, 0.1), position=(0, -0.45))
inventory_slots = []

for i in range(9):
    slot_texture = None
    if i + 1 in block_types:
        slot_texture = block_types[i + 1][0]
    elif i + 1 in weapon_types:
        slot_texture = weapon_types[i + 1][0]

    slot = Button(
        parent=hotbar,
        scale=(0.09, 1),
        position=(i * 0.1 - 0.4, 0),
        color=color.gray,
        texture=slot_texture
    )
    inventory_slots.append(slot)

selector = Entity(parent=hotbar, scale=(0.095, 1.1), position=(-0.4, 0), model='quad', color=color.yellow)

def create_world():
    for x in range(-10, 10):
        for z in range(-10, 10):
            Block(position=(x, 0, z), block_type=2)

def input(key):
    global selected_slot

    if key == 'right mouse down' and selected_slot == 1:
        if mouse.hovered_entity:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type=1)

    if key == 'left mouse down':
        if selected_slot == 1:
            if mouse.hovered_entity:
                destroy(mouse.hovered_entity)
        elif selected_slot == 3:  # Check for weapon slot
            shoot()

    if key == 'q':
        application.quit()

    if key in [str(i) for i in range(1, 10)]:
        selected_slot = int(key)
        selector.x = (selected_slot - 1) * 0.1 - 0.4

def shoot():
    bullet = Bullet(position=player.position + (player.forward * 1.5), direction=player.forward)

create_world()

def spawn_zombie():
    x = random.randint(-10, 10)
    z = random.randint(-10, 10)
    Zombie(position=(x, 1, z))

spawn_zombie()
for _ in range(5):  # Spawn initial zombies
    invoke(spawn_zombie, delay=5)

app.run()
