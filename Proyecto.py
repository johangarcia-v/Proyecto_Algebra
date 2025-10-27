import pygame
import random
import sys
import time
import os
import math
from pygame import mixer
from datetime import datetime
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("Para exportar a Excel, instala openpyxl con: pip install openpyxl")

# Inicializar Pygame y el mixer para el sonido
pygame.init()
mixer.init()

# Función para crear fuente con fallback
def create_font(size, is_pixel=False, bold=False):
    font_list = ['arial', 'helvetica', 'verdana']
    for font_name in font_list:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    return pygame.font.SysFont('arial', size, bold=bold)

# Crear las fuentes con los diferentes estilos
font = create_font(20)
large_font = create_font(26, bold=True)
title_font = create_font(36, bold=True)
number_font = create_font(18)

# Configuración del juego
NUM_COLORS = 6
COLOR_MAP = [
    (255, 0, 0),     # Rojo
    (0, 255, 0),     # Verde
    (0, 0, 255),     # Azul
    (255, 255, 0),   # Amarillo
    (255, 0, 255),   # Magenta
    (0, 255, 255),   # Cian
]

# Configuración de la ventana y juego
class Config:
    ANCHO = 1200
    ALTO = 800
    TAMANO_CELDA = 64
    FILAS = 8
    COLUMNAS = 8
    RIGHT_PANEL_WIDTH = 360
    LEFT_WIDTH = ANCHO - RIGHT_PANEL_WIDTH
    MARGEN_SUPERIOR = (ALTO - (FILAS * TAMANO_CELDA)) // 2
    MARGEN_IZQUIERDO = (LEFT_WIDTH - (COLUMNAS * TAMANO_CELDA)) // 2
    BLANCO = (255, 255, 255)
    NEGRO = (0, 0, 0)
    CAFE_CLARO = (195, 155, 110)
    GRIS = (230, 230, 230)

ANCHO = Config.ANCHO
ALTO = Config.ALTO
TAMANO_CELDA = Config.TAMANO_CELDA
FILAS = Config.FILAS
COLUMNAS = Config.COLUMNAS
RIGHT_PANEL_WIDTH = Config.RIGHT_PANEL_WIDTH
LEFT_WIDTH = Config.LEFT_WIDTH
MARGEN_SUPERIOR = Config.MARGEN_SUPERIOR
MARGEN_IZQUIERDO = Config.MARGEN_IZQUIERDO
BLANCO = Config.BLANCO
NEGRO = Config.NEGRO
CAFE_CLARO = Config.CAFE_CLARO
GRIS = Config.GRIS

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Candy Matrix - Proyecto Algebra Lineal')

# Gestor de sonidos del juego
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._load_sounds()
        self._setup_music()
    
    def _load_sounds(self):
        sound_files = {
            'explosion': os.path.join('sounds', 'bubble-pop-06-351337.mp3')
        }
        
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = mixer.Sound(path)
                except Exception as e:
                    print(f'No se pudo cargar el sonido {name}:', e)
    
    def _setup_music(self):
        music_path = os.path.join('sounds', 'background_music.mp3')
        if os.path.exists(music_path):
            try:
                mixer.music.load(music_path)
                mixer.music.set_volume(0.5)
                mixer.music.play(-1)
            except Exception as e:
                print('No se pudo reproducir la música:', e)
    
    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

sound_manager = SoundManager()

# Clase Habilidad
class Habilidad:
    BOMBA = 'bomb'
    ARCOIRIS = 'rainbow'
    ESTRELLA = 'star'
    
    @staticmethod
    def get_all_types():
        return [Habilidad.BOMBA, Habilidad.ARCOIRIS, Habilidad.ESTRELLA]

