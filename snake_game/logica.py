import pygame
import random
import os
import array
import math
from .estructuras_de_datos import DoublyLinkedList, FoodType # Importación relativa
from .configuracion import CELL_SIZE, GRID_W, GRID_H, C_BLACK, C_WHITE, C_RED, C_GOLD, SCREEN_WIDTH, SCREEN_HEIGHT,SKINS

# --- AUDIO PROCEDURAL ---
class SoundSynth:
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
    
    def generate_wave(self, freq, duration, vol=0.5, wave_type="square"):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        amp = 32767 * vol
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = 0
            if wave_type == "square": val = 1 if int(t * freq * 2) % 2 else -1
            elif wave_type == "saw": val = 2 * (t * freq - math.floor(t * freq + 0.5))
            elif wave_type == "noise": val = random.uniform(-1, 1)
            buf[i] = int(val * amp)
        return pygame.mixer.Sound(buffer=buf)

    def create_sounds(self):
        self.sounds["click"] = self.generate_wave(600, 0.05, 0.2, "square")
        self.sounds["eat"] = self.generate_wave(400, 0.1, 0.3, "square")
        self.sounds["powerup"] = self.generate_wave(800, 0.2, 0.3, "saw")
        self.sounds["die"] = self.generate_wave(100, 0.5, 0.5, "noise")
        self.sounds["buy"] = self.generate_wave(1000, 0.1, 0.3, "square")

    def play(self, name):
        if name in self.sounds: self.sounds[name].play()

