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

# Configuración de la ventana
ANCHO = 1200
ALTO = 800
TAMANO_CELDA = 64
FILAS = 8
COLUMNAS = 8
RIGHT_PANEL_WIDTH = 360
LEFT_WIDTH = ANCHO - RIGHT_PANEL_WIDTH

# Márgenes para centrar la cuadrícula en el panel blanco
MARGEN_SUPERIOR = (ALTO - (FILAS * TAMANO_CELDA)) // 2
MARGEN_IZQUIERDO = (LEFT_WIDTH - (COLUMNAS * TAMANO_CELDA)) // 2

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (10, 90, 180)  # Fondo derecho (Uniminuto azul aproximado)
GRIS = (230, 230, 230)

# Configurar la ventana
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Candy Matrix - Proyecto Algebra Lineal')

# Sonidos (asegúrate que existan en la carpeta sounds)
SONIDO_EXPLOSION = os.path.join('sounds', 'bubble-pop-06-351337.mp3')
MUSICA_FONDO = os.path.join('sounds', 'background_music.mp3')
if os.path.exists(MUSICA_FONDO):
    try:
        mixer.music.load(MUSICA_FONDO)
        mixer.music.set_volume(0.5)
        mixer.music.play(-1)
    except Exception as e:
        print('No se pudo reproducir la música:', e)

sonido_explosion = None
if os.path.exists(SONIDO_EXPLOSION):
    try:
        sonido_explosion = mixer.Sound(SONIDO_EXPLOSION)
    except Exception as e:
        print('No se pudo cargar sonido explosion:', e)

# Colores de caramelos (mapear a números en la matriz)
COLOR_MAP = [
    (220, 20, 60),   # 0 Rojo
    (34, 139, 34),   # 1 Verde
    (30, 144, 255),  # 2 Azul
    (255, 215, 0),   # 3 Amarillo
    (199, 21, 133),  # 4 Magenta
    (0, 206, 209)    # 5 Cian
]
NUM_COLORS = len(COLOR_MAP)

# Estado del juego
tablero = [[random.randrange(NUM_COLORS) for _ in range(COLUMNAS)] for _ in range(FILAS)]
seleccionado = None
moves_count = 0
score = 0
level = 1

# Historial de matrices y eventos
matrix_history = []
game_events = []

