from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import noise  # For terrain generation
import random

# Initialize Ursina
app = Ursina()

# Block and Weapon Definitions
block_types = {
    1: ('textures/dirt_texture.png', color.white),  # Dirt Block
    2: ('textures/grass_texture.png', color.white)  # Grass Block (Ground)
}
weapon_types = {
    3: ('textures/pistol_texture.png', color.white)  # Pistol
}

selected_slot = 1  # Default to Dirt Block

# Define the Block class
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
            collider='box',
            highlight_color=color.lime
        )

# Define the Bullet class
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
        self.position += self.direction * self.speed * time.dt  # Move in 3D direction

    def start_timer(self):
        destroy(self, delay=2)  # Destroy after 2 seconds

# Create the player
player = FirstPersonController()

# Inventory UI (Hotbar)
hotbar_bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.12), position=(0, -0.45), color=color.dark_gray)
hotbar = Entity(parent=camera.ui, scale=(0.5, 0.1), position=(0, -0.45))
inventory_slots = []

for i in range(9):  # 9 inventory slots
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

# Highlight around selected slot
selector = Entity(parent=hotbar, scale=(0.095, 1.1), position=(-0.4, 0), model='quad', color=color.yellow)

# Perlin Noise-based Terrain Generation
def generate_terrain(size=20, height_scale=5):
    seed = random.randint(0, 100)  # Random seed for variation
    for x in range(-size, size):
        for z in range(-size, size):
            # Generate height using Perlin noise
            height = int(noise.pnoise2(x * 0.1, z * 0.1, octaves=3, persistence=0.5, lacunarity=2) * height_scale)
            for y in range(height + 1):  # Generate blocks up to the height level
                block_type = 2 if y == height else 1  # Grass on top, dirt below
                Block(position=(x, y, z), block_type=block_type)

# Handle input to place/remove blocks & weapon firing
def input(key):
    global selected_slot

    if key == 'right mouse down' and selected_slot == 1:  # Place dirt block
        if mouse.hovered_entity:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type=1)  # Always place dirt

    if key == 'left mouse down':
        if selected_slot == 1:  # Remove block
            if mouse.hovered_entity:
                destroy(mouse.hovered_entity)
        elif selected_slot == 2:  # Shoot pistol
            shoot()

    if key == 'q':  # Quit instantly
        application.quit()

    # Inventory selection (1-9)
    if key in [str(i) for i in range(1, 10)]:
        selected_slot = int(key)
        selector.x = (selected_slot - 1) * 0.1 - 0.4  # Move highlight

# Shoot function (3D bullet mechanics)
def shoot():
    bullet = Bullet(position=player.position + (player.forward * 1.5), direction=player.forward)

# Generate the world
generate_terrain(size=25, height_scale=7)

# Run the app
app.run()
