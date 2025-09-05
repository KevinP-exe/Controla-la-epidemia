import pygame
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import numpy as np

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.hovered = False
        self.clicked = False
        self.enabled = True
    
    def handle_event(self, event):
        if not self.enabled:
            return False
            
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
    
    def set_enabled(self, enabled):
        self.enabled = enabled
    
    def draw(self, screen):
        if not self.enabled:
            color = (60, 60, 60)
            text_color = (120, 120, 120)
        else:
            color = self.hover_color if self.hovered else self.color
            text_color = self.text_color
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (150, 150, 150) if self.enabled else (80, 80, 80), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ConfirmDialog:
    def __init__(self, screen, message, title="Confirmación"):
        self.screen = screen
        self.message = message
        self.title = title
        self.font_title = pygame.font.Font(None, 32)
        self.font_text = pygame.font.Font(None, 24)
        
        # Calcular tamaño del diálogo
        self.dialog_width = 400
        self.dialog_height = 200
        screen_width, screen_height = screen.get_size()
        self.dialog_rect = pygame.Rect(
            (screen_width - self.dialog_width) // 2,
            (screen_height - self.dialog_height) // 2,
            self.dialog_width,
            self.dialog_height
        )
        
        # Botones
        button_width, button_height = 100, 40
        button_y = self.dialog_rect.y + self.dialog_height - 60
        
        self.yes_button = Button(
            self.dialog_rect.x + 80, button_y,
            button_width, button_height,
            "Sí", (150, 50, 50)
        )
        
        self.no_button = Button(
            self.dialog_rect.x + 220, button_y,
            button_width, button_height,
            "No", (50, 150, 50)
        )
        
        self.result = None
    
    def handle_event(self, event):
        if self.yes_button.handle_event(event):
            self.result = True
            return True
        elif self.no_button.handle_event(event):
            self.result = False
            return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_y:
                self.result = True
                return True
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                self.result = False
                return True
        
        return False
    
    def draw(self):
        # Fondo semi-transparente
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Diálogo
        pygame.draw.rect(self.screen, (40, 40, 60), self.dialog_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.dialog_rect, 3)
        
        # Título
        title_text = self.font_title.render(self.title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Mensaje
        message_lines = self.message.split('\n')
        y_offset = self.dialog_rect.y + 80
        for line in message_lines:
            message_text = self.font_text.render(line, True, (200, 200, 200))
            message_rect = message_text.get_rect(center=(self.dialog_rect.centerx, y_offset))
            self.screen.blit(message_text, message_rect)
            y_offset += 30
        
        # Botones
        self.yes_button.draw(self.screen)
        self.no_button.draw(self.screen)

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_desc = pygame.font.Font(None, 20)
        
        # Botones
        screen_width, screen_height = screen.get_size()
        button_width, button_height = 200, 50
        center_x = screen_width // 2 - button_width // 2
        
        self.easy_button = Button(center_x, 320, button_width, button_height, "Fácil", (0, 120, 0))
        self.normal_button = Button(center_x, 390, button_width, button_height, "Normal", (120, 120, 0))
        self.expert_button = Button(center_x, 460, button_width, button_height, "Experto", (120, 0, 0))
        self.quit_button = Button(center_x, 540, button_width, button_height, "Salir", (100, 100, 100))
        
        # Animación de título
        self.title_pulse = 0
    
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
        import time
        self.title_pulse = (time.time() * 2) % (2 * 3.14159)
    
    def draw(self):
        # Fondo animado
        self.draw_animated_background()
        
        # Título con efecto de pulsación
        title_alpha = int(255 * (0.8 + 0.2 * abs(np.sin(self.title_pulse))))
        title_color = (min(255, 200 + title_alpha//5), min(255, 200 + title_alpha//5), 255)
        
        title_text = self.font_title.render("Controla la Epidemia Global", True, title_color)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 120))
        
        # Sombra del título
        shadow_text = self.font_title.render("Controla la Epidemia Global", True, (50, 50, 50))
        shadow_rect = shadow_text.get_rect(center=(self.screen.get_width() // 2 + 3, 123))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_subtitle.render("Selecciona la dificultad:", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Botones
        self.easy_button.draw(self.screen)
        self.normal_button.draw(self.screen)
        self.expert_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # Descripción de la dificultad seleccionada
        self.draw_difficulty_descriptions()
        
        # Información del juego
        info_text = "Un simulador de gestión de crisis epidemiológica"
        info_surface = self.font_desc.render(info_text, True, (150, 150, 150))
        info_rect = info_surface.get_rect(center=(self.screen.get_width() // 2, 180))
        self.screen.blit(info_surface, info_rect)
    
    def draw_animated_background(self):
        """Dibuja un fondo animado con efecto de virus"""
        import time
        import math
        
        self.screen.fill((10, 10, 30))
        
        # Partículas simulando virus
        current_time = time.time()
        for i in range(20):
            x = (current_time * 20 + i * 60) % (self.screen.get_width() + 100) - 50
            y = 50 + i * 30 + 20 * math.sin(current_time + i)
            size = 3 + 2 * math.sin(current_time * 2 + i)
            alpha = int(100 + 50 * math.sin(current_time + i))
            
            # Crear superficie con alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (min(255, 100 + alpha//2), min(255, 50 + alpha//3), min(255, 150 + alpha//2), alpha)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            self.screen.blit(particle_surface, (x - size, y - size))
    
    def draw_difficulty_descriptions(self):
        """Dibuja las descripciones de dificultad"""
        descriptions = {
            "easy": [
                "• Recursos abundantes y virus menos agresivo",
                "• Ideal para aprender las mecánicas del juego",
                "• Economía y moral más resistentes"
            ],
            "normal": [
                "• Experiencia equilibrada y realista",
                "• Desafío moderado con recursos limitados",
                "• Basado en datos de epidemias reales"
            ],
            "expert": [
                "• Crisis extrema con recursos muy limitados",
                "• Virus altamente contagioso y mortal",
                "• Solo recomendado para jugadores expertos"
            ]
        }
        
        # Detectar botón hover para mostrar descripción
        mouse_pos = pygame.mouse.get_pos()
        selected_difficulty = None
        
        if self.easy_button.rect.collidepoint(mouse_pos):
            selected_difficulty = "easy"
        elif self.normal_button.rect.collidepoint(mouse_pos):
            selected_difficulty = "normal"
        elif self.expert_button.rect.collidepoint(mouse_pos):
            selected_difficulty = "expert"
        
        if selected_difficulty:
            # Panel de descripción
            panel_rect = pygame.Rect(200, 620, 800, 120)
            pygame.draw.rect(self.screen, (30, 30, 50), panel_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
            
            y_offset = panel_rect.y + 20
            for desc_line in descriptions[selected_difficulty]:
                desc_text = self.font_desc.render(desc_line, True, (200, 200, 200))
                desc_rect = desc_text.get_rect(center=(panel_rect.centerx, y_offset))
                self.screen.blit(desc_text, desc_rect)
                y_offset += 25

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 32)
        
        # Layout mejorado - sin superposiciones
        self.status_panel_rect = pygame.Rect(10, 10, 300, 180)
        self.continent_panels_rect = pygame.Rect(320, 10, 860, 140)
        self.map_rect = pygame.Rect(10, 200, 500, 400)
        self.decisions_rect = pygame.Rect(520, 200, 400, 450)
        self.events_rect = pygame.Rect(930, 200, 260, 450)
        
        # Botones de control en la parte inferior
        button_y = self.screen_height - 60
        self.next_day_button = Button(50, button_y, 120, 40, "Siguiente Día", (0, 100, 200))
        self.stats_button = Button(190, button_y, 120, 40, "Estadísticas", (100, 0, 100))
        self.menu_button = Button(330, button_y, 100, 40, "Menú", (150, 0, 0))
        
        # Panel de estadísticas
        self.stats_panel_visible = False
        self.stats_surface = None
        
        # Diálogo de confirmación
        self.confirm_dialog = None
    
    def handle_event(self, event):
        # Manejar diálogo de confirmación primero
        if self.confirm_dialog:
            if self.confirm_dialog.handle_event(event):
                result = self.confirm_dialog.result
                self.confirm_dialog = None
                if result:  # Usuario confirmó salir
                    return "menu"
            return None
        
        # Si las estadísticas están visibles, solo manejar eventos de estadísticas
        if self.stats_panel_visible:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stats_panel_visible = False
                self.stats_surface = None
            elif event.type == pygame.MOUSEBUTTONUP:
                # Click fuera del panel de estadísticas para cerrar
                stats_rect = pygame.Rect(100, 50, self.screen_width - 200, self.screen_height - 100)
                if not stats_rect.collidepoint(event.pos):
                    self.stats_panel_visible = False
                    self.stats_surface = None
            return None
        
        # Eventos normales del juego
        if self.next_day_button.handle_event(event):
            return "next_day"
        elif self.stats_button.handle_event(event):
            self.stats_panel_visible = True
            return "toggle_stats"
        elif self.menu_button.handle_event(event):
            # Mostrar diálogo de confirmación
            self.confirm_dialog = ConfirmDialog(
                self.screen,
                "¿Estás seguro de que quieres\nvolver al menú principal?\n\nSe perderá el progreso actual.",
                "Confirmar Salida"
            )
            return None
        
        return None
    
    def set_buttons_enabled(self, enabled):
        """Habilita o deshabilita los botones principales"""
        self.next_day_button.set_enabled(enabled)
        self.stats_button.set_enabled(enabled)
        self.menu_button.set_enabled(enabled)
    
    def draw_status_panel(self, day, global_stats):
        """Dibuja el panel de estado global mejorado"""
        pygame.draw.rect(self.screen, (30, 30, 50), self.status_panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 150), self.status_panel_rect, 2)
        
        # Título del panel
        title_text = self.font.render("Estado Global", True, (255, 255, 0))
        self.screen.blit(title_text, (self.status_panel_rect.x + 10, self.status_panel_rect.y + 10))
        
        # Estadísticas
        y_offset = self.status_panel_rect.y + 35
        stats = [
            f"Día: {day}",
            f"Población: {global_stats['total_population']:,}",
            f"Infectados: {global_stats['infected']:,}",
            f"Recuperados: {global_stats['recovered']:,}",
            f"Muertes: {global_stats['deaths']:,}",
            f"Economía: {global_stats['economy']:.1f}%",
            f"Moral: {global_stats['morale']:.1f}%"
        ]
        
        for stat in stats:
            # Color según el tipo de estadística
            if "Muertes" in stat:
                color = (255, 150, 150)
            elif "Infectados" in stat:
                color = (255, 200, 150)
            elif "Recuperados" in stat:
                color = (150, 255, 150)
            elif "Economía" in stat or "Moral" in stat:
                value = float(stat.split(":")[1].replace("%", "").strip())
                if value > 70:
                    color = (150, 255, 150)
                elif value > 40:
                    color = (255, 255, 150)
                else:
                    color = (255, 150, 150)
            else:
                color = (255, 255, 255)
            
            text_surface = self.font_small.render(stat, True, color)
            self.screen.blit(text_surface, (self.status_panel_rect.x + 10, y_offset))
            y_offset += 20
    
    def draw_continent_panels(self, continents):
        """Dibuja los paneles de continentes mejorados"""
        panel_width = 280
        panel_height = 130
        
        for i, continent in enumerate(continents):
            x = self.continent_panels_rect.x + i * (panel_width + 10)
            y = self.continent_panels_rect.y
            panel_rect = pygame.Rect(x, y, panel_width, panel_height)
            
            # Color de fondo según nivel de infección
            infection_rate = continent.get_infection_rate()
            if infection_rate < 0.01:
                bg_color = (30, 60, 30)
                border_color = (100, 200, 100)
            elif infection_rate < 0.05:
                bg_color = (60, 60, 30)
                border_color = (200, 200, 100)
            else:
                bg_color = (60, 30, 30)
                border_color = (200, 100, 100)
            
            pygame.draw.rect(self.screen, bg_color, panel_rect)
            pygame.draw.rect(self.screen, border_color, panel_rect, 2)
            
            # Nombre del continente
            name_text = self.font.render(continent.name, True, (255, 255, 255))
            self.screen.blit(name_text, (x + 10, y + 8))
            
            # Estadísticas del continente
            y_offset = y + 30
            continent_stats = [
                f"Población: {continent.population:,}",
                f"Infectados: {int(continent.I):,}",
                f"Tasa: {infection_rate:.2%}",
                f"Economía: {continent.economy:.0f}%",
                f"Moral: {continent.morale:.0f}%"
            ]
            
            for stat in continent_stats:
                text_surface = self.font_small.render(stat, True, (255, 255, 255))
                self.screen.blit(text_surface, (x + 10, y_offset))
                y_offset += 16
    
    def generate_improved_stats_chart(self, history):
        """Genera gráficos más comprensibles"""
        if not history or len(history) < 2:
            return None
        
        # Configurar matplotlib para fondo oscuro
        plt.style.use('dark_background')
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor('#1a1a2e')
        
        days = list(range(len(history)))
        
        # Gráfico 1: Casos activos vs Recuperados
        infected_data = [day_data['global']['infected'] for day_data in history]
        recovered_data = [day_data['global']['recovered'] for day_data in history]
        
        axes[0,0].fill_between(days, infected_data, color='#ff6b6b', alpha=0.7, label='Casos Activos')
        axes[0,0].fill_between(days, recovered_data, color='#4ecdc4', alpha=0.7, label='Recuperados')
        axes[0,0].set_title('Evolución de Casos', fontsize=14, color='white', pad=20)
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].set_ylabel('Número de Personas', color='white')
        
        # Gráfico 2: Muertes diarias (no acumuladas)
        deaths_data = [day_data['global']['deaths'] for day_data in history]
        daily_deaths = [deaths_data[i] - deaths_data[i-1] if i > 0 else deaths_data[i] 
                       for i in range(len(deaths_data))]
        
        axes[0,1].bar(days, daily_deaths, color='#ff4757', alpha=0.8)
        axes[0,1].set_title('Muertes por Día', fontsize=14, color='white', pad=20)
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].set_ylabel('Muertes Diarias', color='white')
        
        # Gráfico 3: Economía Global
        economy_data = [day_data['global']['economy'] for day_data in history]
        color_economy = ['#2ed573' if x > 60 else '#ffa502' if x > 30 else '#ff4757' for x in economy_data]
        
        axes[1,0].plot(days, economy_data, color='#3742fa', linewidth=3, marker='o', markersize=4)
        axes[1,0].fill_between(days, economy_data, alpha=0.3, color='#3742fa')
        axes[1,0].set_title('Estado de la Economía Global', fontsize=14, color='white', pad=20)
        axes[1,0].set_ylabel('Economía (%)', color='white')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].set_ylim(0, 100)
        
        # Líneas de referencia
        axes[1,0].axhline(y=70, color='#2ed573', linestyle='--', alpha=0.7, label='Buena')
        axes[1,0].axhline(y=30, color='#ff4757', linestyle='--', alpha=0.7, label='Crisis')
        axes[1,0].legend()
        
        # Gráfico 4: Moral Global
        morale_data = [day_data['global']['morale'] for day_data in history]
        
        axes[1,1].plot(days, morale_data, color='#26d0ce', linewidth=3, marker='s', markersize=4)
        axes[1,1].fill_between(days, morale_data, alpha=0.3, color='#26d0ce')
        axes[1,1].set_title('Moral de la Población', fontsize=14, color='white', pad=20)
        axes[1,1].set_ylabel('Moral (%)', color='white')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].set_ylim(0, 100)
        
        # Líneas de referencia
        axes[1,1].axhline(y=70, color='#2ed573', linestyle='--', alpha=0.7, label='Alta')
        axes[1,1].axhline(y=30, color='#ff4757', linestyle='--', alpha=0.7, label='Baja')
        axes[1,1].legend()
        
        # Personalizar todos los ejes
        for ax in axes.flat:
            ax.set_facecolor('#16213e')
            ax.tick_params(colors='white', labelsize=10)
            ax.set_xlabel('Días', color='white')
            for spine in ax.spines.values():
                spine.set_color('white')
                spine.set_alpha(0.5)
        
        plt.tight_layout(pad=3.0)
        
        # Convertir a superficie de Pygame
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = fig.canvas.get_width_height()
        surf = pygame.image.frombuffer(raw_data.tobytes(), size, "RGBA")
        
        plt.close(fig)
        plt.style.use('default')  # Restaurar estilo por defecto
        return surf
    
    def draw_stats_panel(self, history):
        """Dibuja el panel de estadísticas mejorado"""
        if not self.stats_panel_visible:
            return
        
        # Fondo semi-transparente que bloquea interacciones
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Panel principal de estadísticas
        stats_rect = pygame.Rect(100, 50, self.screen_width - 200, self.screen_height - 100)
        pygame.draw.rect(self.screen, (20, 20, 40), stats_rect)
        pygame.draw.rect(self.screen, (100, 150, 200), stats_rect, 3)
        
        # Título
        title_text = self.font_large.render("Análisis Estadístico de la Pandemia", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(stats_rect.centerx, stats_rect.y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Generar gráficos si es necesario
        if self.stats_surface is None and history:
            self.stats_surface = self.generate_improved_stats_chart(history)
        
        if self.stats_surface:
            # Escalar y centrar la superficie de estadísticas
            chart_rect = self.stats_surface.get_rect()
            max_width = stats_rect.width - 40
            max_height = stats_rect.height - 120
            
            scale_x = max_width / chart_rect.width
            scale_y = max_height / chart_rect.height
            scale = min(scale_x, scale_y, 1.0)  # No ampliar, solo reducir si es necesario
            
            if scale < 1.0:
                new_width = int(chart_rect.width * scale)
                new_height = int(chart_rect.height * scale)
                scaled_surface = pygame.transform.scale(self.stats_surface, (new_width, new_height))
            else:
                scaled_surface = self.stats_surface
            
            # Centrar la imagen escalada
            chart_rect = scaled_surface.get_rect()
            chart_rect.center = (stats_rect.centerx, stats_rect.centery + 20)
            self.screen.blit(scaled_surface, chart_rect)
        
        # Instrucciones para cerrar
        instructions = [
            "ESC - Cerrar estadísticas",
            "Click fuera del panel para cerrar"
        ]
        
        y_offset = stats_rect.bottom - 50
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(stats_rect.centerx, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 20
    
    def draw(self, day, global_stats, continents, history):
        """Dibuja la interfaz principal mejorada"""
        # Paneles principales (solo si las estadísticas no están visibles)
        if not self.stats_panel_visible:
            self.draw_status_panel(day, global_stats)
            self.draw_continent_panels(continents)
        
        # Botones de control
        self.next_day_button.draw(self.screen)
        self.stats_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
        # Panel de estadísticas (se dibuja encima de todo)
        self.draw_stats_panel(history)
        
        # Diálogo de confirmación (se dibuja encima de todo)
        if self.confirm_dialog:
            self.confirm_dialog.draw()