def export_to_excel():
    if not EXCEL_AVAILABLE:
        print("Necesitas instalar openpyxl para exportar a Excel")
        return

    # Crear nuevo libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumen del Juego"
    
    # Estilos
    title_font = Font(bold=True, size=12)
    header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    
    # Información general
    ws['A1'] = "CANDY MATRIX - RESUMEN DEL JUEGO"
    ws['A1'].font = Font(bold=True, size=14)
    ws.merge_cells('A1:E1')
    
    # Estadísticas generales
    ws['A3'] = "Fecha:"
    ws['B3'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws['A4'] = "Nivel alcanzado:"
    ws['B4'] = level
    ws['A5'] = "Puntuación final:"
    ws['B5'] = score
    ws['A6'] = "Movimientos totales:"
    ws['B6'] = moves_count
    
    # Estadísticas de matriz actual
    stats = matrix_stats()
    ws['A8'] = "ESTADÍSTICAS DE MATRIZ FINAL"
    ws['A8'].font = title_font
    ws['A9'] = "Suma total:"
    ws['B9'] = stats['sum']
    ws['A10'] = "Promedio:"
    ws['B10'] = stats['mean']
    ws['A11'] = "Mínimo:"
    ws['B11'] = stats['min']
    ws['A12'] = "Máximo:"
    ws['B12'] = stats['max']
    
    # Historial de matrices
    ws['A14'] = "HISTORIAL DE MATRICES"
    ws['A14'].font = title_font
    row = 15
    for idx, (matrix, event) in enumerate(zip(matrix_history, game_events), 1):
        ws.cell(row=row, column=1, value=f"Movimiento {idx}")
        ws.cell(row=row, column=2, value=event)
        row += 1
        
        # Matriz como tabla
        for i, matrix_row in enumerate(matrix):
            for j, val in enumerate(matrix_row):
                cell = ws.cell(row=row+i, column=j+1, value=val if val is not None else "-")
        row += len(matrix) + 2
    
    # Ajustar ancho de columnas
    from openpyxl.utils import get_column_letter
    for i in range(1, ws.max_column + 1):
        max_length = 0
        column = get_column_letter(i)
        for cell in ws[column]:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width
    
    # Guardar archivo
    filename = f"candy_matrix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    return filename
MAX_LEVEL = 5
LEVEL_TIME = 180  # 3 minutos
level_start_time = time.time()
goal_base = 500

# Tiempos globales
game_start_time = time.time()

# Animaciones sencillas: registrar últimas explosiones [(pos_list, start_time)]
last_explosions = []
# Hover
hover_cell = None

# Habilidades en el mapa: dict (fila,col) -> tipo ('bomb','rainbow','star')
skills_on_map = {}
skill_icons = {}

# Preguntas True/False sobre álgebra lineal
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
quiz_success_cooldown = 0  # cooldown después de respuesta correcta
asked_questions = set()

# Popups flotantes no bloqueantes (nivel up)
floating_popups = []

font = pygame.font.SysFont('arial', 20)
large_font = pygame.font.SysFont('arial', 30)

def dibujar_interface():
    # Panel izquierdo: fondo tipo canasta de dulces (tono más claro)
    ventana.fill((245, 230, 235))
    # Dibujar panel principal (canasta)
    panel_rect = pygame.Rect(10, 10, LEFT_WIDTH-20, ALTO-20)
    # Fondo de madera claro (menos saturado)
    pygame.draw.rect(ventana, (195, 155, 110), panel_rect, border_radius=20)
    # Tejido de la canasta (patrón entrecruzado)
    stripe_color1 = (160, 82, 45)
    stripe_color2 = (205, 133, 63)
    spacing = 15
    # Líneas verticales
    for x in range(panel_rect.x, panel_rect.x + panel_rect.width, spacing):
        pygame.draw.line(ventana, stripe_color1, (x, panel_rect.y), (x, panel_rect.y + panel_rect.height), 2)
    # Líneas horizontales entrelazadas
    for y in range(panel_rect.y, panel_rect.y + panel_rect.height, spacing*2):
        for x in range(panel_rect.x, panel_rect.x + panel_rect.width - spacing, spacing*2):
            pygame.draw.rect(ventana, stripe_color2, (x, y, spacing, spacing))
    # Borde superior reforzado
    pygame.draw.rect(ventana, stripe_color2, (panel_rect.x, panel_rect.y, panel_rect.width, spacing*2), border_radius=20)

    # Panel derecho (azul)
    pygame.draw.rect(ventana, AZUL, (LEFT_WIDTH, 0, RIGHT_PANEL_WIDTH, ALTO))

    # Dibujar caramelos (círculos) en la cuadrícula centrada
    for i in range(FILAS):
        for j in range(COLUMNAS):
            # Coordenadas centrales de la celda
            x = MARGEN_IZQUIERDO + j * TAMANO_CELDA + TAMANO_CELDA // 2
            y = MARGEN_SUPERIOR + i * TAMANO_CELDA + TAMANO_CELDA // 2
            radius = TAMANO_CELDA // 2 - 8

            # Dibujar fondo de celda (sutil)
            cell_bg = pygame.Surface((TAMANO_CELDA-8, TAMANO_CELDA-8), pygame.SRCALPHA)
            pygame.draw.rect(cell_bg, (0,0,0,30), (0,0,TAMANO_CELDA-8,TAMANO_CELDA-8), border_radius=8)
            ventana.blit(cell_bg, (x - (TAMANO_CELDA-8)//2, y - (TAMANO_CELDA-8)//2))

            # Dibujar caramelo si existe
            if tablero[i][j] is not None:
                color = COLOR_MAP[tablero[i][j]]
                # Sombras y borde para aspecto dulce
                pygame.draw.circle(ventana, (80, 50, 60), (x+2, y+4), radius+2)
                pygame.draw.circle(ventana, (230, 230, 230), (x, y), radius+1)
                pygame.draw.circle(ventana, color, (x, y), radius)
                # Brillo superior izquierdo
                shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.ellipse(shine, (255,255,255,90), (int(radius*0.1), int(radius*0.05), int(radius*0.9), int(radius*0.6)))
                ventana.blit(shine, (x - radius, y - radius))

            # Dibujar habilidades como caramelos especiales (si hay)
            if (i, j) in skills_on_map:
                val = skills_on_map[(i, j)]
                if isinstance(val, tuple):
                    typ, orig_color = val
                else:
                    typ = val
                    orig_color = None
                if typ == 'bomb':
                    # Caramelo bomba (negro con detalles rojos)
                    pygame.draw.circle(ventana, (40, 40, 40), (x, y), radius)
                    # Detalles de la mecha
                    pygame.draw.line(ventana, (255, 50, 50), (x, y-radius+2), (x+4, y-radius-6), 3)
                    pygame.draw.circle(ventana, (255, 200, 50), (x+4, y-radius-6), 3)
                    # Brillo
                    shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shine, (255,255,255,40), (radius*0.5, radius*0.5, radius, radius))
                    ventana.blit(shine, (x - radius, y - radius))
                elif typ == 'rainbow':
                    # Caramelo arcoíris (efecto giratorio)
                    t = time.time() * 2
                    for angle in range(0, 360, 30):
                        rad = math.radians(angle + t * 30)
                        color = pygame.Color(0)
                        color.hsva = (angle % 360, 100, 100, 100)
                        start = (x + math.cos(rad)*radius*0.5, y + math.sin(rad)*radius*0.5)
                        end = (x + math.cos(rad)*radius*0.9, y + math.sin(rad)*radius*0.9)
                        pygame.draw.line(ventana, color, start, end, 3)
                    # Centro blanco
                    pygame.draw.circle(ventana, (255,255,255), (x, y), int(radius*0.4))
                elif typ == 'star':
                    # Caramelo estrella (dorado brillante)
                    pygame.draw.circle(ventana, (255, 215, 0), (x, y), radius)
                    # Destellos de estrella
                    t = time.time() * 3
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle + t * 30)
                        length = radius * (0.5 + math.sin(t*2 + angle*0.1) * 0.2)
                        end_x = x + math.cos(rad) * length
                        end_y = y + math.sin(rad) * length
                        pygame.draw.line(ventana, (255, 255, 200), (x, y), (end_x, end_y), 2)
                    # Brillo central
                    shine = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shine, (255,255,255,128), (radius*0.6, radius*0.6, radius*0.8, radius*0.8))
                    ventana.blit(shine, (x - radius, y - radius))

    # Resaltar seleccionado
    if seleccionado:
        i, j = seleccionado
        x = MARGEN_IZQUIERDO + j * TAMANO_CELDA
        y = MARGEN_SUPERIOR + i * TAMANO_CELDA
        pygame.draw.rect(ventana, BLANCO, (x-3, y-3, TAMANO_CELDA+6, TAMANO_CELDA+6), 3, border_radius=10)

    # Resaltar hover
    if hover_cell:
        hi, hj = hover_cell
        if 0 <= hi < FILAS and 0 <= hj < COLUMNAS:
            hx = MARGEN_IZQUIERDO + hj * TAMANO_CELDA
            hy = MARGEN_SUPERIOR + hi * TAMANO_CELDA
            s = pygame.Surface((TAMANO_CELDA-4, TAMANO_CELDA-4), pygame.SRCALPHA)
            s.fill((255,255,255,30))
            ventana.blit(s, (hx, hy))

    # Dibujar animaciones de explosión recientes
    now = time.time()
    new_expl = []
    for cells, t0 in last_explosions:
        age = now - t0
        if age > 0.6:
            continue
        new_expl.append((cells, t0))
        # animación simple: círculo con alpha que crece
        for (i, j) in cells:
            cx = MARGEN_IZQUIERDO + j * TAMANO_CELDA + TAMANO_CELDA//2 - 2
            cy = MARGEN_SUPERIOR + i * TAMANO_CELDA + TAMANO_CELDA//2 - 2
            radius = int(6 + age * 30)
            alpha = int(200 * (1 - age/0.6))
            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255,255,255,alpha), (radius, radius), radius)
            ventana.blit(surf, (cx - radius + 2, cy - radius + 2))
    # mantener solo las no expiradas
    last_explosions[:] = new_expl

    # Panel derecho: mostrar matriz numérica y estadísitcas
    draw_right_panel()

    # Dibujar popups flotantes (no bloqueantes)
    now = time.time()
    to_remove = []
    for idx, p in enumerate(floating_popups):
        age = now - p['start']
        if age > p['duration']:
            to_remove.append(idx)
            continue
        # calcular posición en y (subiendo)
        y = p['y'] + p['vy'] * age
        w = 360
        h = 60
        rect = pygame.Rect(p['x'], int(y), w, h)
        # fondo azul
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((*p['color'], 220))
        ventana.blit(s, rect.topleft)
        # texto
        for i, line in enumerate(p['lines']):
            txt = font.render(line, True, (255,255,255))
            ventana.blit(txt, (rect.x + 12, rect.y + 8 + i*22))
    # limpiar expirados (desde el final para no desordenar índices)
    for i in reversed(to_remove):
        floating_popups.pop(i)

