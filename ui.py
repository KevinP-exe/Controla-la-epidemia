import pygame
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import numpy as np

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        self.font = pygame.font.Font(None, 24)
        self.hovered = False
        self.clicked = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.clicked = False
                return True
            self.clicked = False
        return False
    
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        
        # Botones
        screen_width, screen_height = screen.get_size()
        button_width, button_height = 200, 50
        center_x = screen_width // 2 - button_width // 2
        
        self.easy_button = Button(center_x, 300, button_width, button_height, "Fácil", (0, 150, 0))
        self.normal_button = Button(center_x, 370, button_width, button_height, "Normal", (150, 150, 0))
        self.expert_button = Button(center_x, 440, button_width, button_height, "Experto", (150, 0, 0))
        self.quit_button = Button(center_x, 520, button_width, button_height, "Salir", (100, 100, 100))
    
    def handle_event(self, event):
        if self.easy_button.handle_event(event):
            return "easy"
        elif self.normal_button.handle_event(event):
            return "normal"
        elif self.expert_button.handle_event(event):
            return "expert"
        elif self.quit_button.handle_event(event):
            return "quit"
        return None
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((20, 20, 40))
        
        # Título
        title_text = self.font_title.render("Controla la Epidemia Global", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_subtitle.render("Selecciona la dificultad:", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Descripción de dificultades
        descriptions = [
            "Fácil: Más recursos, menos contagiosidad",
            "Normal: Equilibrio entre desafío y recursos",
            "Experto: Alta contagiosidad, recursos limitados"
        ]
        
        font_desc = pygame.font.Font(None, 20)
        for i, desc in enumerate(descriptions):
            desc_text = font_desc.render(desc, True, (150, 150, 150))
            desc_rect = desc_text.get_rect(center=(self.screen.get_width() // 2, 600 + i * 25))
            self.screen.blit(desc_text, desc_rect)
        
        # Botones
        self.easy_button.draw(self.screen)
        self.normal_button.draw(self.screen)
        self.expert_button.draw(self.screen)
        self.quit_button.draw(self.screen)

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Botones de control
        self.next_day_button = Button(50, 700, 150, 40, "Siguiente Día", (0, 100, 200))
        self.stats_button = Button(220, 700, 120, 40, "Estadísticas", (100, 0, 100))
        self.menu_button = Button(360, 700, 100, 40, "Menú", (150, 0, 0))
        
        # Panel de estadísticas
        self.stats_panel_visible = False
        self.stats_surface = None
    
    def handle_event(self, event):
        if self.next_day_button.handle_event(event):
            return "next_day"
        elif self.stats_button.handle_event(event):
            self.stats_panel_visible = not self.stats_panel_visible
            return "toggle_stats"
        elif self.menu_button.handle_event(event):
            return "menu"
        
        if self.stats_panel_visible and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stats_panel_visible = False
        
        return None
    
    def draw_status_panel(self, day, global_stats, continents):
        # Panel de estado global
        panel_rect = pygame.Rect(10, 10, 300, 200)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        y_offset = 25
        texts = [
            f"Día: {day}",
            f"Población Global: {global_stats['total_population']:,}",
            f"Infectados: {global_stats['infected']:,}",
            f"Recuperados: {global_stats['recovered']:,}",
            f"Muertes: {global_stats['deaths']:,}",
            f"Economía Global: {global_stats['economy']:.1f}%",
            f"Moral Global: {global_stats['morale']:.1f}%"
        ]
        
        for text in texts:
            text_surface = self.font_small.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 25
    
    def draw_continent_info(self, continents):
        # Información por continente
        start_x, start_y = 320, 10
        for i, continent in enumerate(continents):
            panel_rect = pygame.Rect(start_x + i * 280, start_y, 270, 150)
            pygame.draw.rect(self.screen, (60, 40, 40), panel_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
            
            # Color según nivel de infección
            infection_rate = continent.get_infection_rate()
            if infection_rate < 0.01:
                color = (0, 150, 0)  # Verde
            elif infection_rate < 0.05:
                color = (150, 150, 0)  # Amarillo
            else:
                color = (150, 0, 0)  # Rojo
            
            pygame.draw.rect(self.screen, color, (start_x + i * 280 + 5, start_y + 5, 260, 10))
            
            y_offset = start_y + 25
            texts = [
                f"{continent.name}",
                f"Población: {continent.population:,}",
                f"Infectados: {int(continent.I):,}",
                f"Recuperados: {int(continent.R):,}",
                f"Muertes: {continent.deaths:,}",
                f"Economía: {continent.economy:.1f}%",
                f"Moral: {continent.morale:.1f}%"
            ]
            
            for j, text in enumerate(texts):
                color = (255, 255, 255) if j > 0 else (255, 255, 0)
                text_surface = self.font_small.render(text, True, color)
                self.screen.blit(text_surface, (start_x + i * 280 + 10, y_offset))
                y_offset += 18
    
    def generate_stats_chart(self, history):
        if not history:
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor('black')
        
        days = list(range(len(history)))
        
        # Gráfico SEIR global
        S_data = [day_data['global']['susceptible'] for day_data in history]
        E_data = [day_data['global']['exposed'] for day_data in history]
        I_data = [day_data['global']['infected'] for day_data in history]
        R_data = [day_data['global']['recovered'] for day_data in history]
        
        axes[0,0].plot(days, S_data, 'b-', label='Susceptibles', linewidth=2)
        axes[0,0].plot(days, E_data, 'y-', label='Expuestos', linewidth=2)
        axes[0,0].plot(days, I_data, 'r-', label='Infectados', linewidth=2)
        axes[0,0].plot(days, R_data, 'g-', label='Recuperados', linewidth=2)
        axes[0,0].set_title('Curva SEIR Global', color='white')
        axes[0,0].legend()
        axes[0,0].set_facecolor('black')
        axes[0,0].tick_params(colors='white')
        
        # Muertes acumuladas
        deaths_data = [day_data['global']['deaths'] for day_data in history]
        axes[0,1].plot(days, deaths_data, 'r-', linewidth=2)
        axes[0,1].set_title('Muertes Acumuladas', color='white')
        axes[0,1].set_facecolor('black')
        axes[0,1].tick_params(colors='white')
        
        # Economía
        economy_data = [day_data['global']['economy'] for day_data in history]
        axes[1,0].plot(days, economy_data, 'b-', linewidth=2)
        axes[1,0].set_title('Economía Global (%)', color='white')
        axes[1,0].set_facecolor('black')
        axes[1,0].tick_params(colors='white')
        
        # Moral
        morale_data = [day_data['global']['morale'] for day_data in history]
        axes[1,1].plot(days, morale_data, 'g-', linewidth=2)
        axes[1,1].set_title('Moral Global (%)', color='white')
        axes[1,1].set_facecolor('black')
        axes[1,1].tick_params(colors='white')
        
        for ax in axes.flat:
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
        
        plt.tight_layout()
        
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = fig.canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data.tobytes(), size, "RGBA")
        
        plt.close(fig)
        return surf
    
    def draw_stats_panel(self, history):
        if self.stats_panel_visible:
            # Fondo semi-transparente
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Panel de estadísticas
            if self.stats_surface is None and history:
                self.stats_surface = self.generate_stats_chart(history)
            
            if self.stats_surface:
                # Centrar la imagen
                surf_rect = self.stats_surface.get_rect()
                screen_rect = self.screen.get_rect()
                surf_rect.center = screen_rect.center
                self.screen.blit(self.stats_surface, surf_rect)
                
                # Botón para cerrar
                close_text = self.font.render("Presiona ESC para cerrar", True, (255, 255, 255))
                close_rect = close_text.get_rect()
                close_rect.centerx = screen_rect.centerx
                close_rect.bottom = screen_rect.bottom - 20
                self.screen.blit(close_text, close_rect)
    
    def draw(self, day, global_stats, continents, history):
        # Botones de control
        self.next_day_button.draw(self.screen)
        self.stats_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
        # Paneles de información
        self.draw_status_panel(day, global_stats, continents)
        self.draw_continent_info(continents)
        
        # Panel de estadísticas si está visible
        if self.stats_panel_visible:
            self.draw_stats_panel(history)