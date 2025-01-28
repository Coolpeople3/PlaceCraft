from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize Ursina
app = Ursina()

# Constants
block_types = {
    1: color.rgb(139, 69, 19),  # Dirt
    2: color.rgb(34, 139, 34)   # Grass
}

# Define the Block class
class Block(Button):
    def __init__(self, position=(0, 0, 0), block_type=1):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=block_types[block_type],
            highlight_color=color.lime
        )

# Create the player
player = FirstPersonController()

# Generate a flat world
def create_world():
    for x in range(-10, 10):
        for z in range(-10, 10):
            Block(position=(x, 0, z), block_type=2 if z % 2 == 0 else 1)

# Handle input to place/remove blocks
def input(key):
    if key == 'left mouse down':
        hit_info = mouse.hovered_entity
        if hit_info:
            Block(position=hit_info.position + mouse.normal, block_type=1)
    if key == 'right mouse down':
        hit_info = mouse.hovered_entity
        if hit_info:
            destroy(hit_info.entity)

# Create the world
create_world()

# Run the app
app.run()