def draw_right_panel():
    # Fondo azul ya dibujado
    padding = 20
    x0 = LEFT_WIDTH + padding
    y0 = padding

    # Título
    title = large_font.render(f'Nivel {level}', True, BLANCO)
    ventana.blit(title, (x0, y0))

    # Mostrar matriz (números)
    y_matrix = y0 + 50
    cell_h = 24
    for i in range(FILAS):
        row_text = ' '.join(str(tablero[i][j]) for j in range(COLUMNAS))
        surf = font.render(row_text, True, BLANCO)
        ventana.blit(surf, (x0, y_matrix + i * (cell_h+2)))

    # Estadísticas
    y_stats = y_matrix + FILAS * (cell_h+2) + 20
    stats = [
        f'Puntos: {score}',
        f'Movimientos: {moves_count}',
        f'Tiempo restante: {max(0, int(LEVEL_TIME - (time.time() - level_start_time)))}s',
        f'Objetivo: {goal_for_level()}'
    ]
    for i, s in enumerate(stats):
        ventana.blit(font.render(s, True, BLANCO), (x0, y_stats + i * 26))

    # Botón HABILIDADES MAGICAS
    btn_rect = pygame.Rect(LEFT_WIDTH + 40, ALTO - 140, RIGHT_PANEL_WIDTH - 80, 40)
    pygame.draw.rect(ventana, GRIS, btn_rect, border_radius=6)
    txt = font.render('HABILIDADES MAGICAS', True, (0, 0, 0))
    ventana.blit(txt, (btn_rect.x + 12, btn_rect.y + 8))

    # Contador de cooldown si aplica
    if quiz_cooldown_until > time.time():
        rem = int(quiz_cooldown_until - time.time())
        cd_txt = font.render(f'Cooldown: {rem}s', True, BLANCO)
        ventana.blit(cd_txt, (btn_rect.x, btn_rect.y - 28))
        
    # Botón EXPORTAR DATOS
    export_btn = pygame.Rect(LEFT_WIDTH + 40, ALTO - 80, RIGHT_PANEL_WIDTH - 80, 40)
    pygame.draw.rect(ventana, (220, 220, 220), export_btn, border_radius=6)
    txt = font.render('EXPORTAR A EXCEL', True, (0, 0, 0))
    ventana.blit(txt, (export_btn.x + 12, export_btn.y + 8))

