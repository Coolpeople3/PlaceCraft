from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time

app = Ursina()

# Define block and weapon textures
block_types = {
    'dirt': ('textures/dirt_texture.png', color.white),
    'grass': ('textures/grass_texture.png', color.white)
}
weapon_types = {
    'pistol': ('textures/pistol_texture.png', color.white)
}

inventory = ['dirt', None, 'pistol', None, None, None, None, None, None]
selected_slot = 0

# Create player's health and health bar UI (full health = 100)
player_health = 100
# The health bar is a green quad; full width is 0.4.
health_bar = Entity(parent=camera.ui, model='quad', color=color.green, 
                    scale=(0.4, 0.05), position=(-0.5, 0.45))

# Create a red health bar for lost health (starts off hidden)
lost_health_bar = Entity(parent=camera.ui, model='quad', color=color.red, 
                         scale=(0, 0.05), position=(-0.5, 0.45))

# Block class
class Block(Button):
    def __init__(self, position=(0, 0, 0), block_type='dirt'):
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

# Bullet class
class Bullet(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='models/bullet.stl',
            texture='textures/bullet_texture.png',
            scale=(0.02, 0.02, 0.02),
            position=position,
            collider='box'
        )
        self.rotation_x = 90
        self.rotation_y = 90
        self.direction = direction.normalized()
        self.speed = 20
        self.start_timer()

    def update(self):
        self.position += self.direction * self.speed * time.dt
        hit_info = raycast(self.position, self.direction, 1, ignore=(self,))
        if hit_info.hit:
            if isinstance(hit_info.entity, Zombie):
                hit_info.entity.hit()
                destroy(self)
            elif isinstance(hit_info.entity, Block):
                destroy(self)

    def start_timer(self):
        destroy(self, delay=2)

# Zombie class
class Zombie(Entity):
    def __init__(self, position):
        super().__init__(
            model='models/zombie_model.stl',
            scale=(0.025, 0.05, 0.025),  # Half the original size
            position=position,
            collider='box',
            texture='textures/zombie_skin_texture.jpg'
        )
        self.rotation_x = -90
        self.rotation_y = 180
        self.health = 2
        self.walk_speed = 1
        self.player = None  # Will be assigned after player creation
        self.is_alive = True
        # This is the zombie's own health bar (for the zombie itself)
        self.health_bar = Entity(parent=self, model='quad', color=color.green, 
                                 scale=(0.5, 0.05, 0.05), position=(0, 0.6, 0))
        self.state = 'wandering'  # 'wandering' or 'chasing'
        self.wander_timer = 0
        self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.last_player_detection = 0
        self.last_damage_time = 0  # timestamp of last damage dealt to player
        self.damage_cooldown = 1  # Damage cooldown of 1 second (to keep it smooth)

    def update(self):
        if self.is_alive and self.player:
            if self.state == 'wandering':
                self.wander()
            elif self.state == 'chasing':
                self.chase_player()
            self.detect_player()

            # Handle the damage dealing on a smooth interval (every `damage_cooldown` seconds)
            if time.time() - self.last_damage_time > self.damage_cooldown:
                self.deal_damage()

    def wander(self):
        self.position += self.move_direction * self.walk_speed * time.dt
        self.rotation_y += random.uniform(-5, 5)
        self.wander_timer += time.dt
        if self.wander_timer > 5:
            self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.wander_timer = 0
        if self.check_collision():
            self.move_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()

    def chase_player(self):
        direction_to_player = self.player.position - self.position
        direction_to_player.y = 0  # movement on the XZ plane
        if self.grounded:
            self.position += direction_to_player.normalized() * self.walk_speed * time.dt
        self.look_at_2d(self.player.position)

    def detect_player(self):
        distance_to_player = (self.player.position - self.position).length()
        if distance_to_player < 10:
            if self.state == 'wandering':
                self.state = 'chasing'
                self.last_player_detection = time.time()

    def check_collision(self):
        hit_info = raycast(self.position + Vec3(0, 1, 0), self.move_direction, 1, ignore=(self,))
        return hit_info.hit

    @property
    def grounded(self):
        return raycast(self.position, Vec3(0, -1, 0), distance=1.1, ignore=(self,)).hit

    def hit(self):
        self.health -= 1
        self.health_bar.scale_x -= 0.25
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        destroy(self)

    def deal_damage(self):
        distance_to_player = (self.player.position - self.position).length()
        if distance_to_player < 1.5:
            global player_health
            player_health = max(0, player_health - 1)  # Standard damage (1)
            health_bar.scale_x = 0.4 * (player_health / 100)
            flash_red_edges()
            self.last_damage_time = time.time()

            if player_health <= 0:
                player_die()