class AssetManager:
    def __init__(self):
        self.textures = {}
        self.fonts = {}
        self.create_textures()
        self.noise_texture = self.create_noise_texture()
        self.create_fonts()
        self.music_files = []
        self.load_music()
        

    def load_music(self):
        """Define la lista de archivos de música para el bucle."""
        self.music_files = [
            r"C:\Users\User\OneDrive\Documents\PROGRAMACIÓN UNAL\ESTRUCTURAS DE DATOS\PROYECTO\Musica\a-video-game-248444.mp3",
            r"C:\Users\User\OneDrive\Documents\PROGRAMACIÓN UNAL\ESTRUCTURAS DE DATOS\PROYECTO\Musica\Lexica   Press X Twice (Royalty Free Music).mp3",
            r"C:\Users\User\OneDrive\Documents\PROGRAMACIÓN UNAL\ESTRUCTURAS DE DATOS\PROYECTO\Musica\A Lil BIT.mp3",
            
        ]

    def create_textures(self):
        cs = CELL_SIZE
        def get_surf(color, shape="circle"):
            s = pygame.Surface((cs, cs), pygame.SRCALPHA)
            if shape=="circle": 
                pygame.draw.circle(s, color, (cs//2, cs//2), cs//2-2)
                pygame.draw.circle(s, (255,255,255), (cs//2+4, cs//2-4), cs//6)
            elif shape=="bomb":
                pygame.draw.circle(s, (30,30,30), (cs//2, cs//2), cs//2-2)
                pygame.draw.line(s, (255,100,0), (cs//2, 2), (cs//2, cs//2), 2)
            elif shape=="pear":
                 pygame.draw.ellipse(s, color, (2, 2, cs-4, cs-4))
            return s

        self.textures[FoodType.APPLE] = get_surf((220, 20, 60))
        self.textures[FoodType.BLUE_APPLE] = get_surf((30, 144, 255))
        self.textures[FoodType.PURPLE_APPLE] = get_surf((138, 43, 226))
        self.textures[FoodType.LEMON] = get_surf((255, 255, 0))
        self.textures[FoodType.BERRY] = get_surf((75, 0, 130))
        self.textures[FoodType.BOMB] = get_surf((0,0,0), "bomb")

    def create_fonts(self):
        """Carga y crea las fuentes de diferentes tamaños."""
        font_name = 'monospace' 
        self.fonts[18] = pygame.font.SysFont(font_name, 18, bold=True)
        self.fonts[20] = pygame.font.SysFont(font_name, 20, bold=True)
        self.fonts[24] = pygame.font.SysFont(font_name, 24, bold=True)
        self.fonts[30] = pygame.font.SysFont(font_name, 30, bold=True)
        self.fonts[40] = pygame.font.SysFont(font_name, 40, bold=True)
        self.fonts[60] = pygame.font.SysFont(font_name, 60, bold=True)

    def get_snake_head(self, skin_key, direction):
        cs = CELL_SIZE
        s = pygame.Surface((cs, cs), pygame.SRCALPHA)
        data = SKINS[skin_key]
        color = data["color"]
        pygame.draw.rect(s, color, (1,1,cs-2,cs-2), border_radius=5)
        eye_c = C_BLACK if color != (30,30,30) else C_WHITE
        pygame.draw.circle(s, eye_c, (6, 6), 2)
        pygame.draw.circle(s, eye_c, (cs-6, 6), 2)
        
        acc = data["acc"]
        if acc == "glasses":
            pygame.draw.line(s, C_BLACK, (4, 6), (cs-4, 6), 2)
            pygame.draw.circle(s, (0,0,0,100), (6, 6), 4, 1)
            pygame.draw.circle(s, (0,0,0,100), (cs-6, 6), 4, 1)
        elif acc == "beard":
            pygame.draw.polygon(s, (80,80,80), [(4, cs-8), (cs//2, cs), (cs-4, cs-8)])
        elif acc == "hat":
            pygame.draw.rect(s, (20,20,20), (4, -2, cs-8, 6))
            pygame.draw.line(s, (20,20,20), (0, 4), (cs, 4), 2)
        elif acc == "mustache":
             pygame.draw.line(s, (200,200,200), (4, cs-6), (cs-4, cs-6), 3)
        elif acc == "pacifier":
            pygame.draw.circle(s, (255,192,203), (cs//2, cs-6), 3)

        angle = 0
        if direction == (1, 0): angle = -90
        elif direction == (-1, 0): angle = 90
        elif direction == (0, -1): angle = 180
        return pygame.transform.rotate(s, angle)

    def get_snake_body(self, skin_key):
        cs = CELL_SIZE
        s = pygame.Surface((cs, cs), pygame.SRCALPHA)
        c = SKINS[skin_key]["color"]
        darker = (max(0, c[0]-20), max(0, c[1]-20), max(0, c[2]-20))
        pygame.draw.rect(s, darker, (1,1,cs-2,cs-2), border_radius=3)
        return s
    
    def create_noise_texture(self):
        """Crea una superficie con ruido aleatorio para simular grano retro."""
        noise_size = 50 
        noise_surf = pygame.Surface((noise_size, noise_size), pygame.SRCALPHA)
        
        # Generar píxeles aleatorios semitransparentes
        for x in range(noise_size):
            for y in range(noise_size):
                # Color oscuro o blanco, con poca opacidad
                alpha = random.randint(0, 30) # Opacidad baja (0 a 30)
                color = random.choice([(0,0,0, alpha), (255,255,255, alpha)])
                pygame.draw.rect(noise_surf, color, (x, y, 1, 1))
        
        # Escalar la textura a la pantalla para que el patrón se repita
        # Usa pygame.transform.scale para que cubra todo el SCREEN_WIDTH, SCREEN_HEIGHT
        return pygame.transform.scale(noise_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
    

class Snake:
    def __init__(self):
        # Inicialización CORREGIDA para evitar colisión instantánea
        self.body = DoublyLinkedList()
        
        # Centro del mapa
        cx, cy = 20, 15 
        
        # Insertamos primero la COLA, luego MEDIO, luego CABEZA
        # Así, al hacer push_front, la cabeza queda primera en la lista.
        self.body.push_front((cx-2, cy)) # Cola
        self.body.push_front((cx-1, cy)) # Medio
        self.body.push_front((cx, cy))   # Cabeza
        
        self.body_set = {(cx, cy), (cx-1, cy), (cx-2, cy)}
        
        self.direction = (1, 0) # Moviendo a la derecha (hacia cx+1) -> Espacio libre
        self.grow_queue = 0
        self.shield = False
        self.ghost_mode = False
        self.ghost_end_time = 0
        self.alive = True

        


    def move(self, obstacles: set):
        if not self.alive: return
        
        head = self.body.get_head_data()
        nx, ny = head[0] + self.direction[0], head[1] + self.direction[1]
        
        # Colisión Pared
        if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
            if self.shield:
                self.shield = False
                self.direction = (-self.direction[0], -self.direction[1])
                return
            else:
                self.alive = False; return
        
        #Colisión Obstáculo
        if (nx, ny) in obstacles:
            self.alive = False; return

        # Colisión Cuerpo
        if not self.ghost_mode:
            # Si choca con cuerpo Y no es la cola (la cola se va a mover)
            if (nx, ny) in self.body_set and (nx, ny) != self.body.tail.data:
                if self.shield: self.shield = False; return
                else: self.alive = False; return

        if self.ghost_mode and pygame.time.get_ticks() > self.ghost_end_time:
            self.ghost_mode = False

        self.body.push_front((nx, ny))
        self.body_set.add((nx, ny))

        if self.grow_queue > 0:
            self.grow_queue -= 1
        else:
            removed = self.body.pop_back()
            if removed in self.body_set:
                self.body_set.remove(removed)

    def apply_effect(self, food_type):
        if food_type == FoodType.APPLE: self.grow_queue += 1
        elif food_type == FoodType.BLUE_APPLE: self.grow_queue += 2
        elif food_type == FoodType.PURPLE_APPLE: self.grow_queue += 5
        elif food_type == FoodType.LEMON:
            for _ in range(3): 
                if self.body.size > 1: 
                    rem = self.body.pop_back()
                    if rem in self.body_set: self.body_set.remove(rem)
        elif food_type == FoodType.BERRY:
            while self.body.size > 1: 
                rem = self.body.pop_back()
                if rem in self.body_set: self.body_set.remove(rem)
        elif food_type == FoodType.BOMB:
            if self.shield: self.shield = False
            else: self.alive = False