def goal_for_level():
    # Objetivo que se duplica cada nivel (progresión exponencial 2^n)
    return int(goal_base * (2 ** (level - 1)))


def show_level_up(new_level):
    # Antes: modal bloqueante. Ahora crear popup flotante no bloqueante.
    lines = [f'¡Felicidades! Subiste al nivel {new_level}', f'Nuevo objetivo: {goal_base * (2 ** (new_level - 1))} pts']
    popup = {
        'lines': lines,
        'start': time.time(),
        'duration': 3.0,
        'x': ANCHO//2 - 180,
        'y': ALTO//2 - 40,
        'vy': -30.0,  # velocidad hacia arriba (pixeles por segundo)
        'color': (30, 120, 220)
    }
    floating_popups.append(popup)
    return

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
    
    # Guardar estado actual en historial
    current_matrix = [[tablero[i][j] for j in range(COLUMNAS)] for i in range(FILAS)]
    matrix_history.append(current_matrix)
    game_events.append(f"Intercambio ({r1},{c1}) con ({r2},{c2})")
    # intercambiar habilidades si existen (permitir mover la habilidad con el caramelo)
    has1 = p1 in skills_on_map
    has2 = p2 in skills_on_map
    if has1 or has2:
        v1 = skills_on_map.pop(p1) if has1 else None
        v2 = skills_on_map.pop(p2) if has2 else None
        if v1 is not None:
            skills_on_map[p2] = v1
        if v2 is not None:
            skills_on_map[p1] = v2
    # intercambiar colores del tablero
    tablero[r1][c1], tablero[r2][c2] = tablero[r2][c2], tablero[r1][c1]
    moves_count += 1