# Damage effect: flash red edges only.
edge_top = Entity(parent=camera.ui, model='quad', color=color.clear, 
                  scale=(1.2, 0.02), position=(0, 0.5))
edge_bottom = Entity(parent=camera.ui, model='quad', color=color.clear, 
                     scale=(1.2, 0.02), position=(0, -0.5))
edge_left = Entity(parent=camera.ui, model='quad', color=color.clear, 
                   scale=(0.02, 1.2), position=(-0.5, 0))
edge_right = Entity(parent=camera.ui, model='quad', color=color.clear, 
                    scale=(0.02, 1.2), position=(0.5, 0))

def flash_red_edges():
    global lost_health_bar
    for edge in [edge_top, edge_bottom, edge_left, edge_right]:
        edge.color = color.rgba(255, 0, 0, 150)
        invoke(setattr, edge, 'color', color.clear, delay=0.15)
    
    # Update the red health bar to increase with lost health
    lost_health_bar.scale_x = 0.4 * (1 - (player_health / 100))

# Inventory UI (Hotbar)
hotbar_bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.12), 
                   position=(0, -0.45), color=color.dark_gray)
hotbar = Entity(parent=camera.ui, scale=(0.5, 0.1), position=(0, -0.45))
inventory_slots = []
for i in range(9):
    slot_texture = None
    item = inventory[i]
    if item in block_types:
        slot_texture = block_types[item][0]
    elif item in weapon_types:
        slot_texture = weapon_types[item][0]
    slot = Button(
        parent=hotbar,
        scale=(0.09, 1),
        position=(i * 0.1 - 0.4, 0),
        color=color.gray,
        texture=slot_texture
    )
    inventory_slots.append(slot)

selector = Entity(parent=hotbar, scale=(0.095, 1.1), position=(-0.4, 0), 
                  model='quad', color=color.yellow)
weapon_display = Entity(parent=camera.ui, position=(0.5, -0.3), 
                        scale=(0.3, 0.3), visible=False, rotation_z=-30)

def create_world():
    for x in range(-10, 10):
        for z in range(-30, 20):
            Block(position=(x, 0, z), block_type='grass')

def input(key):
    global selected_slot
    if key == 'right mouse down' and inventory[selected_slot] == 'dirt':
        if mouse.hovered_entity:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type='dirt')
    if key == 'left mouse down':
        if inventory[selected_slot] == 'dirt':
            if mouse.hovered_entity:
                destroy(mouse.hovered_entity)
        elif inventory[selected_slot] == 'pistol':
            shoot()
    if key in ['q', 'escape', 'backspace']:
        application.quit()
    if key in [str(i + 1) for i in range(9)]:
        selected_slot = int(key) - 1
        selector.x = selected_slot * 0.1 - 0.4
        weapon_display.visible = (inventory[selected_slot] == 'pistol')
        if inventory[selected_slot] == 'pistol':
            weapon_display.texture = 'textures/pistol_texture.png'
            weapon_display.visible = True

def shoot():
    bullet = Bullet(position=player.position + Vec3(0, 1.5, 0) + player.forward * 1.5, 
                    direction=player.forward)
    bullet.rotation_y = player.rotation_y

create_world()

def spawn_zombie():
    x = random.randint(-10, 10)
    z = random.randint(-30, 20)
    if (x, z) != (0, 0):
        Zombie(position=(x, 1, z))

# Create the player and assign to zombies
player = FirstPersonController()
for _ in range(6):
    invoke(spawn_zombie, delay=5)

# Check for zombie collision with player.
def check_zombie_collision():
    global player_health
    for zombie in scene.entities:
        if isinstance(zombie, Zombie) and zombie.is_alive:
            zombie.player = player  # Assign player to zombie so it can deal damage
            distance_to_player = (player.position - zombie.position).length()
            if distance_to_player < 1.5:
                zombie.deal_damage()

    invoke(check_zombie_collision, delay=0.5)

def player_die():
    print("Player has died!")
    # Stop the game or perform other actions
    application.quit()

invoke(check_zombie_collision, delay=1)

app.run()
