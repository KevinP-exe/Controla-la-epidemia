import pygame
import sys
from game_loop import GameLoop
from ui import MainMenu
from story_screen import StoryScreen

def main():
    """Función principal del juego"""
    pygame.init()
    
    # Configuración de pantalla
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Controla la Epidemia Global - Simulador de Crisis Pandémica")
    
    # Icono de la ventana (opcional)
    try:
        icon = pygame.Surface((32, 32))
        icon.fill((255, 0, 0))
        pygame.draw.circle(icon, (255, 255, 255), (16, 16), 12)
        pygame.draw.circle(icon, (255, 0, 0), (16, 16), 8)
        pygame.display.set_icon(icon)
    except:
        pass  # Si no se puede crear el icono, continuar sin él
    
    clock = pygame.time.Clock()
    FPS = 60
    
    # Estados del juego
    game_state = "menu"  # "menu", "story", "playing"
    menu = MainMenu(screen)
    story_screen = None
    game_loop = None
    selected_difficulty = None
    
    # Variables para controlar transiciones
    fade_surface = None
    fade_alpha = 0
    fade_direction = 0  # 0: no fade, 1: fade out, -1: fade in
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time en segundos
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif game_state == "menu":
                result = menu.handle_event(event)
                if result == "quit":
                    running = False
                elif result in ["easy", "normal", "expert"]:
                    selected_difficulty = result
                    story_screen = StoryScreen(screen, result)
                    game_state = "story"
                    start_fade_transition()
            
            elif game_state == "story":
                result = story_screen.handle_event(event)
                if result == "start_game":
                    game_loop = GameLoop(screen, selected_difficulty)
                    game_state = "playing"
                    start_fade_transition()
            
            elif game_state == "playing":
                result = game_loop.handle_event(event)
                if result == "menu":
                    # Limpiar recursos del juego
                    game_loop = None
                    game_state = "menu"
                    start_fade_transition()
        
        # Actualización de estados
        if game_state == "menu":
            menu.update()
        elif game_state == "story":
            story_screen.update()
        elif game_state == "playing":
            game_loop.update()
        
        # Renderizado
        if game_state == "menu":
            menu.draw()
        elif game_state == "story":
            story_screen.draw()
        elif game_state == "playing":
            game_loop.draw()
        
        # Efectos de transición (opcional)
        draw_fade_effect(screen)
        
        # Actualizar pantalla
        pygame.display.flip()
    
    # Limpieza
    pygame.quit()
    sys.exit()

def start_fade_transition():
    """Inicia un efecto de transición (opcional)"""
    # Esta función podría implementar efectos de transición
    # Por ahora está vacía, pero se puede expandir
    pass

def draw_fade_effect(screen):
    """Dibuja efecto de fade (opcional)"""
    # Esta función podría dibujar efectos de transición
    # Por ahora está vacía, pero se puede expandir
    pass

def show_loading_screen(screen):
    """Muestra pantalla de carga mientras se inicializa el juego"""
    screen.fill((20, 20, 40))
    
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    
    # Título de carga
    loading_text = font_large.render("Iniciando Simulación...", True, (255, 255, 255))
    loading_rect = loading_text.get_rect(center=(screen.get_width() // 2, 
                                               screen.get_height() // 2 - 50))
    screen.blit(loading_text, loading_rect)
    
    # Información adicional
    info_texts = [
        "Configurando continentes...",
        "Inicializando modelos epidemiológicos...",
        "Preparando sistema de decisiones...",
        "Cargando interfaz de usuario..."
    ]
    
    y_offset = screen.get_height() // 2 + 20
    for info in info_texts:
        info_surface = font_medium.render(info, True, (200, 200, 200))
        info_rect = info_surface.get_rect(center=(screen.get_width() // 2, y_offset))
        screen.blit(info_surface, info_rect)
        y_offset += 35
    
    pygame.display.flip()

def handle_error(error_message):
    """Maneja errores del juego mostrando un mensaje al usuario"""
    pygame.init()
    screen = pygame.display.set_mode((600, 300))
    pygame.display.set_caption("Error en el Juego")
    
    font_title = pygame.font.Font(None, 36)
    font_text = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                waiting = False
        
        # Dibujar pantalla de error
        screen.fill((50, 20, 20))
        
        # Título
        title_text = font_title.render("Error en la Aplicación", True, (255, 200, 200))
        title_rect = title_text.get_rect(center=(300, 80))
        screen.blit(title_text, title_rect)
        
        # Mensaje de error
        error_lines = error_message.split('\n')
        y_offset = 130
        for line in error_lines:
            if line.strip():
                error_surface = font_text.render(line, True, (255, 255, 255))
                error_rect = error_surface.get_rect(center=(300, y_offset))
                screen.blit(error_surface, error_rect)
                y_offset += 30
        
        # Instrucción
        instruction_text = font_text.render("Presiona cualquier tecla para salir", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(300, 250))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

def check_dependencies():
    """Verifica que todas las dependencias necesarias estén disponibles"""
    try:
        import numpy
        import matplotlib.pyplot
        import matplotlib.backends.backend_agg
        return True
    except ImportError as e:
        error_msg = f"Dependencia faltante: {str(e)}\n\n"
        error_msg += "Instala las dependencias necesarias:\n"
        error_msg += "pip install numpy matplotlib"
        handle_error(error_msg)
        return False

def print_game_info():
    """Imprime información del juego en la consola"""
    print("=" * 60)
    print("CONTROLA LA EPIDEMIA GLOBAL")
    print("Simulador de Crisis Pandémica")
    print("=" * 60)
    print()
    print("CONTROLES:")
    print("  ESPACIO/ENTER - Avanzar día")
    print("  P - Pausar/Reanudar")
    print("  ESC - Volver al menú (en estadísticas)")
    print("  Click en mapa - Seleccionar continente")
    print()
    print("OBJETIVO:")
    print("  Controla la propagación de una pandemia mundial")
    print("  Balancea salud pública, economía y moral ciudadana")
    print("  Toma decisiones estratégicas para salvar vidas")
    print()
    print("DIFICULTADES:")
    print("  FÁCIL - Recursos abundantes, virus menos agresivo")
    print("  NORMAL - Experiencia equilibrada y realista")
    print("  EXPERTO - Crisis extrema, recursos muy limitados")
    print()
    print("¡Buena suerte salvando al mundo!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Mostrar información del juego
    print_game_info()
    
    try:
        # Ejecutar juego principal
        main()
    
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario.")
        pygame.quit()
        sys.exit(0)
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # Esto imprime el traceback completo en la terminal
        error_msg = f"Error inesperado en el juego:\n{str(e)}\n\n{traceback.format_exc()}\nSi el problema persiste, reinicia el juego."
        print(f"ERROR: {str(e)}")
        handle_error(error_msg)