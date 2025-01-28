from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize Ursina
app = Ursina()

# Constants for block types
block_types = {
    1: color.rgb(139, 69, 19),  # Dirt
    2: color.rgb(34, 139, 34),   # Grass
    3: color.rgb(169, 169, 169), # Stone
    4: color.rgb(139, 69, 19),   # Wood (Same as dirt for simplicity)
    5: color.rgb(255, 255, 0)    # Sand
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

    def on_click(self):
        pass  # Prevent default Button behavior

# Create the player
player = FirstPersonController()

# Inventory
inventory = [1, 2, 3, 4, 5]  # Default blocks: dirt, grass, stone, wood, sand
selected_block = 1  # Start with the first block (dirt)

# Generate a flat world
def create_world():
    for x in range(-10, 10):
        for z in range(-10, 10):
            Block(position=(x, 0, z), block_type=2 if z % 2 == 0 else 1)

# Create the inventory UI (placed at the bottom of the screen)
def create_inventory_ui():
    for i in range(5):
        # Create a slot for each inventory item
        slot = Entity(
            parent=camera.ui,  # Parent the inventory to the camera UI
            model='cube',
            color=color.dark_gray,  # Slot background color
            scale=(0.75, 0.75, 0.75),
            position=(i * 1.5 - 3, -0.5, 0),  # Position at the bottom of the screen
            collider='box'
        )
        
        # Create a block for each slot in the inventory
        block = Entity(
            parent=slot,
            model='cube',
            color=block_types[inventory[i]],  # Color of the block
            scale=(0.5, 0.5, 0.5),
            position=(0, 0, 0)  # Center the block inside the slot
        )

# Handle input to place/remove blocks
def input(key):
    global selected_block

    # Switch between blocks using number keys
    if key == '1':
        selected_block = 1
    elif key == '2':
        selected_block = 2
    elif key == '3':
        selected_block = 3
    elif key == '4':
        selected_block = 4
    elif key == '5':
        selected_block = 5

    # Switch between blocks using scroll wheel
    if key == 'scroll up':
        selected_block = inventory[(inventory.index(selected_block) + 1) % len(inventory)]
    elif key == 'scroll down':
        selected_block = inventory[(inventory.index(selected_block) - 1) % len(inventory)]

    # Right-click to place a block
    if key == 'right mouse down':
        hit_info = mouse.hovered_entity
        if hit_info:
            Block(position=hit_info.position + mouse.normal, block_type=selected_block)

    # Left-click to remove a block
    if key == 'left mouse down':
        hit_info = mouse.hovered_entity
        if hit_info:
            hit_info.destroy()  # Remove the block

# Create the world and inventory UI
create_world()
create_inventory_ui()

# Run the app
app.run()
