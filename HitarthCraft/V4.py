from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize Ursina
app = Ursina()

# Constants
block_types = {
    1: ('textures/dirt_texture.png', color.white),  # Dirt
    2: ('textures/grass_texture.png', color.white)  # Grass
}

selected_block = 1  # Default block type

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
            highlight_color=color.lime
        )

# Create the player
player = FirstPersonController()

# Inventory UI (Hotbar)
hotbar_bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.12), position=(0, -0.45), color=color.dark_gray)  # Gray background
hotbar = Entity(parent=camera.ui, scale=(0.5, 0.1), position=(0, -0.45))
inventory_slots = []

for i in range(9):  # 9 inventory slots
    slot = Button(
        parent=hotbar,
        scale=(0.09, 1),  # Square shape
        position=(i * 0.1 - 0.4, 0),
        color=color.gray,
        texture=block_types[i + 1][0] if i < 2 else None  # First 2 slots have textures, others are empty
    )
    inventory_slots.append(slot)

# Highlight around selected block
selector = Entity(parent=hotbar, scale=(0.095, 1.1), position=(-0.4, 0), model='quad', color=color.yellow)

# Generate a flat world
def create_world():
    for x in range(-10, 10):
        for z in range(-10, 10):
            block_type = 2 if z % 2 == 0 else 1  # Alternating pattern
            Block(position=(x, 0, z), block_type=block_type)

# Handle input to place/remove blocks & inventory selection
def input(key):
    global selected_block

    if key == 'right mouse down':  # Place block
        if mouse.hovered_entity:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type=selected_block)
    if key == 'left mouse down':  # Remove block
        if mouse.hovered_entity:
            destroy(mouse.hovered_entity)
    if key == 'q':  # Quit instantly
        application.quit()
    
    # Block selection (1-9)
    if key in [str(i) for i in range(1, 10)]:
        selected_block = int(key)
        selector.x = (selected_block - 1) * 0.1 - 0.4  # Move highlight

# Create the world
create_world()

# Run the app
app.run()
