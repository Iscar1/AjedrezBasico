import pygame

# Configuración inicial
ANCHO_TABLERO = 640
ALTO_TABLERO = 640
ANCHO_VENTANA = ANCHO_TABLERO
ALTO_VENTANA = ALTO_TABLERO + 80  # Espacio extra para información
FILAS, COLUMNAS = 8, 8
TAM_CASILLA = ANCHO_TABLERO // COLUMNAS

# Definir las piezas y posiciones iniciales
# Representación: 'P'=peón, 'T'=torre, 'C'=caballo, 'A'=alfil, 'Q'=reina, 'K'=rey
# Mayúsculas = blancas, minúsculas = negras
# Fila 0 = arriba (negras), Fila 7 = abajo (blancas)
POSICIONES_INICIALES = [
    ['t', 'c', 'a', 'q', 'k', 'a', 'c', 't'],  # Fila 0 - Negras
    ['p'] * 8,                                  # Fila 1 - Peones negros
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ['P'] * 8,                                  # Fila 6 - Peones blancos
    ['T', 'C', 'A', 'Q', 'K', 'A', 'C', 'T'],  # Fila 7 - Blancas
]

# Colores
BLANCO = (232, 235, 239)
NEGRO = (125, 135, 150)

# Colores de piezas
COLOR_BLANCO = (240, 240, 240)
COLOR_NEGRO = (40, 40, 40)

# Diccionario para asociar letras a colores (luego se puede asociar a imágenes)
PIEZAS = {
    'P': COLOR_BLANCO, 'T': COLOR_BLANCO, 'C': COLOR_BLANCO, 'A': COLOR_BLANCO, 'Q': COLOR_BLANCO, 'K': COLOR_BLANCO,
    'p': COLOR_NEGRO, 't': COLOR_NEGRO, 'c': COLOR_NEGRO, 'a': COLOR_NEGRO, 'q': COLOR_NEGRO, 'k': COLOR_NEGRO
}

pygame.init()
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption('Ajedrez Básico')


def dibujar_tablero(ventana):
    # Limpiar toda la ventana
    ventana.fill((240, 240, 240))  # Color de fondo gris claro
    
    # Dibujar el tablero en la parte superior
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            if (fila + col) % 2 == 0:
                color = BLANCO
            else:
                color = NEGRO
            pygame.draw.rect(
                ventana, color,
                (col * TAM_CASILLA, fila * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA)
            )

def dibujar_piezas(ventana, posiciones):
    radio = TAM_CASILLA // 2 - 8
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            pieza = posiciones[fila][col]
            if pieza:
                color = PIEZAS[pieza]
                centro = (
                    col * TAM_CASILLA + TAM_CASILLA // 2,
                    fila * TAM_CASILLA + TAM_CASILLA // 2
                )
                
                # Si es un rey en jaque, dibujarlo en rojo
                if (pieza == 'K' and esta_en_jaque(posiciones, True)) or \
                   (pieza == 'k' and esta_en_jaque(posiciones, False)):
                    color = (255, 0, 0)  # Rojo para rey en jaque
                
                pygame.draw.circle(ventana, color, centro, radio)
                # Opcional: dibujar la letra de la pieza
                fuente = pygame.font.SysFont(None, 32)
                letra = pieza.upper() if color == COLOR_BLANCO or color == (255, 0, 0) else pieza.lower()
                texto = fuente.render(letra, True, (0,0,0) if color == COLOR_BLANCO else (255,255,255))
                rect = texto.get_rect(center=centro)
                ventana.blit(texto, rect)

def obtener_casilla_desde_pos(pos, rotacion_180):
    x, y = pos
    col = x // TAM_CASILLA
    fila = y // TAM_CASILLA
    
    # Validar que las coordenadas estén dentro del tablero
    if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
        # Desrotar las coordenadas para obtener las coordenadas reales del tablero
        return desrotar_coordenadas(fila, col, rotacion_180)
    else:
        return None, None