def find_matches():
    remove = set()
    # Horizontal
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

    # Vertical
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
    # Reproducir sonido
    if sonido_explosion:
        sonido_explosion.play()

    removed = len(matches)
    score += removed * 10

    # Guardar para animación breve
    last_explosions.append((set(matches), time.time()))

    # Crear una copia del tablero para la animación
    tablero_anim = [[tablero[i][j] for j in range(COLUMNAS)] for i in range(FILAS)]
    # Eliminar marcando con None
    for (i, j) in matches:
        tablero[i][j] = None
        tablero_anim[i][j] = None

    # Calcular posiciones finales después del colapso
    tablero_final = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
    for j in range(COLUMNAS):
        stack = [tablero[i][j] for i in range(FILAS) if tablero[i][j] is not None]
        # Rellenar arriba con nuevos
        while len(stack) < FILAS:
            stack.insert(0, random.randrange(NUM_COLORS))
        # Asignar a posiciones finales
        for i in range(FILAS):
            tablero_final[i][j] = stack[i]

    # Animación suave de caída
    start_time = time.time()
    duration = 0.5  # medio segundo de animación
    anim_clock = pygame.time.Clock()
    
    while time.time() - start_time < duration:
        progress = min(1.0, (time.time() - start_time) / duration)
        # Interpolar posiciones
        for j in range(COLUMNAS):
            col_stack = []
            # Encontrar caramelos existentes y sus destinos
            for i in range(FILAS):
                if tablero_anim[i][j] is not None:
                    # Buscar su posición final
                    found = False
                    for k in range(i, FILAS):
                        if tablero_final[k][j] == tablero_anim[i][j]:
                            found = True
                            # Interpolar posición
                            start_y = i
                            end_y = k
                            current_y = start_y + (end_y - start_y) * progress
                            col_stack.append((tablero_anim[i][j], current_y))
                            break
                    if not found and tablero_anim[i][j] is not None:
                        # El caramelo desaparece, moverlo hacia abajo
                        current_y = i + progress * 2
                        if current_y < FILAS:
                            col_stack.append((tablero_anim[i][j], current_y))
            
            # Dibujar nuevos caramelos cayendo desde arriba
            for i in range(FILAS):
                if tablero_final[i][j] not in [x[0] for x in col_stack]:
                    current_y = -1 + (i + 1) * progress
                    if current_y >= 0:
                        col_stack.append((tablero_final[i][j], current_y))
            
            # Actualizar tablero_anim para esta columna
            for i in range(FILAS):
                tablero_anim[i][j] = None
            for valor, y in col_stack:
                if 0 <= int(y) < FILAS:
                    tablero_anim[int(y)][j] = valor

        # Dibujar frame
        dibujar_interface()
        pygame.display.flip()
        anim_clock.tick(60)

    # Actualizar tablero final
    for i in range(FILAS):
        for j in range(COLUMNAS):
            tablero[i][j] = tablero_final[i][j]

    return removed

