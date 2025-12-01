import pygame
import sys
import json
import random
import os

from snake_game.configuracion import (
    CLOCK, SCREEN_WIDTH, SCREEN_HEIGHT, MUSIC_END,
    C_BG, C_ACCENT, C_WHITE, C_BLACK, C_RED, C_GOLD, C_GRAY, C_INFO, 
    C_OBSTACLE_ORANGE, C_RETRO_GREEN, C_RETRO_BLUE, DIFFICULTIES, MAP_BACKGROUNDS, CELL_SIZE, GRID_W, GRID_H, SKINS
)
from snake_game.estructuras_de_datos import FoodType, FOOD_DESC
from snake_game.logica import Snake, AssetManager, SoundSynth

class GameApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Proyecto DS")
        
        self.state = "MENU"
        self.data = self.load_data()
        self.current_difficulty = "FACIL"
        self.current_fps = DIFFICULTIES[self.current_difficulty][0] 
        
        self.assets = AssetManager()
        self.sound_synth = SoundSynth()
        self.snake = None
        self.active_fruits = {}
        self.active_obstacles = set()
        self.score = 0
        self.session_coins = 0
        self.music_list = self.assets.music_files
        self.current_track_index = 0
        self.play_next_track()
        self.current_background = MAP_BACKGROUNDS["NEGRO ARCADE"]
        self.MUSIC_END = pygame.USEREVENT + 1
        self.music_list = self.assets.music_files
        pygame.mixer.music.set_endevent(self.MUSIC_END)


    def load_data(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as f: return json.load(f)
        return {"coins": 0, "owned_skins": ["default"], "equipped_skin": "default"}

    def save_data(self):
        with open("savegame.json", "w") as f: json.dump(self.data, f)

    def play_snd(self, name):
        self.sound_synth.play(name)
    
    def play_next_track(self):
        """Carga y reproduce la siguiente canción de la lista."""
        if not self.music_list:
            return # No hay canciones
        
        #Obtener la ruta de la canción actual
        track_path = self.music_list[self.current_track_index]
        
        #Cargar y reproducir
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()
        
        #Preparar el índice para la siguiente canción (bucle)
        self.current_track_index = (self.current_track_index + 1) % len(self.music_list)

    def start_game(self):
        # Limpiar eventos viejos para evitar 'clicks' fantasma que giren la serpiente al inicio
        pygame.event.clear()
        self.snake = Snake()
        self.active_fruits = {}
        self.score = 0
        self.session_coins = 0
        self.spawn_food(force_red=True)
        self.state = "PLAYING"
        self.generate_obstacles()

    def generate_obstacles(self):
        """Genera bloques de obstáculos basados en la dificultad actual."""
        self.active_obstacles.clear()
        
        difficulty = self.current_difficulty
        
        if difficulty == "FACIL":
            num_blocks = 12
            block_length = 1
        
        # Parámetros por dificultad
        if difficulty == "NORMAL":
            # Pequeños bloques dispersos
            num_blocks = 16
            block_length = 3
        elif difficulty == "DIFICIL":
            # Bloques más largos y mayor cantidad
            num_blocks = 18
            block_length = 6
        
        for _ in range(num_blocks):
            # Posición de inicio aleatoria
            sx = random.randint(5, GRID_W - 5)
            sy = random.randint(5, GRID_H - 5)
            
            # Dirección del bloque (horizontal o vertical)
            direction = random.choice([(1, 0), (0, 1)])
            
            for i in range(block_length):
                pos = (sx + i * direction[0], sy + i * direction[1])
                
                # Asegurarse de que el bloque esté dentro de los límites y no en la posición inicial de la serpiente
                if 0 <= pos[0] < GRID_W and 0 <= pos[1] < GRID_H and pos not in self.snake.body_set:
                    self.active_obstacles.add(pos)

    def spawn_food(self, force_red=False):
        has_red = any(f == FoodType.APPLE for f in self.active_fruits.values())
        
        def get_pos():
            while True:
                x, y = random.randint(0, GRID_W-1), random.randint(0, GRID_H-1)
                if ((x,y) not in self.snake.body_set and 
                    (x,y) not in self.active_fruits and
                    (x,y) not in self.active_obstacles):
                    return (x,y)

        if not has_red or force_red:
            self.active_fruits[get_pos()] = FoodType.APPLE
            
        if len(self.active_fruits) < 3 and random.random() < 0.4:
             types = [FoodType.BLUE_APPLE, FoodType.PURPLE_APPLE, FoodType.LEMON, FoodType.BERRY, FoodType.BOMB]
             weights = [30, 10, 15, 10, 5]
             self.active_fruits[get_pos()] = random.choices(types, weights=weights, k=1)[0]

    # --- UI ---
    def draw_text(self, text, size, color, x, y, center=True):
        font = self.assets.fonts.get(size, self.assets.fonts[20])
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        self.screen.blit(surf, rect)

    def draw_retro_button(self, text, x, y, w, h, color_bg):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        rect = pygame.Rect(x, y, w, h)
        shade = 6
        c_dark = (max(0, color_bg[0] - 60), max(0, color_bg[1] - 60), max(0, color_bg[2] - 60))
        c_light = (min(255, color_bg[0] + 40), min(255, color_bg[1] + 40), min(255, color_bg[2] + 40))

        # Estado: Normal o Presionado
        is_pressed = rect.collidepoint(mouse) and click

        # Dibuja la base (sombra)
        pygame.draw.rect(self.screen, c_dark, (x, y + shade, w, h)) 
        
        #Dibuja el borde superior (luz)
        pygame.draw.rect(self.screen, c_light, (x, y, w, h), 2)
         
        #Dibuja el cuerpo del botón (con offset si está presionado)
        offset = shade if is_pressed else 0
        pygame.draw.rect(self.screen, color_bg, (x, y + offset, w, h))
        
        #Dibuja el texto (con offset si está presionado)
        self.draw_text(text, 24, C_BLACK, x + w//2, y + h//2 + offset)
        
        if rect.collidepoint(mouse) and click:
            # El sonido del click debe ir aquí, justo antes de devolver True
            self.play_snd("click")
            return True

        return False
    
    def screen_config(self):
        self.screen.fill(C_BG)
        self.screen.blit(self.assets.noise_texture, (0, 0))
        cx = SCREEN_WIDTH // 2
        
        self.draw_text("SELECCIÓN DE FONDO RETRO", 40, C_WHITE, cx, 100)
        
        y = 200
        for name, color in MAP_BACKGROUNDS.items():
            
            x_button = cx - 125
            w_button = 250
            h_button = 50
            
            # Comprobar si es el fondo actual para resaltarlo
            is_current = self.current_background == color
            col = C_ACCENT if is_current else C_GRAY
            
            if self.draw_retro_button(name, x_button, y, w_button, h_button, col):
                self.current_background = color 
                self.play_snd("click") 
                pygame.time.delay(200)
            
            # Dibujar la muestra de color
            pygame.draw.rect(self.screen, color, (cx + 150, y + 10, 30, 30), border_radius=5)
            
            y += 70
            
        if self.draw_retro_button("VOLVER", 20, 20, 100, 40, C_RED):
            self.state = "MENU"
            pygame.time.delay(200)

    def exit_game(self):
        """Maneja la salida del juego de forma limpia."""
        self.running = False 
        pygame.quit()       
        sys.exit()        

    # PANTALLAS 
    def screen_menu(self):
        self.screen.fill((20,20,60))
        self.screen.blit(self.assets.noise_texture, (0, 0)) # Añadir el ruido para el grano retro

        cx = SCREEN_WIDTH // 2

        offset = 3 # Desplazamiento de la sombra en píxeles

        self.draw_text("SUPER SNAKE DS", 60, C_BLACK, cx + offset, 80 + offset) 
        self.draw_text("SUPER SNAKE DS", 60, C_RETRO_GREEN, cx, 80)
        self.draw_text(f"> Dificultad: {self.current_difficulty} <", 20, C_RETRO_BLUE, cx, 130)

        bx = cx - 135
        

        if self.draw_retro_button("JUGAR", bx, 180, 270, 50, C_ACCENT):
            self.start_game(); pygame.time.delay(200)
        
        if self.draw_retro_button("DIFICULTAD", bx, 250, 270, 50, (100, 100, 150)):
            self.state = "DIFFICULTY"; pygame.time.delay(200)

        if self.draw_retro_button("TIENDA", bx, 320, 270, 50, (70, 70, 150)):
            self.state = "SHOP"; pygame.time.delay(200)
        
        if self.draw_retro_button("CONFIGURACIÓN MAPA", bx, 390, 270, 50, (150, 100, 50)):
            self.state = "CONFIG"
            pygame.time.delay(200)

        if self.draw_retro_button("GUÍA FRUTAS", bx, 460, 270, 50, C_INFO):
            self.state = "GUIDE"; pygame.time.delay(200)

        if self.draw_retro_button("SALIR", bx, 530, 270, 50, C_RED):
            self.exit_game() 
            pygame.time.delay(200)

    def screen_guide(self):
        self.screen.fill(C_BG)
        self.draw_text("GUÍA DE PODERES", 40, C_WHITE, SCREEN_WIDTH//2, 50)
        
        if self.draw_retro_button("VOLVER", 20, 20, 100, 40, C_RED):
            self.state = "MENU"; pygame.time.delay(200)
        
        # Grid de explicación
        start_y = 120
        col1_x = 100
        col2_x = 450
        
        i = 0
        for ftype, desc in FOOD_DESC.items():
            # 1. Determina la columna: 
            #    Si i < 3 (las primeras 3 frutas), usa col1_x (izquierda).
            #    Si i >= 3 (las siguientes), usa col2_x (derecha).
            x = col1_x if i < 3 else col2_x

            # 2. Determina la fila: Usa el resto de i dividido por 3.
            #    (0%3=0, 1%3=1, 2%3=2, 3%3=0, 4%3=1, 5%3=2)
            y = start_y + (i % 3) * 100 # Multiplica por 100 para dar espacio a la tarjeta
            
            # Fondo tarjeta
            pygame.draw.rect(self.screen, (40,40,50), (x, y, 320, 80), border_radius=10)
            
            # Icono
            icon = pygame.transform.scale(self.assets.textures[ftype], (40, 40))
            self.screen.blit(icon, (x + 20, y + 20))
            
            # Texto
            self.draw_text(desc, 22, C_GOLD, x + 80, y + 40, center=False)
            i += 1

    def screen_difficulty(self):
        self.screen.fill(C_BG)
        self.screen.blit(self.assets.noise_texture, (0, 0))
        self.draw_text("VELOCIDAD / DIFICULTAD", 40, C_WHITE, SCREEN_WIDTH//2, 100)
        y = 200
        for diff in DIFFICULTIES:
            col = C_ACCENT if diff == self.current_difficulty else C_GRAY
            if self.draw_retro_button(diff, SCREEN_WIDTH//2 - 100, y, 200, 50, col):
                self.current_difficulty = diff
                pygame.time.delay(200)
            y += 70
        if self.draw_retro_button("VOLVER", 20, 20, 100, 40, C_RED):
            self.state = "MENU"; pygame.time.delay(200)

    def screen_shop(self):
        self.screen.fill(C_BG)
        self.screen.blit(self.assets.noise_texture, (0, 0))
        self.draw_text("TIENDA", 40, C_WHITE, SCREEN_WIDTH//2, 50)
        self.draw_text(f"Monedas: {self.data['coins']}", 25, C_GOLD, SCREEN_WIDTH//2, 90)
        if self.draw_retro_button("VOLVER", 20, 20, 100, 40, C_RED):
            self.state = "MENU"; pygame.time.delay(200)

        start_x, start_y = 80, 140
        col, row = 0, 0
        for key, props in SKINS.items():
            x = start_x + col * 210
            y = start_y + row * 110
            rect = pygame.Rect(x, y, 200, 100)
            color_border = C_ACCENT if key == self.data["equipped_skin"] else C_GRAY
            pygame.draw.rect(self.screen, (50, 50, 60), rect, border_radius=8)
            pygame.draw.rect(self.screen, color_border, rect, 3, border_radius=8)
            
            head_preview = self.assets.get_snake_head(key, (1,0))
            self.screen.blit(pygame.transform.scale(head_preview, (40, 40)), (x+10, y+30))
            self.draw_text(props["name"], 20, C_WHITE, x+110, y+25)
            
            is_owned = key in self.data["owned_skins"]
            price_text = "LISTO" if is_owned else f"${props['price']}"
            self.draw_text(price_text, 18, C_GOLD if not is_owned else C_ACCENT, x+110, y+50)

            mouse = pygame.mouse.get_pos()
            if rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
                pygame.time.delay(200)
                if is_owned:
                    self.data["equipped_skin"] = key
                    self.play_snd("click")
                    self.save_data()
                elif self.data["coins"] >= props["price"]:
                    self.data["coins"] -= props["price"]
                    self.data["owned_skins"].append(key)
                    self.play_snd("buy")
                    self.save_data()
            
            col += 1
            if col > 2: col = 0; row += 1

    def screen_playing(self):
            
        self.snake.move(self.active_obstacles)

        if not self.snake.alive:
            self.play_snd("die")
            self.state = "GAMEOVER"
            self.data["coins"] += self.session_coins
            self.save_data()
            return

        head = self.snake.body.get_head_data()
        if head in self.active_fruits:
            ftype = self.active_fruits.pop(head)
            self.snake.apply_effect(ftype)
            
            if ftype != FoodType.BOMB and self.snake.alive:
                # Obtener la configuración de la dificultad
                _, _, max_fps, increase_rate = DIFFICULTIES[self.current_difficulty]
                
                # Aumento progresivo
                self.current_fps += increase_rate 
                
                # Límite Máximo
                self.current_fps = min(self.current_fps, max_fps)
            
            #Lógica especial para la BOMBA (a nivel 3 de indentación)
            if ftype == FoodType.BOMB:
                self.play_snd("die")
                if not self.snake.alive:
                    self.state = "GAMEOVER"
                    self.data["coins"] += self.session_coins
                    self.save_data()
                    return # Salimos del bucle si muere
            
            #Lógica para otros sonidos (a nivel 3 de indentación)
            elif ftype in [FoodType.APPLE, FoodType.LEMON]: 
                self.play_snd("eat")
            
            
            else: 
                self.play_snd("eat")

            #Aumento de puntaje y spawn (a nivel 3 de indentación)
            self.score += 10
            self.session_coins += 1
            self.spawn_food()

        self.screen.fill(self.current_background) # Fondo juego (usa el color seleccionado)
        
        self.screen.blit(self.assets.noise_texture, (0, 0))

        for x, y in self.active_obstacles:
            
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, C_OBSTACLE_ORANGE, rect)
            pygame.draw.rect(self.screen, C_BLACK, rect, 1) 

        for pos, ftype in self.active_fruits.items():
            self.screen.blit(self.assets.textures[ftype], (pos[0]*CELL_SIZE, pos[1]*CELL_SIZE))
            
        skin_key = self.data["equipped_skin"]
        current = self.snake.body.head
        is_head = True
        while current:
            x, y = current.data[0]*CELL_SIZE, current.data[1]*CELL_SIZE
            if is_head:
                head_s = self.assets.get_snake_head(skin_key, self.snake.direction)
                self.screen.blit(head_s, (x,y))
                is_head = False
            else:
                body_s = self.assets.get_snake_body(skin_key)
                self.screen.blit(body_s, (x,y))
            current = current.next

        self.draw_text(f"Puntos: {self.score}", 20, C_WHITE, 60, 20)
        if self.snake.shield: self.draw_text("ESCUDO", 20, C_GOLD, SCREEN_WIDTH-50, 20)
        pygame.display.flip()

    def screen_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 180))
        self.screen.blit(overlay, (0,0))
        
        cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        self.draw_text("¡PERDISTE!", 50, C_RED, cx, cy - 50)
        self.draw_text(f"Puntaje: {self.score}", 30, C_WHITE, cx, cy)
        self.draw_text(f"Monedas ganadas: {self.session_coins}", 30, C_GOLD, cx, cy + 40)

        # Llama a self.start_game(), que reinicia el juego.
        if self.draw_retro_button("REINICIAR", cx - 100, cy + 100, 200, 50, C_ACCENT):
            self.start_game()
            pygame.time.delay(200)
        
        if self.draw_retro_button("MENU PRINCIPAL", cx - 100, cy + 170, 200, 50, C_INFO):
            self.state = "MENU"
            pygame.time.delay(200)

    def run(self):
        while True:
        
            if self.state == "MENU": self.screen_menu()
            elif self.state == "GUIDE": self.screen_guide()
            elif self.state == "DIFFICULTY": self.screen_difficulty()
            elif self.state == "SHOP": self.screen_shop()
            elif self.state == "CONFIG": self.screen_config()
            elif self.state == "PLAYING": self.screen_playing()
            elif self.state == "GAMEOVER": self.screen_gameover()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == self.MUSIC_END:
                    self.play_next_track()

                if self.state == "PLAYING" and event.type == pygame.KEYDOWN: 
                    d = self.snake.direction
                    if event.key == pygame.K_UP and d != (0, 1): self.snake.direction = (0, -1)
                    if event.key == pygame.K_DOWN and d != (0, -1): self.snake.direction = (0, 1)
                    if event.key == pygame.K_LEFT and d != (1, 0): self.snake.direction = (-1, 0)
                    if event.key == pygame.K_RIGHT and d != (-1, 0): self.snake.direction = (1, 0)
                
                
            
            if self.state == "PLAYING":
                fps = self.current_fps
            else:
               fps = 30
            if self.state != "PLAYING": pygame.display.flip()
            CLOCK.tick(fps)

if __name__ == "__main__":
    GameApp().run()