def es_movimiento_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino):
    """Valida si el movimiento es legal según las reglas del ajedrez"""
    pieza = posiciones[fila_origen][col_origen]
    if not pieza:
        return False
    
    # Verificar que no se capture pieza del mismo color
    pieza_destino = posiciones[fila_destino][col_destino]
    if pieza_destino:
        if (pieza.isupper() and pieza_destino.isupper()) or (pieza.islower() and pieza_destino.islower()):
            return False
    
    pieza_tipo = pieza.upper()
    
    if pieza_tipo == 'P':  # Peón
        return es_movimiento_peon_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino, pieza.isupper())
    elif pieza_tipo == 'T':  # Torre
        return es_movimiento_torre_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino)
    elif pieza_tipo == 'A':  # Alfil
        return es_movimiento_alfil_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino)
    elif pieza_tipo == 'Q':  # Reina
        return es_movimiento_reina_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino)
    elif pieza_tipo == 'K':  # Rey
        return es_movimiento_rey_valido(fila_origen, col_origen, fila_destino, col_destino)
    elif pieza_tipo == 'C':  # Caballo
        return es_movimiento_caballo_valido(fila_origen, col_origen, fila_destino, col_destino)
    
    return False

def es_movimiento_peon_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino, es_blanco):
    """Valida movimiento de peón"""
    direccion = -1 if es_blanco else 1  # Blancas suben (fila disminuye), negras bajan (fila aumenta)
    
    # Movimiento hacia adelante
    if col_origen == col_destino:
        if fila_destino == fila_origen + direccion:
            return posiciones[fila_destino][col_destino] is None
        # Movimiento inicial de 2 casillas
        elif (es_blanco and fila_origen == 6 and fila_destino == 4) or \
             (not es_blanco and fila_origen == 1 and fila_destino == 3):
            return posiciones[fila_origen + direccion][col_origen] is None and \
                   posiciones[fila_destino][col_destino] is None
    
    # Captura en diagonal
    elif abs(col_destino - col_origen) == 1 and fila_destino == fila_origen + direccion:
        return posiciones[fila_destino][col_destino] is not None
    
    return False

def es_movimiento_torre_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento de torre"""
    if fila_origen != fila_destino and col_origen != col_destino:
        return False
    
    # Verificar que no hay piezas en el camino
    if fila_origen == fila_destino:  # Movimiento horizontal
        inicio = min(col_origen, col_destino) + 1
        fin = max(col_origen, col_destino)
        for col in range(inicio, fin):
            if posiciones[fila_origen][col] is not None:
                return False
    else:  # Movimiento vertical
        inicio = min(fila_origen, fila_destino) + 1
        fin = max(fila_origen, fila_destino)
        for fila in range(inicio, fin):
            if posiciones[fila][col_origen] is not None:
                return False
    
    return True

def es_movimiento_alfil_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento de alfil"""
    if abs(fila_destino - fila_origen) != abs(col_destino - col_origen):
        return False
    
    # Verificar que no hay piezas en el camino diagonal
    fila_dir = 1 if fila_destino > fila_origen else -1
    col_dir = 1 if col_destino > col_origen else -1
    
    fila, col = fila_origen + fila_dir, col_origen + col_dir
    while fila != fila_destino and col != col_destino:
        if posiciones[fila][col] is not None:
            return False
        fila += fila_dir
        col += col_dir
    
    return True

def es_movimiento_reina_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento de reina (combinación de torre y alfil)"""
    return es_movimiento_torre_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino) or \
           es_movimiento_alfil_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino)

def es_movimiento_rey_valido(fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento de rey"""
    return abs(fila_destino - fila_origen) <= 1 and abs(col_destino - col_origen) <= 1