def spawn_skill_random(typ):
    # Escoger celda aleatoria
    attempts = 0
    while attempts < 100:
        r = random.randrange(FILAS)
        c = random.randrange(COLUMNAS)
        if (r, c) not in skills_on_map:
            # Guardar el color original antes de reemplazar y reemplazar con None
            orig = tablero[r][c]
            skills_on_map[(r, c)] = (typ, orig)
            tablero[r][c] = None
            return True
        attempts += 1
    return False

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
        # Usar el color original guardado cuando la habilidad fue colocada
        color = orig if orig is not None else tablero[r][c]
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if tablero[i][j] == color:
                    affected.add((i, j))

    remove_and_collapse(affected)

def handle_quiz():
    global quiz_cooldown_until, quiz_success_cooldown
    # Simple modal de preguntas: pregunta aleatoria entre la lista
    # Elegir pregunta sin repetir hasta agotar
    available = [i for i in range(len(questions)) if i not in asked_questions]
    if not available:
        asked_questions.clear()
        available = list(range(len(questions)))
    q_idx = random.choice(available)
    asked_questions.add(q_idx)
    pregunta, respuesta = questions[q_idx]
    
    # Dividir pregunta en líneas si es muy larga
    palabras = pregunta.split()
    lineas = []
    linea_actual = palabras[0]
    for palabra in palabras[1:]:
        if len(linea_actual + " " + palabra) <= 40:  # máximo ~40 caracteres por línea
            linea_actual += " " + palabra
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    lineas.append(linea_actual)
    
    asking = True
    clock = pygame.time.Clock()
    while asking:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Botones true/false
                btn_true = pygame.Rect(LEFT_WIDTH + 60, ALTO - 100, 120, 36)
                btn_false = pygame.Rect(LEFT_WIDTH + 200, ALTO - 100, 120, 36)
                if btn_true.collidepoint(mx, my):
                    if respuesta is True:
                        # éxito: spawnear una habilidad aleatoria y establecer cooldown de 10s
                        spawn_skill_random(random.choice(['bomb','rainbow','star']))
                        quiz_success_cooldown = time.time() + 10
                    else:
                        quiz_cooldown_until = time.time() + 20
                    asking = False
                if btn_false.collidepoint(mx, my):
                    if respuesta is False:
                        spawn_skill_random(random.choice(['bomb','rainbow','star']))
                        quiz_success_cooldown = time.time() + 10
                    else:
                        quiz_cooldown_until = time.time() + 20
                    asking = False

        # Dibujar modal sobre la pantalla
        dibujar_interface()
        # Rect fondo modal (más alto para acomodar preguntas largas)
        modal = pygame.Rect(LEFT_WIDTH + 20, ALTO - 220, RIGHT_PANEL_WIDTH - 40, 150)
        pygame.draw.rect(ventana, (245,245,245), modal, border_radius=8)
        pygame.draw.rect(ventana, (200,200,200), modal, 2, border_radius=8)
        
        # Renderizar pregunta en múltiples líneas si es necesario
        y_offset = 10
        for linea in lineas:
            qsurf = font.render(linea, True, (0,0,0))
            ventana.blit(qsurf, (modal.x + 10, modal.y + y_offset))
            y_offset += 25  # espaciado entre líneas

        btn_true = pygame.Rect(LEFT_WIDTH + 60, ALTO - 100, 120, 36)
        btn_false = pygame.Rect(LEFT_WIDTH + 200, ALTO - 100, 120, 36)
        pygame.draw.rect(ventana, (100, 200, 100), btn_true, border_radius=6)
        pygame.draw.rect(ventana, (200, 100, 100), btn_false, border_radius=6)
        ventana.blit(font.render('Verdadero', True, (0,0,0)), (btn_true.x+10, btn_true.y+8))
        ventana.blit(font.render('Falso', True, (0,0,0)), (btn_false.x+40, btn_false.y+8))

        pygame.display.flip()
        clock.tick(30)

