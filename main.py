import pygame
import sys
from game_loop import GameLoop
from ui import MainMenu

def main():
    pygame.init()
    
    # Configuración de pantalla
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Controla la Epidemia Global")
    
    clock = pygame.time.Clock()
    
    # Estado del juego
    game_state = "menu"  # "menu" o "playing"
    menu = MainMenu(screen)
    game_loop = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "menu":
                result = menu.handle_event(event)
                if result == "quit":
                    running = False
                elif result in ["easy", "normal", "expert"]:
                    game_loop = GameLoop(screen, result)
                    game_state = "playing"
            
            elif game_state == "playing":
                result = game_loop.handle_event(event)
                if result == "menu":
                    game_state = "menu"
                    game_loop = None
        
        # Renderizado
        if game_state == "menu":
            menu.update()
            menu.draw()
        elif game_state == "playing":
            game_loop.update()
            game_loop.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()