def es_movimiento_caballo_valido(fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento de caballo"""
    dif_fila = abs(fila_destino - fila_origen)
    dif_col = abs(col_destino - col_origen)
    return (dif_fila == 2 and dif_col == 1) or (dif_fila == 1 and dif_col == 2)

def obtener_movimientos_validos(posiciones, fila_origen, col_origen):
    """Obtiene todos los movimientos válidos para una pieza en la posición dada"""
    movimientos = []
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            if es_movimiento_valido_con_jaque(posiciones, fila_origen, col_origen, fila, col):
                movimientos.append((fila, col))
    return movimientos

def dibujar_guia_movimientos(ventana, movimientos_validos):
    """Dibuja círculos semitransparentes en las casillas donde se puede mover la pieza"""
    # Crear superficie semitransparente
    superficie_guia = pygame.Surface((ANCHO_TABLERO, ALTO_TABLERO), pygame.SRCALPHA)
    
    for fila, col in movimientos_validos:
        centro = (
            col * TAM_CASILLA + TAM_CASILLA // 2,
            fila * TAM_CASILLA + TAM_CASILLA // 2
        )
        # Círculo semitransparente verde para movimientos válidos
        pygame.draw.circle(superficie_guia, (0, 255, 0, 128), centro, TAM_CASILLA // 4)
    
    # Dibujar la superficie sobre la ventana
    ventana.blit(superficie_guia, (0, 0))

def encontrar_rey(posiciones, es_blanco):
    """Encuentra la posición del rey del color especificado"""
    rey = 'K' if es_blanco else 'k'
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            if posiciones[fila][col] == rey:
                return fila, col
    return None

def esta_en_jaque(posiciones, es_blanco):
    """Verifica si el rey del color especificado está en jaque"""
    pos_rey = encontrar_rey(posiciones, es_blanco)
    if not pos_rey:
        return False
    
    fila_rey, col_rey = pos_rey
    
    # Verificar si alguna pieza del oponente puede capturar al rey
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            pieza = posiciones[fila][col]
            if pieza and ((es_blanco and pieza.islower()) or (not es_blanco and pieza.isupper())):
                if es_movimiento_valido(posiciones, fila, col, fila_rey, col_rey):
                    return True
    return False

def movimiento_saca_del_jaque(posiciones, fila_origen, col_origen, fila_destino, col_destino, es_blanco):
    """Verifica si un movimiento saca al rey del jaque"""
    # Crear una copia del tablero para simular el movimiento
    posiciones_temp = [fila[:] for fila in posiciones]
    posiciones_temp[fila_destino][col_destino] = posiciones_temp[fila_origen][col_origen]
    posiciones_temp[fila_origen][col_origen] = None
    
    # Verificar si el rey sigue en jaque después del movimiento
    return not esta_en_jaque(posiciones_temp, es_blanco)

def es_movimiento_valido_con_jaque(posiciones, fila_origen, col_origen, fila_destino, col_destino):
    """Valida movimiento considerando las reglas de jaque"""
    pieza = posiciones[fila_origen][col_origen]
    if not pieza:
        return False
    
    es_blanco = pieza.isupper()
    
    # Verificar movimiento básico
    if not es_movimiento_valido(posiciones, fila_origen, col_origen, fila_destino, col_destino):
        return False
    
    # Si el rey está en jaque, solo permitir movimientos que lo saquen del jaque
    if esta_en_jaque(posiciones, es_blanco):
        return movimiento_saca_del_jaque(posiciones, fila_origen, col_origen, fila_destino, col_destino, es_blanco)
    
    # Si no está en jaque, verificar que el movimiento no ponga al rey en jaque
    return movimiento_saca_del_jaque(posiciones, fila_origen, col_origen, fila_destino, col_destino, es_blanco)

def hay_movimientos_validos(posiciones, es_blanco):
    """Verifica si hay movimientos válidos para el color especificado"""
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            pieza = posiciones[fila][col]
            if pieza and ((es_blanco and pieza.isupper()) or (not es_blanco and pieza.islower())):
                for fila_dest in range(FILAS):
                    for col_dest in range(COLUMNAS):
                        if es_movimiento_valido_con_jaque(posiciones, fila, col, fila_dest, col_dest):
                            return True
    return False

def es_jaque_mate(posiciones, es_blanco):
    """Verifica si es jaque mate para el color especificado"""
    return esta_en_jaque(posiciones, es_blanco) and not hay_movimientos_validos(posiciones, es_blanco)

def verificar_promocion_peon(posiciones, fila_destino, col_destino):
    """Verifica si un peón debe ser promovido y retorna True si es necesario"""
    pieza = posiciones[fila_destino][col_destino]
    if pieza and pieza.upper() == 'P':
        # Peón blanco en la primera fila o peón negro en la última fila
        if (pieza == 'P' and fila_destino == 0) or (pieza == 'p' and fila_destino == 7):
            return True
    return False

def mostrar_dialogo_promocion(ventana, es_blanco):
    """Muestra un diálogo para seleccionar la pieza de promoción"""
    # Crear superficie semitransparente para el fondo
    superficie_dialogo = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
    superficie_dialogo.fill((0, 0, 0, 128))  # Fondo semitransparente negro
    
    # Dibujar el fondo
    ventana.blit(superficie_dialogo, (0, 0))
    
    # Opciones de promoción
    opciones = ['Q', 'T', 'A', 'C']  # Reina, Torre, Alfil, Caballo
    if not es_blanco:
        opciones = [opcion.lower() for opcion in opciones]
    
    # Configuración del diálogo
    ancho_dialogo = 300
    alto_dialogo = 150
    x_dialogo = (ANCHO_VENTANA - ancho_dialogo) // 2
    y_dialogo = (ALTO_VENTANA - alto_dialogo) // 2
    
    # Dibujar fondo del diálogo
    pygame.draw.rect(ventana, (255, 255, 255), (x_dialogo, y_dialogo, ancho_dialogo, alto_dialogo))
    pygame.draw.rect(ventana, (0, 0, 0), (x_dialogo, y_dialogo, ancho_dialogo, alto_dialogo), 3)
    
    # Título
    fuente_titulo = pygame.font.SysFont(None, 28)
    texto_titulo = fuente_titulo.render("Selecciona la pieza de promoción:", True, (0, 0, 0))
    ventana.blit(texto_titulo, (x_dialogo + 10, y_dialogo + 10))
    
    # Dibujar opciones
    tam_opcion = 50
    espaciado = 20
    x_inicio = x_dialogo + (ancho_dialogo - (len(opciones) * tam_opcion + (len(opciones) - 1) * espaciado)) // 2
    y_opciones = y_dialogo + 50
    
    opciones_rect = []
    for i, opcion in enumerate(opciones):
        x = x_inicio + i * (tam_opcion + espaciado)
        rect = pygame.Rect(x, y_opciones, tam_opcion, tam_opcion)
        opciones_rect.append((rect, opcion))
        
        # Dibujar círculo de la pieza
        color = COLOR_BLANCO if es_blanco else COLOR_NEGRO
        centro = (x + tam_opcion // 2, y_opciones + tam_opcion // 2)
        pygame.draw.circle(ventana, color, centro, tam_opcion // 2 - 5)
        pygame.draw.circle(ventana, (0, 0, 0), centro, tam_opcion // 2 - 5, 2)
        
        # Dibujar letra de la pieza
        fuente = pygame.font.SysFont(None, 24)
        letra = opcion.upper() if es_blanco else opcion.lower()
        color_texto = (0, 0, 0) if es_blanco else (255, 255, 255)
        texto = fuente.render(letra, True, color_texto)
        rect_texto = texto.get_rect(center=centro)
        ventana.blit(texto, rect_texto)
    
    pygame.display.flip()
    
    # Esperar selección del usuario
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, opcion in opciones_rect:
                    if rect.collidepoint(mouse_pos):
                        return opcion
        pygame.time.wait(100)

def dibujar_informacion_juego(ventana, turno_blancas, posiciones, rotacion_180):
    """Dibuja la información del juego en el espacio inferior"""
    # Área de información
    y_info = ALTO_TABLERO
    alto_info = ALTO_VENTANA - ALTO_TABLERO
    
    # Fondo del área de información
    pygame.draw.rect(ventana, (220, 220, 220), (0, y_info, ANCHO_VENTANA, alto_info))
    pygame.draw.line(ventana, (100, 100, 100), (0, y_info), (ANCHO_VENTANA, y_info), 2)
    
    # Configurar fuente
    fuente_grande = pygame.font.SysFont(None, 32)
    fuente_pequena = pygame.font.SysFont(None, 24)
    
    # Información del turno
    color_turno = COLOR_BLANCO if turno_blancas else COLOR_NEGRO
    texto_turno = f"Turno: {'Blancas' if turno_blancas else 'Negras'}"
    texto_surface = fuente_grande.render(texto_turno, True, color_turno)
    ventana.blit(texto_surface, (20, y_info + 15))
    
    # Información de estado (jaque, jaque mate)
    if esta_en_jaque(posiciones, turno_blancas):
        if es_jaque_mate(posiciones, turno_blancas):
            texto_estado = "¡JAQUE MATE!"
            color_estado = (255, 0, 0)  # Rojo
        else:
            texto_estado = "¡JAQUE!"
            color_estado = (255, 165, 0)  # Naranja
        texto_surface = fuente_grande.render(texto_estado, True, color_estado)
        ventana.blit(texto_surface, (20, y_info + 45))
    
    # Información adicional
    texto_ayuda = "Haz clic en una pieza para seleccionarla"
    texto_surface = fuente_pequena.render(texto_ayuda, True, (80, 80, 80))
    ventana.blit(texto_surface, (ANCHO_VENTANA - 300, y_info + 20))
    
    # Información de rotación
    texto_rotacion = f"Rotación: {'180°' if rotacion_180 else '0°'} (R para rotar)"
    texto_surface = fuente_pequena.render(texto_rotacion, True, (80, 80, 80))
    ventana.blit(texto_surface, (ANCHO_VENTANA - 300, y_info + 45))

def rotar_coordenadas(fila, col, rotacion_180):
    """Rota las coordenadas según la rotación del tablero"""
    if rotacion_180:
        return FILAS - 1 - fila, COLUMNAS - 1 - col
    return fila, col

def desrotar_coordenadas(fila, col, rotacion_180):
    """Desrota las coordenadas para obtener las coordenadas reales del tablero"""
    if rotacion_180:
        return FILAS - 1 - fila, COLUMNAS - 1 - col
    return fila, col

def dibujar_tablero_rotado(ventana, rotacion_180):
    """Dibuja el tablero con rotación"""
    # Limpiar toda la ventana
    ventana.fill((240, 240, 240))  # Color de fondo gris claro
    
    # Dibujar el tablero en la parte superior
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            # Aplicar rotación a las coordenadas de dibujo
            fila_dibujo, col_dibujo = rotar_coordenadas(fila, col, rotacion_180)
            
            if (fila + col) % 2 == 0:
                color = BLANCO
            else:
                color = NEGRO
            pygame.draw.rect(
                ventana, color,
                (col_dibujo * TAM_CASILLA, fila_dibujo * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA)
            )

def dibujar_piezas_rotadas(ventana, posiciones, rotacion_180):
    """Dibuja las piezas con rotación del tablero"""
    radio = TAM_CASILLA // 2 - 8
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            pieza = posiciones[fila][col]
            if pieza:
                color = PIEZAS[pieza]
                # Aplicar rotación a las coordenadas de dibujo
                fila_dibujo, col_dibujo = rotar_coordenadas(fila, col, rotacion_180)
                centro = (
                    col_dibujo * TAM_CASILLA + TAM_CASILLA // 2,
                    fila_dibujo * TAM_CASILLA + TAM_CASILLA // 2
                )
                
                # Si es un rey en jaque, dibujarlo en rojo
                if (pieza == 'K' and esta_en_jaque(posiciones, True)) or \
                   (pieza == 'k' and esta_en_jaque(posiciones, False)):
                    color = (255, 0, 0)  # Rojo para rey en jaque
                
                pygame.draw.circle(ventana, color, centro, radio)
                # Opcional: dibujar la letra de la pieza
                fuente = pygame.font.SysFont(None, 32)
                letra = pieza.upper() if color == COLOR_BLANCO or color == (255, 0, 0) else pieza.lower()
                texto = fuente.render(letra, True, (0,0,0) if color == COLOR_BLANCO else (255,255,255))
                rect = texto.get_rect(center=centro)
                ventana.blit(texto, rect)

def dibujar_guia_movimientos_rotada(ventana, movimientos_validos, rotacion_180):
    """Dibuja círculos semitransparentes con rotación"""
    # Crear superficie semitransparente
    superficie_guia = pygame.Surface((ANCHO_TABLERO, ALTO_TABLERO), pygame.SRCALPHA)
    
    for fila, col in movimientos_validos:
        # Aplicar rotación a las coordenadas de dibujo
        fila_dibujo, col_dibujo = rotar_coordenadas(fila, col, rotacion_180)
        centro = (
            col_dibujo * TAM_CASILLA + TAM_CASILLA // 2,
            fila_dibujo * TAM_CASILLA + TAM_CASILLA // 2
        )
        # Círculo semitransparente verde para movimientos válidos
        pygame.draw.circle(superficie_guia, (0, 255, 0, 128), centro, TAM_CASILLA // 4)
    
    # Dibujar la superficie sobre la ventana
    ventana.blit(superficie_guia, (0, 0))

def main():
    posiciones = [fila[:] for fila in POSICIONES_INICIALES]
    seleccionada = None  # (fila, col) de la pieza seleccionada
    movimientos_validos = []  # Lista de movimientos válidos para la pieza seleccionada
    turno_blancas = True  # True = turno de blancas, False = turno de negras
    corriendo = True
    rotacion_180 = False  # Variable para controlar la rotación del tablero
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    # Rotar tablero manualmente con la tecla R
                    rotacion_180 = not rotacion_180
                    print(f"Tablero rotado: {'180°' if rotacion_180 else '0°'}")
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                fila, col = obtener_casilla_desde_pos(mouse_pos, rotacion_180)
                
                # Verificar que el clic fue dentro del tablero
                if fila is None or col is None:
                    continue
                
                if seleccionada:
                    # Mover la pieza seleccionada a la nueva casilla si es válido
                    f0, c0 = seleccionada
                    pieza = posiciones[f0][c0]
                    if pieza:
                        es_valido = es_movimiento_valido_con_jaque(posiciones, f0, c0, fila, col)
                        print(f"Intentando mover {pieza} de ({f0},{c0}) a ({fila},{col}): {es_valido}")
                        if es_valido:
                            posiciones[fila][col] = posiciones[f0][c0]
                            posiciones[f0][c0] = None
                            
                            # Verificar promoción de peón
                            if verificar_promocion_peon(posiciones, fila, col):
                                es_blanco_promocion = posiciones[fila][col].isupper()
                                pieza_promocion = mostrar_dialogo_promocion(ventana, es_blanco_promocion)
                                if pieza_promocion:
                                    posiciones[fila][col] = pieza_promocion
                                    print(f"Peón promovido a {pieza_promocion}")
                                else:
                                    # Si se cierra la ventana, cancelar el movimiento
                                    posiciones[fila][col] = posiciones[f0][c0]
                                    posiciones[f0][c0] = None
                                    continue
                            
                            # Cambiar turno después de un movimiento válido
                            turno_blancas = not turno_blancas
                            print("Movimiento realizado!")
                    seleccionada = None
                    movimientos_validos = []  # Limpiar movimientos válidos
                else:
                    # Seleccionar pieza si hay una en la casilla y es del turno correcto
                    if posiciones[fila][col]:
                        pieza = posiciones[fila][col]
                        print(f"Pieza seleccionada: {pieza} en ({fila},{col})")
                        # Verificar que la pieza es del color del turno actual
                        if (turno_blancas and pieza.isupper()) or (not turno_blancas and pieza.islower()):
                            seleccionada = (fila, col)
                            # Calcular movimientos válidos para la pieza seleccionada
                            movimientos_validos = obtener_movimientos_validos(posiciones, fila, col)
                            print(f"Pieza válida para el turno actual. Movimientos válidos: {len(movimientos_validos)}")
                        else:
                            print(f"Pieza no válida para el turno actual")

        dibujar_tablero_rotado(ventana, rotacion_180)
        dibujar_piezas_rotadas(ventana, posiciones, rotacion_180)
        
        # Dibujar guía de movimientos válidos
        if movimientos_validos:
            dibujar_guia_movimientos_rotada(ventana, movimientos_validos, rotacion_180)
        
        # Resaltar la casilla seleccionada
        if seleccionada:
            f, c = seleccionada
            # Aplicar rotación a las coordenadas de dibujo para el resaltado
            f_dibujo, c_dibujo = rotar_coordenadas(f, c, rotacion_180)
            pygame.draw.rect(
                ventana, (0, 255, 0),
                (c_dibujo * TAM_CASILLA, f_dibujo * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA), 4
            )
        
        # Mostrar indicador de turno
        dibujar_informacion_juego(ventana, turno_blancas, posiciones, rotacion_180)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main() 