import pygame

# --- CONFIGURACIÓN GENERAL ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.font.init()
CLOCK = pygame.time.Clock()

# Dimensiones Fijas y Estables (800x600)
CELL_SIZE = 20 
GRID_W = 40  
GRID_H = 30  
SCREEN_WIDTH = GRID_W * CELL_SIZE  
SCREEN_HEIGHT = GRID_H * CELL_SIZE 

# Colores
C_BG = (30, 30, 40)
C_ACCENT = (50, 200, 50)  
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_RED = (200, 50, 50)
C_GOLD = (255, 215, 0)
C_GRAY = (100, 100, 100)
C_INFO = (100, 100, 180) 
C_OBSTACLE_ORANGE = (255, 120, 0) 
C_RETRO_GREEN = (0, 255, 0) 
C_RETRO_BLUE = (0, 150, 255) 


# Dificultades: {NOMBRE: [FPS_INICIAL, FPS_MINIMO, FPS_MAXIMO, AUMENTO_POR_FRUTA]}
DIFFICULTIES = {
    "FACIL": [2,2,10, 0.2],
    "NORMAL": [10,10,20, 0.15],
    "DIFICIL": [20,20,30, 0.1]
}

MAP_BACKGROUNDS = {
    "NEGRO ARCADE": (0, 0, 0),
    "ROJO OSCURO": (90, 20, 20), 
    "VERDE FÓSFORO": (20, 50, 20),
    "CLASICO (Verde)": (170, 215, 81) # Mantener el verde clásico si quieres
}

SKINS = {
    "default": {"name": "Normal", "price": 0, "color": (50, 205, 50), "acc": None},
    "blue": {"name": "Azul", "price": 50, "color": (30, 144, 255), "acc": None},
    "red": {"name": "Roja", "price": 50, "color": (220, 20, 60), "acc": None},
    "yellow": {"name": "Amarilla", "price": 50, "color": (255, 215, 0), "acc": None},
    "black": {"name": "Negra", "price": 100, "color": (30, 30, 30), "acc": None},
    "glasses": {"name": "Con Gafas", "price": 150, "color": (50, 205, 50), "acc": "glasses"},
    "beard": {"name": "Barbuda", "price": 200, "color": (50, 205, 50), "acc": "beard"},
    "hat": {"name": "Sombrero", "price": 200, "color": (50, 205, 50), "acc": "hat"},
    "old": {"name": "Viejita", "price": 300, "color": (150, 150, 150), "acc": "mustache"},
    "baby": {"name": "Bebé", "price": 300, "color": (144, 238, 144), "acc": "pacifier"}
}

MUSIC_END = pygame.USEREVENT + 1