def sum_matrix():
    s = 0
    for i in range(FILAS):
        for j in range(COLUMNAS):
            # tablero puede contener None o -1 para habilidades; ignorar
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
    # Mostrar ventana final compacta con estadísticas detalladas
    total_time = int(time.time() - game_start_time)
    stats = matrix_stats()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                return

        # Fondo tenue
        ventana.fill((30,30,30))

        # Dibujar ventana central pequeña
        w = 520
        h = 360
        rx = (ANCHO - w)//2
        ry = (ALTO - h)//2
        rect = pygame.Rect(rx, ry, w, h)
        pygame.draw.rect(ventana, (235, 245, 255), rect, border_radius=12)

        # Título
        if victory:
            title = large_font.render('¡Felicidades! Juego completado', True, (10,90,30))
        else:
            title = large_font.render('Game Over', True, (150,10,10))
        ventana.blit(title, (rect.x + 20, rect.y + 16))

        # Estadísticas
        lines = [
            f'Nivel alcanzado: {level}',
            f'Puntos totales: {score}',
            f'Movimientos totales: {moves_count}',
            f'Tiempo total (s): {total_time}',
            f'Suma matriz: {stats["sum"]}',
            f'Media matriz: {stats["mean"]:.2f}',
            f'Mín matriz: {stats["min"]}  Máx matriz: {stats["max"]}'
        ]
        for i, l in enumerate(lines):
            ventana.blit(font.render(l, True, (20,20,20)), (rect.x + 24, rect.y + 80 + i*32))

        hint = font.render('Haz click o presiona cualquier tecla para cerrar', True, (80,80,80))
        ventana.blit(hint, (rect.x + 24, rect.y + h - 40))

        pygame.display.flip()
        clock.tick(30)


# Bucle principal
clock = pygame.time.Clock()
running = True
while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos = obtener_celda(pygame.mouse.get_pos())
            mx, my = pygame.mouse.get_pos()
            # Verificar botón preguntas
            btn_rect = pygame.Rect(LEFT_WIDTH + 40, ALTO - 140, RIGHT_PANEL_WIDTH - 80, 40)
            export_btn = pygame.Rect(LEFT_WIDTH + 40, ALTO - 80, RIGHT_PANEL_WIDTH - 80, 40)
            
            if btn_rect.collidepoint(mx, my):
                if time.time() >= quiz_cooldown_until:
                    handle_quiz()
                else:
                    # cooldown activo: mostrar mensaje breve
                    pass
            elif export_btn.collidepoint(mx, my):
                if EXCEL_AVAILABLE:
                    filename = export_to_excel()
                    # Mostrar mensaje de éxito como popup flotante
                    popup = {
                        'lines': [f'Datos exportados a:', filename],
                        'start': time.time(),
                        'duration': 3.0,
                        'x': ANCHO//2 - 180,
                        'y': ALTO//2 - 40,
                        'vy': -30.0,
                        'color': (30, 180, 30)
                    }
                    floating_popups.append(popup)
            else:
                if pos:
                    if not seleccionado:
                        seleccionado = pos
                    else:
                        if son_adyacentes(seleccionado, pos):
                            intercambiar(seleccionado, pos)
                            # Activar habilidad si se movió sobre una
                            if pos in skills_on_map:
                                activate_skill_at(pos)
                            # Buscar matches y resolver cascadas
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

    # Comprobar si se alcanzó objetivo para subir de nivel
    if score >= goal_for_level():
        if level >= MAX_LEVEL:
            # completó el último nivel: victoria
            show_end_screen(victory=True)
            running = False
            break
        else:
            # informar subida de nivel
            show_level_up(level + 1)
            level += 1
            level_start_time = time.time()

    # Comprobar tiempo de nivel
    elapsed = time.time() - level_start_time
    if elapsed >= LEVEL_TIME:
        # tiempo finalizado
        if score >= goal_for_level():
            if level >= MAX_LEVEL:
                # Ganó el juego
                # mostrar pantalla de felicitaciones simple y salir
                ventana.fill(BLANCO)
                msg = large_font.render('¡Felicidades! Completaste el nivel final.', True, (0,0,0))
                ventana.blit(msg, (50, ALTO//2 - 20))
                pygame.display.flip()
                pygame.time.delay(3000)
                running = False
            else:
                level += 1
                level_start_time = time.time()
                # aumentar objetivo y continuar
        else:
            # Game over
            show_end_screen(victory=False)
            running = False

    dibujar_interface()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()