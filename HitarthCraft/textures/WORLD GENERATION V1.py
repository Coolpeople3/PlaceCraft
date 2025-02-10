from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import noise  # Perlin noise for terrain generation

# Initialize Ursina
app = Ursina()

# Block Types
block_types = {
    1: ('textures/dirt_texture.png', color.white),  # Dirt Block
    2: ('textures/grass_texture.png', color.white)  # Grass Block (Top Layer)
}

# Selected slot (1 = Dirt)
selected_slot = 1

# Block Class
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

# Create the player
player = FirstPersonController()

# Handle block placement and removal
def input(key):
    global selected_slot

    if key == 'right mouse down' and selected_slot == 1:  # Place block
        if mouse.hovered_entity:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type=1)

    if key == 'left mouse down':  # Remove block
        if mouse.hovered_entity:
            destroy(mouse.hovered_entity)

    # Hotbar Selection (1-2)
    if key in ['1', '2']:
        selected_slot = int(key)

# Generate the terrain
generate_terrain()

# Run the game
app.run()