def show_start_menu():
    """Muestra el menú de inicio con información del juego."""
    running = True
    while running:
        ventana.fill((250, 245, 240))
        
        # Título centrado con efecto de sombra
        title_shadow = title_font.render('CANDY MATRIX', True, (160, 80, 40))
        title = title_font.render('CANDY MATRIX', True, (200, 100, 50))
        title_rect = title.get_rect(center=(ANCHO//2, 60))
        ventana.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        ventana.blit(title, title_rect)
        
        # Subtítulo
        subtitle = large_font.render('Aprendizaje Interactivo de Álgebra Lineal', True, (60,60,60))
        subtitle_rect = subtitle.get_rect(center=(ANCHO//2, 110))
        ventana.blit(subtitle, subtitle_rect)
        
        # Crear secciones con mejor espaciado
        sections = [
            {
                'title': 'OBJETIVOS',
                'items': [
                    "Combina caramelos iguales para puntuación",
                    "Alcanza objetivos de nivel antes del tiempo",
                    "Aprende respondiendo preguntas"
                ]
            },
            {
                'title': 'REGLAS',
                'items': [
                    "Intercambia caramelos adyacentes en líneas",
                    "Usa habilidades respondiendo correctamente",
                    "Completa el objetivo antes del tiempo"
                ]
            },
            {
                'title': 'CARACTERÍSTICAS',
                'items': [
                    "Zona de estudio con explicaciones",
                    "Exportación de datos a Excel",
                    "Niveles progresivos"
                ]
            }
        ]
        
        # Dibujar secciones
        y = 150
        section_padding = 15
        for section in sections:
            title_surf = number_font.render(section['title'], True, (180, 100, 60))
            title_rect = title_surf.get_rect(centerx=ANCHO//2, y=y)
            ventana.blit(title_surf, title_rect)
            y += 28
            
            for item in section['items']:
                text_surf = font.render(item, True, (40,40,40))
                text_rect = text_surf.get_rect(centerx=ANCHO//2, y=y)
                ventana.blit(text_surf, text_rect)
                y += 20
            
            y += section_padding
        
        # Botón de inicio
        btn_w, btn_h = 220, 60
        btn_rect = pygame.Rect((ANCHO-btn_w)//2, ALTO-90, btn_w, btn_h)
        
        shadow_rect = btn_rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(ventana, (160, 80, 40), shadow_rect, border_radius=12)
        pygame.draw.rect(ventana, (200, 100, 50), btn_rect, border_radius=12)
        pygame.draw.rect(ventana, (220, 120, 70), btn_rect, border_radius=12, width=2)
        
        start_text = number_font.render('COMENZAR', True, BLANCO)
        text_rect = start_text.get_rect(center=btn_rect.center)
        shadow_text = number_font.render('COMENZAR', True, (160, 80, 40))
        ventana.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        ventana.blit(start_text, text_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False

def truncate_filename(filepath, max_length=50):
    """Recorta el nombre del archivo para no hacer el texto muy largo."""
    if len(filepath) <= max_length:
        return filepath
    # Mostrar inicio + "..." + final
    start_len = max_length // 2 - 5
    end_len = max_length // 2 - 2
    return filepath[:start_len] + "..." + filepath[-end_len:]

def export_to_excel():
    if not EXCEL_AVAILABLE:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumen del Juego"

    title_font_style = Font(bold=True, size=14)
    header_font_style = Font(bold=True, size=11, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

    ws.merge_cells('A1:E1')
    ws['A1'] = "CANDY MATRIX - RESUMEN DEL JUEGO"
    ws['A1'].font = title_font_style
    ws['A1'].alignment = openpyxl.styles.Alignment(horizontal='center')

    info_rows = [
        ("Fecha", datetime.now().strftime("%Y-%m-%d %H:%M"), "Momento en que se generó el reporte"),
        ("Nivel alcanzado", globals().get('level', 'N/A'), "Nivel alcanzado por el jugador"),
        ("Puntuación final", globals().get('score', 0), "Puntos totales obtenidos"),
        ("Movimientos totales", globals().get('moves_count', 0), "Número de intercambios realizados")
    ]

    start_row = 3
    for i, (campo, valor, explicacion) in enumerate(info_rows, start_row):
        ws.cell(row=i, column=1, value=campo)
        ws.cell(row=i, column=2, value=valor)
        ws.cell(row=i, column=3, value=explicacion)
        ws.cell(row=i, column=1).font = header_font_style
        ws.cell(row=i, column=1).fill = header_fill

    stats = matrix_stats()
    stats_row = start_row + len(info_rows) + 2
    ws.cell(row=stats_row, column=1, value="ESTADÍSTICAS DE MATRIZ FINAL").font = title_font_style
    
    stat_items = [
        ("Suma total", stats['sum'], "Suma de todos los valores"),
        ("Promedio", round(stats['mean'], 2), "Promedio de valores"),
        ("Mínimo", stats['min'], "Valor mínimo"),
        ("Máximo", stats['max'], "Valor máximo")
    ]
    
    for idx, (campo, valor, explicacion) in enumerate(stat_items, 1):
        r = stats_row + idx
        ws.cell(row=r, column=1, value=campo)
        ws.cell(row=r, column=2, value=valor)
        ws.cell(row=r, column=3, value=explicacion)

    ws2 = wb.create_sheet(title="Historial de Matrices")
    ws2.cell(row=1, column=1, value="Movimiento").font = header_font_style
    ws2.cell(row=1, column=2, value="Evento").font = header_font_style
    ws2.cell(row=1, column=1).fill = header_fill
    ws2.cell(row=1, column=2).fill = header_fill

    row = 2
    hist = globals().get('matrix_history', [])
    events = globals().get('game_events', [])
    for idx, matrix in enumerate(hist, 1):
        evento = events[idx-1] if idx-1 < len(events) else ''
        ws2.cell(row=row, column=1, value=f"Movimiento {idx}")
        ws2.cell(row=row, column=2, value=evento)
        row += 1
        for i, matrix_row in enumerate(matrix):
            for j, val in enumerate(matrix_row):
                ws2.cell(row=row+i, column=j+1, value=("#" if val is None else val))
        row += len(matrix) + 1

    ws3 = wb.create_sheet(title="Explicación")
    ws3.cell(row=1, column=1, value="Campo").font = header_font_style
    ws3.cell(row=1, column=2, value="Descripción").font = header_font_style
    ws3.cell(row=1, column=1).fill = header_fill
    ws3.cell(row=1, column=2).fill = header_fill
    
    explanations = [
        ("Fecha", "Fecha y hora en que se generó el reporte"),
        ("Nivel alcanzado", "Nivel del jugador en el momento del reporte"),
        ("Puntuación final", "Puntos acumulados en la sesión"),
        ("Movimientos totales", "Número total de movimientos/intercambios realizados"),
        ("ESTADÍSTICAS", "Resumen estadístico de la matriz: suma, promedio, min y max"),
        ("Historial", "Registros de movimientos con matriz tras cada movimiento")
    ]
    
    for i, (campo, desc) in enumerate(explanations, 2):
        ws3.cell(row=i, column=1, value=campo)
        ws3.cell(row=i, column=2, value=desc)

    from openpyxl.utils import get_column_letter
    for sheet in [ws, ws2, ws3]:
        for col in range(1, sheet.max_column + 1):
            col_letter = get_column_letter(col)
            max_length = 0
            for cell in sheet[col_letter]:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            sheet.column_dimensions[col_letter].width = min(50, max_length + 4)

    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.isdir(downloads):
        downloads = os.getcwd()
    filename = f"candy_matrix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    fullpath = os.path.join(downloads, filename)
    wb.save(fullpath)
    return fullpath

# Variables de juego
MAX_LEVEL = 5
LEVEL_TIME = 180
level_start_time = time.time()
goal_base = 500
game_start_time = time.time()
last_explosions = []
hover_cell = None
skills_on_map = {}

questions = [
    ("La suma de matrices A+B es conmutativa", True),
    ("El producto de matrices AB = BA siempre", False),
    ("Una matriz singular es no invertible", True),
    ("El rango de una matriz es <= min(m,n)", True),
    ("Toda matriz es diagonalizable", False),
    ("tr(AB) = tr(BA) para toda matriz", True),
    ("Los autovalores son únicos", True),
    ("La traza es la suma de autovalores", True),
    ("Una matriz simétrica es diagonalizable", True),
    ("det(AB) = det(A)det(B)", True),
    ("La inversa de una matriz ortogonal es su transpuesta", True),
    ("Una matriz triangular superior no tiene autovalores", False),
    ("El espacio nulo es un subespacio vectorial", True),
    ("Los autovectores de valores distintos son LI", True),
    ("Una matriz idempotente cumple A^2 = A", True)
]

quiz_cooldown_until = 0
skill_success_cooldown_until = 0
MAX_SKILL_USES_PER_LEVEL = 4
skill_uses_this_level = 0
asked_questions = set()

floating_popups = []

def make_mcq(question_text, correct_answer, distractors=None):
    """Crear estructura MCQ con opciones mezcladas."""
    if distractors is None:
        distractors = []
    options = [str(correct_answer)] + [str(d) for d in distractors]
    random.shuffle(options)
    correct_idx = options.index(str(correct_answer))
    
    words = question_text.split()
    lines = []
    cur = words[0] if words else ''
    for w in words[1:]:
        if len(cur + ' ' + w) <= 35:
            cur += ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return {'lines': lines, 'options': options, 'correct_idx': correct_idx}

def generate_matrix_mcq():
    """Genera una pregunta basada en la matriz actual."""
    typ = random.choice(['row_sum', 'col_sum', 'cell_val'])
    if typ == 'row_sum':
        r = random.randrange(FILAS)
        correct = sum(v for v in tablero[r] if isinstance(v, int) and v >= 0)
        distractors = [correct + random.randint(-3, -1), correct + random.randint(1, 4)]
        q = f'Suma fila {r}: ?'
        return make_mcq(q, correct, distractors)
    elif typ == 'col_sum':
        c = random.randrange(COLUMNAS)
        colvals = [tablero[i][c] for i in range(FILAS) if isinstance(tablero[i][c], int) and tablero[i][c] >= 0]
        correct = sum(colvals)
        distractors = [correct + random.randint(-4, -1), correct + random.randint(1, 5)]
        q = f'Suma columna {c}: ?'
        return make_mcq(q, correct, distractors)
    else:
        i = random.randrange(FILAS)
        j = random.randrange(COLUMNAS)
        val = tablero[i][j]
        correct = val if isinstance(val, int) and val >= 0 else 0
        distractors = [correct + 1, correct - 1]
        q = f'Valor celda ({i},{j}): ?'
        return make_mcq(q, correct, distractors)

def draw_row_sums_bar(surface, area_rect):
    """Dibuja un gráfico de barras con sumas de filas."""
    row_sums = [sum(v for v in row if isinstance(v, int) and v >= 0) for row in tablero]
    if not row_sums:
        return
    maxv = max(row_sums)
    padding = 8
    gw = area_rect.width - 2*padding
    gh = area_rect.height - 2*padding
    bar_w = gw / len(row_sums) - 6
    
    for i, val in enumerate(row_sums):
        x = area_rect.x + padding + i * (bar_w + 6)
        h = int((val / maxv) * (gh - 20)) if maxv > 0 else 0
        y = area_rect.y + area_rect.height - padding - h
        pygame.draw.rect(surface, (100,180,220), (x, y, int(bar_w), h))
        lbl = font.render(str(val), True, (20,20,20))
        surface.blit(lbl, (x, y - 18))
    
    surface.blit(font.render('Suma por fila', True, (10,10,10)), (area_rect.x + padding, area_rect.y + 4))

def draw_transform_demo(surface, area_rect):
    """Dibuja una demo de transformación 2D."""
    M = [[1.2, 0.6], [-0.5, 1.0]]
    cx = area_rect.x + area_rect.width // 2
    cy = area_rect.y + area_rect.height // 2
    scale = min(area_rect.width, area_rect.height) * 0.18
    pts = [(0,0), (1,0), (1,1), (0,1), (0,0)]
    
    pygame.draw.line(surface, (180,180,180), (cx - scale*2, cy), (cx + scale*2, cy), 1)
    pygame.draw.line(surface, (180,180,180), (cx, cy - scale*2), (cx, cy + scale*2), 1)
    
    transformed = []
    for (x,y) in pts:
        tx = M[0][0]*x + M[0][1]*y
        ty = M[1][0]*x + M[1][1]*y
        sx = cx + tx * scale
        sy = cy - ty * scale
        transformed.append((int(sx), int(sy)))
    pygame.draw.lines(surface, (220,100,80), False, transformed, 3)
    
    orig = []
    for (x,y) in pts:
        ox = cx + x * scale
        oy = cy - y * scale
        orig.append((int(ox), int(oy)))
    pygame.draw.lines(surface, (120,120,120), False, orig, 1)
    surface.blit(font.render('Transformacion 2D', True, (10,10,10)), (area_rect.x + 6, area_rect.y + 4))

LEARN_PAGES = [
    ("Matrices y operaciones", [
        "Una matriz es tabla de numeros en filas y columnas.",
        "Operaciones: suma, resta, multiplicacion.",
        "Observa como los numeros cambian con operaciones."
    ]),
    ("Rango y soluciones", [
        "Rango: columnas/filas linealmente independientes.",
        "Si det(A) != 0, la matriz es invertible.",
        "Autovalores: vectores que solo cambian de escala."
    ]),
    ("Ejemplos practicos", [
        "Calcula determinantes de 2x2: ad - bc.",
        "Usa el juego para conectar numeros y conceptos.",
        "Explora por que una matriz singular sin inversa."
    ]),
    ("Consejos de estudio", [
        "Practica con ejercicios cortos.",
        "Haz tarjetas de definiciones clave.",
        "Divide: 20min teoria + 20min practica."
    ])
]

def show_learn_screen():
    """Pantalla de mini-lección modal."""
    global level_start_time
    tiempo_pausa = time.time()
    page = 0
    clock = pygame.time.Clock()
    
    while True:
        w = 900
        h = 520
        rx = (ANCHO - w)//2
        ry = (ALTO - h)//2
        rect = pygame.Rect(rx, ry, w, h)
        btn_prev = pygame.Rect(rect.x + 20, rect.y + h - 64, 120, 40)
        btn_next = pygame.Rect(rect.x + rect.width - 140, rect.y + h - 64, 120, 40)
        btn_close = pygame.Rect(rect.x + rect.width//2 - 60, rect.y + h - 64, 120, 40)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    tiempo_actual = time.time()
                    tiempo_pausado = tiempo_actual - tiempo_pausa
                    level_start_time += tiempo_pausado
                    return
                if ev.key == pygame.K_RIGHT:
                    page = min(page + 1, len(LEARN_PAGES) - 1)
                if ev.key == pygame.K_LEFT:
                    page = max(page - 1, 0)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if btn_next.collidepoint(mx, my):
                    page = min(page + 1, len(LEARN_PAGES) - 1)
                if btn_prev.collidepoint(mx, my):
                    page = max(page - 1, 0)
                if btn_close.collidepoint(mx, my):
                    tiempo_actual = time.time()
                    tiempo_pausado = tiempo_actual - tiempo_pausa
                    level_start_time += tiempo_pausado
                    return

        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((10, 10, 10, 200))
        ventana.blit(s, (0, 0))
        pygame.draw.rect(ventana, (245,245,255), rect, border_radius=12)
        pygame.draw.rect(ventana, (200,200,200), rect, 2, border_radius=12)

        title, lines = LEARN_PAGES[page]
        ventana.blit(large_font.render(title, True, (20,20,20)), (rect.x + 24, rect.y + 18))
        
        y_offset = rect.y + 70
        for l in lines:
            text_surf = font.render('- ' + l, True, (40,40,40))
            ventana.blit(text_surf, (rect.x + 24, y_offset))
            y_offset += 25

        y_offset += 30
        viz_area = pygame.Rect(rect.x + (rect.width - 400)//2, y_offset + 30, 400, 160)
        if title == 'Matrices y operaciones':
            draw_row_sums_bar(ventana, viz_area)
        elif title == 'Rango y soluciones':
            draw_transform_demo(ventana, viz_area)
        elif title == 'Ejemplos practicos':
            m2x2 = [[1, 2], [3, 4]]
            det = m2x2[0][0]*m2x2[1][1] - m2x2[0][1]*m2x2[1][0]
            ventana.blit(font.render('Ejemplo 2x2:', True, (20,20,20)), (viz_area.x + 6, viz_area.y + 6))
            ventana.blit(font.render(f'[{m2x2[0][0]} {m2x2[0][1]}]', True, (20,20,20)), (viz_area.x + 6, viz_area.y + 36))
            ventana.blit(font.render(f'[{m2x2[1][0]} {m2x2[1][1]}]', True, (20,20,20)), (viz_area.x + 6, viz_area.y + 60))
            ventana.blit(font.render(f'det = {det}', True, (120,10,10)), (viz_area.x + 6, viz_area.y + 96))

        btn_width = 100
        btn_height = 35
        spacing = 20
        btn_prev = pygame.Rect(rect.x + spacing, rect.y + h - 50, btn_width, btn_height)
        btn_next = pygame.Rect(rect.x + rect.width - btn_width - spacing, rect.y + h - 50, btn_width, btn_height)
        btn_close = pygame.Rect(rect.x + (rect.width - btn_width)//2, rect.y + h - 50, btn_width, btn_height)
        
        pygame.draw.rect(ventana, (200,200,200), btn_prev, border_radius=6)
        pygame.draw.rect(ventana, (200,200,200), btn_next, border_radius=6)
        pygame.draw.rect(ventana, (180, 120, 120), btn_close, border_radius=6)
        
        for btn, texto in [(btn_prev, 'Anterior'), (btn_next, 'Siguiente'), (btn_close, 'Cerrar')]:
            txt_surf = font.render(texto, True, (0,0,0))
            txt_rect = txt_surf.get_rect(center=btn.center)
            ventana.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(30)

def dibujar_interface():
    ventana.fill((245, 230, 235))
    panel_rect = pygame.Rect(10, 10, LEFT_WIDTH-20, ALTO-20)
    pygame.draw.rect(ventana, (195, 155, 110), panel_rect, border_radius=20)
    
    stripe_color1 = (160, 82, 45)
    stripe_color2 = (205, 133, 63)
    spacing = 15
    
    for x in range(panel_rect.x, panel_rect.x + panel_rect.width, spacing):
        pygame.draw.line(ventana, stripe_color1, (x, panel_rect.y), (x, panel_rect.y + panel_rect.height), 2)
    for y in range(panel_rect.y, panel_rect.y + panel_rect.height, spacing*2):
        for x in range(panel_rect.x, panel_rect.x + panel_rect.width - spacing, spacing*2):
            pygame.draw.rect(ventana, stripe_color2, (x, y, spacing, spacing))
    pygame.draw.rect(ventana, stripe_color2, (panel_rect.x, panel_rect.y, panel_rect.width, spacing*2), border_radius=20)

    pygame.draw.rect(ventana, Config.CAFE_CLARO, (LEFT_WIDTH, 0, RIGHT_PANEL_WIDTH, ALTO))

    for i in range(FILAS):
        for j in range(COLUMNAS):
            x = MARGEN_IZQUIERDO + j * TAMANO_CELDA + TAMANO_CELDA // 2
            y = MARGEN_SUPERIOR + i * TAMANO_CELDA + TAMANO_CELDA // 2
            radius = TAMANO_CELDA // 2 - 8

            cell_bg = pygame.Surface((TAMANO_CELDA-8, TAMANO_CELDA-8), pygame.SRCALPHA)
            pygame.draw.rect(cell_bg, (0,0,0,30), (0,0,TAMANO_CELDA-8,TAMANO_CELDA-8), border_radius=8)
            ventana.blit(cell_bg, (x - (TAMANO_CELDA-8)//2, y - (TAMANO_CELDA-8)//2))

            if tablero[i][j] is not None:
                color = COLOR_MAP[tablero[i][j]]
                pygame.draw.circle(ventana, (80, 50, 60), (x+2, y+4), radius+2)
                pygame.draw.circle(ventana, (230, 230, 230), (x, y), radius+1)
                pygame.draw.circle(ventana, color, (x, y), radius)
                shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.ellipse(shine, (255,255,255,90), (int(radius*0.1), int(radius*0.05), int(radius*0.9), int(radius*0.6)))
                ventana.blit(shine, (x - radius, y - radius))

            if (i, j) in skills_on_map:
                val = skills_on_map[(i, j)]
                if isinstance(val, tuple):
                    typ, orig_color = val
                else:
                    typ = val
                    orig_color = None
                if typ == 'bomb':
                    pygame.draw.circle(ventana, (40, 40, 40), (x, y), radius)
                    pygame.draw.line(ventana, (255, 50, 50), (x, y-radius+2), (x+4, y-radius-6), 3)
                    pygame.draw.circle(ventana, (255, 200, 50), (x+4, y-radius-6), 3)
                    shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shine, (255,255,255,40), (radius*0.5, radius*0.5, radius, radius))
                    ventana.blit(shine, (x - radius, y - radius))
                elif typ == 'rainbow':
                    t = time.time() * 2
                    for angle in range(0, 360, 30):
                        rad = math.radians(angle + t * 30)
                        color = pygame.Color(0)
                        color.hsva = (angle % 360, 100, 100, 100)
                        start = (x + math.cos(rad)*radius*0.5, y + math.sin(rad)*radius*0.5)
                        end = (x + math.cos(rad)*radius*0.9, y + math.sin(rad)*radius*0.9)
                        pygame.draw.line(ventana, color, start, end, 3)
                    pygame.draw.circle(ventana, (255,255,255), (x, y), int(radius*0.4))
                elif typ == 'star':
                    pygame.draw.circle(ventana, (255, 215, 0), (x, y), radius)
                    t = time.time() * 3
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle + t * 30)
                        length = radius * (0.5 + math.sin(t*2 + angle*0.1) * 0.2)
                        end_x = x + math.cos(rad) * length
                        end_y = y + math.sin(rad) * length
                        pygame.draw.line(ventana, (255, 255, 200), (x, y), (end_x, end_y), 2)
                    shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shine, (255,255,255,128), (radius*0.6, radius*0.6, radius*0.8, radius*0.8))
                    ventana.blit(shine, (x - radius, y - radius))

    if seleccionado:
        i, j = seleccionado
        x = MARGEN_IZQUIERDO + j * TAMANO_CELDA
        y = MARGEN_SUPERIOR + i * TAMANO_CELDA
        pygame.draw.rect(ventana, BLANCO, (x-3, y-3, TAMANO_CELDA+6, TAMANO_CELDA+6), 3, border_radius=10)

    if hover_cell:
        hi, hj = hover_cell
        if 0 <= hi < FILAS and 0 <= hj < COLUMNAS:
            hx = MARGEN_IZQUIERDO + hj * TAMANO_CELDA
            hy = MARGEN_SUPERIOR + hi * TAMANO_CELDA
            s = pygame.Surface((TAMANO_CELDA-4, TAMANO_CELDA-4), pygame.SRCALPHA)
            s.fill((255,255,255,30))
            ventana.blit(s, (hx, hy))

    now = time.time()
    new_expl = []
    for cells, t0 in last_explosions:
        age = now - t0
        if age > 0.6:
            continue
        new_expl.append((cells, t0))
        for (i, j) in cells:
            cx = MARGEN_IZQUIERDO + j * TAMANO_CELDA + TAMANO_CELDA//2 - 2
            cy = MARGEN_SUPERIOR + i * TAMANO_CELDA + TAMANO_CELDA//2 - 2
            radius = int(6 + age * 30)
            alpha = int(200 * (1 - age/0.6))
            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255,255,255,alpha), (radius, radius), radius)
            ventana.blit(surf, (cx - radius + 2, cy - radius + 2))
    last_explosions[:] = new_expl

    draw_right_panel()

    now = time.time()
    to_remove = []
    for idx, p in enumerate(floating_popups):
        age = now - p['start']
        if age > p['duration']:
            to_remove.append(idx)
            continue
        y = p['y'] + p['vy'] * age
        max_popup_w = min(ANCHO - 40, 520)
        padding_x = 12
        padding_y = 8

        icon = p.get('icon', None)
        icon_space = 0
        icon_size = 0
        if icon:
            icon_size = 18
            icon_space = icon_size + 8

        max_text_w_allowed = max_popup_w - padding_x*2 - icon_space
        rendered_lines = []
        for line in p['lines']:
            if len(line) > 40:
                rendered_lines.append(line[:37] + "...")
            else:
                rendered_lines.append(line)

        line_surfs = [font.render(line, True, (255,255,255)) for line in rendered_lines]
        max_text_w = max((surf.get_width() for surf in line_surfs), default=0)
        total_text_h = sum(surf.get_height() for surf in line_surfs) + (len(line_surfs)-1) * 6

        w = max(200, max_text_w + padding_x * 2 + icon_space)
        w = min(w, max_popup_w)
        h = total_text_h + padding_y * 2

        rect_x = p.get('x', ANCHO//2 - w//2)
        if rect_x + w > ANCHO - 10:
            rect_x = max(10, ANCHO - w - 10)
        if rect_x < 10:
            rect_x = 10

        rect = pygame.Rect(rect_x, int(y), w, h)

        fade_in = 0.12
        fade_out = min(0.3, p['duration'] * 0.25)
        alpha_factor = 1.0
        if age < fade_in and fade_in > 0:
            alpha_factor = age / fade_in
        elif age > (p['duration'] - fade_out) and fade_out > 0:
            alpha_factor = max(0.0, (p['duration'] - age) / fade_out)
        alpha255 = int(220 * alpha_factor)

        s = pygame.Surface((w, h), pygame.SRCALPHA)
        try:
            pygame.draw.rect(s, (*p['color'], alpha255), s.get_rect(), border_radius=8)
        except Exception:
            s.fill((*p['color'], alpha255))
        ventana.blit(s, rect.topleft)

        text_x = rect.x + padding_x
        if icon:
            icon_x = rect.x + padding_x
            icon_y = rect.y + padding_y + (h - padding_y*2 - icon_size)//2
            icon_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            icon_surf.fill((0,0,0,0))
            pygame.draw.circle(icon_surf, (255,255,255, alpha255), (icon_size//2, icon_size//2), icon_size//2)
            if icon == 'check':
                cx = icon_size//2
                cy = icon_size//2
                pygame.draw.line(icon_surf, (30,160,60, alpha255), (4, icon_size//2), (icon_size//2, icon_size-5), 3)
                pygame.draw.line(icon_surf, (30,160,60, alpha255), (icon_size//2, icon_size-5), (icon_size-4, 6), 3)
            ventana.blit(icon_surf, (icon_x, icon_y))
            text_x += icon_space

        y_off = rect.y + padding_y
        for surf in line_surfs:
            surf.set_alpha(int(255 * alpha_factor))
            ventana.blit(surf, (text_x, y_off))
            y_off += surf.get_height() + 6
    for i in reversed(to_remove):
        floating_popups.pop(i)

def draw_right_panel():
    padding = 20
    x0 = LEFT_WIDTH + padding
    y0 = padding

    title = large_font.render(f'Nivel {level}', True, BLANCO)
    ventana.blit(title, (x0, y0))

    y_matrix = y0 + 40
    cell_h = 20
    for i in range(FILAS):
        row_text = ' '.join('#' if tablero[i][j] is None else str(tablero[i][j]) for j in range(COLUMNAS))
        surf = font.render(row_text, True, BLANCO)
        ventana.blit(surf, (x0, y_matrix + i * (cell_h+1)))

    y_stats = y_matrix + FILAS * (cell_h+1) + 15
    stats = [
        f'Puntos: {score}',
        f'Movimientos: {moves_count}',
        f'Tiempo: {max(0, int(LEVEL_TIME - (time.time() - level_start_time)))}s',
        f'Objetivo: {goal_for_level()}'
    ]
    for i, s in enumerate(stats):
        ventana.blit(font.render(s, True, BLANCO), (x0, y_stats + i * 22))

    btn_rect = pygame.Rect(LEFT_WIDTH + 30, ALTO - 210, RIGHT_PANEL_WIDTH - 60, 35)
    pygame.draw.rect(ventana, GRIS, btn_rect, border_radius=6)
    txt = font.render('ZONA DE ESTUDIO', True, (0, 0, 0))
    txt_rect = txt.get_rect(center=btn_rect.center)
    ventana.blit(txt, txt_rect)

    status_rect = pygame.Rect(LEFT_WIDTH + 15, y_stats + 100, RIGHT_PANEL_WIDTH - 30, 75)
    pygame.draw.rect(ventana, (0, 0, 0, 30), status_rect, border_radius=6)
    
    ventana.blit(font.render('Habilidades:', True, BLANCO), (status_rect.x + 8, status_rect.y + 6))
    
    y_offset = status_rect.y + 28
    if quiz_cooldown_until > time.time():
        rem = int(quiz_cooldown_until - time.time())
        cd_txt = font.render(f'Penaliz: {rem}s', True, BLANCO)
        ventana.blit(cd_txt, (status_rect.x + 8, y_offset))
        y_offset += 20
    
    if skill_success_cooldown_until > time.time():
        rem2 = int(skill_success_cooldown_until - time.time())
        cd_txt2 = font.render(f'Cooldown: {rem2}s', True, BLANCO)
        ventana.blit(cd_txt2, (status_rect.x + 8, y_offset))
        y_offset += 20
    
    try:
        usos_restantes = MAX_SKILL_USES_PER_LEVEL - skill_uses_this_level
    except NameError:
        usos_restantes = MAX_SKILL_USES_PER_LEVEL
    usos_txt = font.render(f'Usos: {skill_uses_this_level}/{MAX_SKILL_USES_PER_LEVEL}', True, BLANCO)
    ventana.blit(usos_txt, (status_rect.x + 8, y_offset))

    btn_magic = pygame.Rect(LEFT_WIDTH + 30, ALTO - 165, RIGHT_PANEL_WIDTH - 60, 35)
    pygame.draw.rect(ventana, GRIS, btn_magic, border_radius=6)
    txt = font.render('HABILIDADES MAGICAS', True, (0, 0, 0))
    txt_rect = txt.get_rect(center=btn_magic.center)
    ventana.blit(txt, txt_rect)

    export_btn = pygame.Rect(LEFT_WIDTH + 30, ALTO - 120, RIGHT_PANEL_WIDTH - 60, 35)
    pygame.draw.rect(ventana, (220, 220, 220), export_btn, border_radius=6)
    txt = font.render('EXPORTAR A EXCEL', True, (0, 0, 0))
    txt_rect = txt.get_rect(center=export_btn.center)
    ventana.blit(txt, txt_rect)

def goal_for_level():
    return int(goal_base * (2 ** (level - 1)))

def show_level_up(new_level):
    lines = [f'Nivel {new_level}!', f'Objetivo: {goal_base * (2 ** (new_level - 1))} pts']
    popup = {
        'lines': lines,
        'start': time.time(),
        'duration': 3.0,
        'x': ANCHO//2 - 150,
        'y': ALTO//2 - 40,
        'vy': -30.0,
        'color': (30, 120, 220),
        'icon': 'check'
    }
    floating_popups.append(popup)

def obtener_celda(pos):
    x, y = pos
    if x < 0 or x >= LEFT_WIDTH:
        return None
    fila = (y - MARGEN_SUPERIOR) // TAMANO_CELDA
    columna = (x - MARGEN_IZQUIERDO) // TAMANO_CELDA
    if 0 <= fila < FILAS and 0 <= columna < COLUMNAS:
        return (fila, columna)
    return None

def son_adyacentes(p1, p2):
    (r1, c1), (r2, c2) = p1, p2
    return abs(r1 - r2) + abs(c1 - c2) == 1

def intercambiar(p1, p2):
    global moves_count
    r1, c1 = p1
    r2, c2 = p2
    
    current_matrix = [[tablero[i][j] for j in range(COLUMNAS)] for i in range(FILAS)]
    matrix_history.append(current_matrix)
    game_events.append(f"Intercambio ({r1},{c1}) con ({r2},{c2})")
    
    has1 = p1 in skills_on_map
    has2 = p2 in skills_on_map
    if has1 or has2:
        v1 = skills_on_map.pop(p1) if has1 else None
        v2 = skills_on_map.pop(p2) if has2 else None
        if v1 is not None:
            skills_on_map[p2] = v1
        if v2 is not None:
            skills_on_map[p1] = v2
    
    tablero[r1][c1], tablero[r2][c2] = tablero[r2][c2], tablero[r1][c1]
    moves_count += 1

def find_matches():
    remove = set()
    for i in range(FILAS):
        run_color = tablero[i][0]
        run_start = 0
        for j in range(1, COLUMNAS + 1):
            color = tablero[i][j] if j < COLUMNAS else None
            if color == run_color:
                continue
            else:
                length = j - run_start
                if run_color is not None and length >= 3:
                    for k in range(run_start, j):
                        remove.add((i, k))
                if j < COLUMNAS:
                    run_color = tablero[i][j]
                    run_start = j

    for j in range(COLUMNAS):
        run_color = tablero[0][j]
        run_start = 0
        for i in range(1, FILAS + 1):
            color = tablero[i][j] if i < FILAS else None
            if color == run_color:
                continue
            else:
                length = i - run_start
                if run_color is not None and length >= 3:
                    for k in range(run_start, i):
                        remove.add((k, j))
                if i < FILAS:
                    run_color = tablero[i][j]
                    run_start = i

    return remove

def remove_and_collapse(matches):
    global score
    if not matches:
        return 0
    
    sound_manager.play_sound('explosion')
    removed = len(matches)
    score += removed * 10
    last_explosions.append((set(matches), time.time()))

    tablero_anim = [[tablero[i][j] for j in range(COLUMNAS)] for i in range(FILAS)]
    for (i, j) in matches:
        tablero[i][j] = None
        tablero_anim[i][j] = None

    tablero_final = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
    for j in range(COLUMNAS):
        stack = [tablero[i][j] for i in range(FILAS) if tablero[i][j] is not None]
        while len(stack) < FILAS:
            stack.insert(0, random.randrange(NUM_COLORS))
        for i in range(FILAS):
            tablero_final[i][j] = stack[i]

    start_time = time.time()
    duration = 0.5
    anim_clock = pygame.time.Clock()
    
    while time.time() - start_time < duration:
        progress = min(1.0, (time.time() - start_time) / duration)
        for j in range(COLUMNAS):
            col_stack = []
            for i in range(FILAS):
                if tablero_anim[i][j] is not None:
                    found = False
                    for k in range(i, FILAS):
                        if tablero_final[k][j] == tablero_anim[i][j]:
                            found = True
                            start_y = i
                            end_y = k
                            current_y = start_y + (end_y - start_y) * progress
                            col_stack.append((tablero_anim[i][j], current_y))
                            break
                    if not found and tablero_anim[i][j] is not None:
                        current_y = i + progress * 2
                        if current_y < FILAS:
                            col_stack.append((tablero_anim[i][j], current_y))
            
            for i in range(FILAS):
                if tablero_final[i][j] not in [x[0] for x in col_stack]:
                    current_y = -1 + (i + 1) * progress
                    if current_y >= 0:
                        col_stack.append((tablero_final[i][j], current_y))
            
            for i in range(FILAS):
                tablero_anim[i][j] = None
            for valor, y in col_stack:
                if 0 <= int(y) < FILAS:
                    tablero_anim[int(y)][j] = valor

        dibujar_interface()
        pygame.display.flip()
        anim_clock.tick(60)

    for i in range(FILAS):
        for j in range(COLUMNAS):
            tablero[i][j] = tablero_final[i][j]

    return removed

def spawn_skill_random(typ):
    if typ not in Habilidad.get_all_types():
        raise ValueError(f"Tipo inválido: {typ}")
        
    celdas_disponibles = [
        (r, c) for r in range(FILAS) for c in range(COLUMNAS)
        if (r, c) not in skills_on_map
    ]
    
    if not celdas_disponibles:
        return False
        
    r, c = random.choice(celdas_disponibles)
    orig = tablero[r][c]
    skills_on_map[(r, c)] = (typ, orig)
    tablero[r][c] = None
    return True

def activate_skill_at(pos):
    global score
    if pos not in skills_on_map:
        return
    val = skills_on_map.pop(pos)
    if isinstance(val, tuple):
        typ, orig = val
    else:
        typ = val
        orig = None
    r, c = pos
    affected = set()
    if typ == 'bomb':
        for i in range(r-1, r+2):
            for j in range(c-1, c+2):
                if 0 <= i < FILAS and 0 <= j < COLUMNAS:
                    affected.add((i, j))
    elif typ == 'rainbow':
        for i in range(FILAS):
            affected.add((i, c))
        for j in range(COLUMNAS):
            affected.add((r, j))
    elif typ == 'star':
        color = orig if orig is not None else tablero[r][c]
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if tablero[i][j] == color:
                    affected.add((i, j))

    remove_and_collapse(affected)

def handle_quiz():
    global quiz_cooldown_until, skill_success_cooldown_until, skill_uses_this_level
    
    available = [i for i in range(len(questions)) if i not in asked_questions]
    if not available:
        asked_questions.clear()
        available = list(range(len(questions)))
    
    q_idx = random.choice(available)
    asked_questions.add(q_idx)
    pregunta, respuesta = questions[q_idx]
    
    pick = random.random()
    if pick < 0.5:
        lines = []
        palabras = pregunta.split()
        cur = palabras[0] if palabras else ''
        for w in palabras[1:]:
            if len(cur + ' ' + w) <= 35:
                cur += ' ' + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        opts = ['Verdadero', 'Falso']
        correct_idx = 0 if respuesta else 1
        q_struct = {'lines': lines, 'options': opts, 'correct_idx': correct_idx}
    elif pick < 0.8:
        q_struct = generate_matrix_mcq()
    else:
        q = 'Que es la traza?'
        opts = ['Suma autovalores', 'Producto autovalores', 'Num filas']
        correct_idx = 0
        lines = [q]
        q_struct = {'lines': lines, 'options': opts, 'correct_idx': correct_idx}

    asking = True
    clock = pygame.time.Clock()
    
    while asking:
        y_start = 350
        modal = pygame.Rect(LEFT_WIDTH + 15, y_start, RIGHT_PANEL_WIDTH - 30, 140)
        options_base_x = modal.x + 8
        options_base_y = modal.y + 55
        w_btn = modal.width - 16
        h_btn = 32
        gap = 6

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btns = []
                for k in range(len(q_struct['options'])):
                    rect = pygame.Rect(options_base_x, options_base_y + k*(h_btn+gap), w_btn, h_btn)
                    btns.append(rect)
                for idx, rect in enumerate(btns):
                    if rect.collidepoint(mx, my):
                        if idx == q_struct['correct_idx']:
                            spawn_skill_random(random.choice(['bomb','rainbow','star']))
                            skill_uses_this_level += 1
                            skill_success_cooldown_until = time.time() + 10
                        else:
                            quiz_cooldown_until = time.time() + 20
                        asking = False

        dibujar_interface()
        pygame.draw.rect(ventana, (245,245,245), modal, border_radius=8)
        pygame.draw.rect(ventana, (200,200,200), modal, 2, border_radius=8)
        
        y_offset = 10
        for linea in q_struct['lines']:
            qsurf = font.render(linea, True, (0,0,0))
            ventana.blit(qsurf, (modal.x + 10, modal.y + y_offset))
            y_offset += 22

        for k, opt in enumerate(q_struct['options']):
            rect = pygame.Rect(options_base_x, options_base_y + k*(h_btn+gap), w_btn, h_btn)
            pygame.draw.rect(ventana, (220,220,220), rect, border_radius=5)
            txt_surf = font.render(opt, True, (0,0,0))
            txt_rect = txt_surf.get_rect(center=rect.center)
            ventana.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(30)

def sum_matrix():
    s = 0
    for i in range(FILAS):
        for j in range(COLUMNAS):
            v = tablero[i][j]
            if isinstance(v, int) and v >= 0:
                s += v
    return s

def matrix_stats():
    vals = []
    for i in range(FILAS):
        for j in range(COLUMNAS):
            v = tablero[i][j]
            if isinstance(v, int) and v >= 0:
                vals.append(v)
    if not vals:
        return {'sum':0, 'min':0, 'max':0, 'mean':0}
    return {'sum': sum(vals), 'min': min(vals), 'max': max(vals), 'mean': sum(vals)/len(vals)}

def show_end_screen(victory=False):
    total_time = int(time.time() - game_start_time)
    stats = matrix_stats()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                export_btn = pygame.Rect(rx + w//2 - 110, ry + h - 110, 220, 40)
                if export_btn.collidepoint(mx, my):
                    if EXCEL_AVAILABLE:
                        filename = export_to_excel()
                        truncated = truncate_filename(filename, 45)
                        popup = {
                            'lines': ['Datos exportados!', truncated],
                            'start': time.time(),
                            'duration': 3.5,
                            'x': ANCHO//2 - 200,
                            'y': ALTO//2 - 100,
                            'vy': -25.0,
                            'color': (30, 180, 30),
                            'icon': 'check'
                        }
                        floating_popups.append(popup)
                else:
                    return
            if ev.type == pygame.KEYDOWN:
                return

        ventana.fill((30,30,30))

        w = 520
        h = 430
        rx = (ANCHO - w)//2
        ry = (ALTO - h)//2
        rect = pygame.Rect(rx, ry, w, h)
        pygame.draw.rect(ventana, (235, 245, 255), rect, border_radius=12)

        if victory:
            title = large_font.render('¡Felicidades!', True, (10,90,30))
        else:
            title = large_font.render('Game Over', True, (150,10,10))
        ventana.blit(title, (rect.x + 20, rect.y + 16))

        lines = [
            f'Nivel alcanzado: {level}',
            f'Puntos totales: {score}',
            f'Movimientos totales: {moves_count}',
            f'Tiempo total: {total_time}s',
            f'Suma matriz: {stats["sum"]}',
            f'Media matriz: {stats["mean"]:.2f}',
            f'Min: {stats["min"]}  Max: {stats["max"]}'
        ]
        for i, l in enumerate(lines):
            ventana.blit(font.render(l, True, (20,20,20)), (rect.x + 20, rect.y + 70 + i*28))

        export_btn = pygame.Rect(rx + w//2 - 110, ry + h - 110, 220, 40)
        pygame.draw.rect(ventana, (220, 220, 220), export_btn, border_radius=6)
        export_text = font.render('EXPORTAR A EXCEL', True, (0, 0, 0))
        text_rect = export_text.get_rect(center=export_btn.center)
        ventana.blit(export_text, text_rect)

        hint = font.render('Click o tecla para cerrar', True, (80,80,80))
        ventana.blit(hint, (rect.x + 20, rect.y + h - 35))

        dibujar_interface()
        pygame.display.flip()
        clock.tick(30)


score = 0
level = 1
moves_count = 0
seleccionado = None
tablero = [[random.randrange(NUM_COLORS) for _ in range(COLUMNAS)] for _ in range(FILAS)]
matrix_history = []
game_events = []

show_start_menu()

clock = pygame.time.Clock()
running = True
while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos = obtener_celda(pygame.mouse.get_pos())
            mx, my = pygame.mouse.get_pos()
            
            btn_learn = pygame.Rect(LEFT_WIDTH + 30, ALTO - 210, RIGHT_PANEL_WIDTH - 60, 35)
            btn_rect = pygame.Rect(LEFT_WIDTH + 30, ALTO - 165, RIGHT_PANEL_WIDTH - 60, 35)
            export_btn = pygame.Rect(LEFT_WIDTH + 30, ALTO - 120, RIGHT_PANEL_WIDTH - 60, 35)
            
            if btn_learn.collidepoint(mx, my):
                show_learn_screen()
            elif btn_rect.collidepoint(mx, my):
                now = time.time()
                if now < quiz_cooldown_until:
                    rem = int(quiz_cooldown_until - now)
                    popup = {
                        'lines': [f'Penalizacion: {rem}s'],
                        'start': time.time(),
                        'duration': 2.0,
                        'x': ANCHO//2 - 120,
                        'y': ALTO//2 - 40,
                        'vy': -20.0,
                        'color': (180, 60, 60)
                    }
                    floating_popups.append(popup)
                elif skill_uses_this_level >= MAX_SKILL_USES_PER_LEVEL:
                    popup = {
                        'lines': [f'Max habilidades: {MAX_SKILL_USES_PER_LEVEL}'],
                        'start': time.time(),
                        'duration': 2.0,
                        'x': ANCHO//2 - 120,
                        'y': ALTO//2 - 40,
                        'vy': -20.0,
                        'color': (200, 140, 40)
                    }
                    floating_popups.append(popup)
                elif now < skill_success_cooldown_until:
                    rem = int(skill_success_cooldown_until - now)
                    popup = {
                        'lines': [f'Cooldown: {rem}s'],
                        'start': time.time(),
                        'duration': 2.0,
                        'x': ANCHO//2 - 120,
                        'y': ALTO//2 - 40,
                        'vy': -20.0,
                        'color': (100, 120, 200)
                    }
                    floating_popups.append(popup)
                else:
                    handle_quiz()
            elif export_btn.collidepoint(mx, my):
                if EXCEL_AVAILABLE:
                    filename = export_to_excel()
                    truncated = truncate_filename(filename, 45)
                    popup = {
                        'lines': ['Datos exportados!', truncated],
                        'start': time.time(),
                        'duration': 3.5,
                        'x': ANCHO//2 - 180,
                        'y': ALTO//2 - 40,
                        'vy': -30.0,
                        'color': (30, 180, 30),
                        'icon': 'check'
                    }
                    floating_popups.append(popup)
            else:
                if pos:
                    if not seleccionado:
                        seleccionado = pos
                    else:
                        if son_adyacentes(seleccionado, pos):
                            intercambiar(seleccionado, pos)
                            if pos in skills_on_map:
                                activate_skill_at(pos)
                            total_removed = 0
                            while True:
                                matches = find_matches()
                                if not matches:
                                    break
                                removed = remove_and_collapse(matches)
                                total_removed += removed
                            seleccionado = None
                        else:
                            seleccionado = pos
        elif evento.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            hover_cell = obtener_celda((mx, my))

    if score >= goal_for_level():
        if level >= MAX_LEVEL:
            if EXCEL_AVAILABLE:
                filename = export_to_excel()
                truncated = truncate_filename(filename, 45)
                popup = {
                    'lines': ['Victoria exportada!', truncated],
                    'start': time.time(),
                    'duration': 3.0,
                    'x': ANCHO//2 - 180,
                    'y': ALTO//2 - 100,
                    'vy': -20.0,
                    'color': (30, 180, 30),
                    'icon': 'check'
                }
                floating_popups.append(popup)
                pygame.time.wait(1500)
            show_end_screen(victory=True)
            running = False
            break
        else:
            show_level_up(level + 1)
            level += 1
            try:
                skill_uses_this_level = 0
                skill_success_cooldown_until = 0
                quiz_cooldown_until = 0
            except NameError:
                pass
            level_start_time = time.time()

    elapsed = time.time() - level_start_time
    if elapsed >= LEVEL_TIME:
        if score >= goal_for_level():
            if level >= MAX_LEVEL:
                ventana.fill(BLANCO)
                msg = large_font.render('Completaste el nivel final!', True, (0,0,0))
                ventana.blit(msg, (50, ALTO//2 - 20))
                pygame.display.flip()
                pygame.time.delay(3000)
                running = False
            else:
                level += 1
                try:
                    skill_uses_this_level = 0
                    skill_success_cooldown_until = 0
                    quiz_cooldown_until = 0
                except NameError:
                    pass
                level_start_time = time.time()
        else:
            if EXCEL_AVAILABLE:
                filename = export_to_excel()
                truncated = truncate_filename(filename, 45)
                popup = {
                    'lines': ['Partida guardada!', truncated],
                    'start': time.time(),
                    'duration': 3.0,
                    'x': ANCHO//2 - 180,
                    'y': ALTO//2 - 100,
                    'vy': -20.0,
                    'color': (30, 180, 30),
                    'icon': 'check'
                }
                floating_popups.append(popup)
                pygame.time.wait(1500)
            show_end_screen(victory=False)
            running = False

    dibujar_interface()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()