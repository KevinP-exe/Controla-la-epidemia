import pygame
import time

class StoryScreen:
    def __init__(self, screen, difficulty="normal"):
        self.screen = screen
        self.difficulty = difficulty
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        
        self.story_text = self.get_story_text()
        self.current_page = 0
        self.max_pages = len(self.story_text)
        
        # Animación de texto
        self.text_animation_progress = 0
        self.animation_speed = 50  # caracteres por segundo
        self.last_animation_time = time.time()
        
        # Botones
        self.next_button = pygame.Rect(600, 700, 120, 40)
        self.skip_button = pygame.Rect(750, 700, 120, 40)
        self.prev_button = pygame.Rect(450, 700, 120, 40)
        
        self.button_hovered = None
        self.finished = False
    
    def get_story_text(self):
        """Devuelve el texto de la historia según la dificultad"""
        base_story = [
            {
                "title": "Crisis Global",
                "text": [
                    "Enero 2024: Un nuevo patógeno altamente contagioso ha emergido",
                    "en Asia y se está extendiendo rápidamente por todo el mundo.",
                    "",
                    "Los científicos estiman que sin medidas de contención,",
                    "podría infectar hasta el 70% de la población mundial.",
                    "",
                    "Como líder de la Organización Mundial de la Salud,",
                    "tus decisiones determinarán el destino de la humanidad."
                ]
            },
            {
                "title": "Tu Misión",
                "text": [
                    "Debes coordinar la respuesta global para:",
                    "",
                    "• Minimizar las muertes por la epidemia",
                    "• Mantener la estabilidad económica mundial",
                    "• Preservar la moral y confianza pública",
                    "• Implementar medidas efectivas de contención",
                    "",
                    "Cada decisión tendrá consecuencias a corto y largo plazo.",
                    "El equilibrio entre salud pública y estabilidad social",
                    "será tu mayor desafío."
                ]
            }
        ]
        
        difficulty_info = {
            "easy": {
                "title": "Modo Fácil - Recursos Abundantes",
                "text": [
                    "Ventajas en este modo:",
                    "",
                    "• Mayor capacidad hospitalaria inicial",
                    "• Economía y moral más resistentes",
                    "• Virus menos contagioso y mortal",
                    "• Costos de decisiones reducidos",
                    "• Menos eventos negativos aleatorios",
                    "",
                    "Este modo te permite aprender las mecánicas",
                    "sin la presión extrema de una crisis real."
                ]
            },
            "normal": {
                "title": "Modo Normal - Realismo Equilibrado",
                "text": [
                    "Características de este modo:",
                    "",
                    "• Parámetros basados en epidemias reales",
                    "• Balance entre recursos y desafíos",
                    "• Respuesta realista de la población",
                    "• Eventos aleatorios moderados",
                    "",
                    "La experiencia está calibrada para ofrecer",
                    "un desafío realista pero manejable.",
                    "Requiere planificación estratégica cuidadosa."
                ]
            },
            "expert": {
                "title": "Modo Experto - Crisis Extrema",
                "text": [
                    "Desafíos de este modo:",
                    "",
                    "• Virus altamente contagioso y mortal",
                    "• Recursos hospitalarios limitados",
                    "• Economía y moral muy frágiles",
                    "• Costos de decisiones elevados",
                    "• Eventos adversos frecuentes",
                    "",
                    "Solo para jugadores experimentados.",
                    "Cada error puede ser catastrófico."
                ]
            }
        }
        
        story = base_story.copy()
        story.append(difficulty_info[self.difficulty])
        
        final_page = {
            "title": "¡Comienza la Crisis!",
            "text": [
                "Los primeros casos han sido detectados en tres continentes.",
                "",
                "El mundo te observa. Millones de vidas dependen",
                "de tus decisiones en los próximos días y semanas.",
                "",
                "Recuerda:",
                "• Actúa rápido pero piensa las consecuencias",
                "• Balancea la salud pública con la economía",
                "• Mantén informada y tranquila a la población",
                "• Adapta tu estrategia según evolucione la situación",
                "",
                "¡El destino de la humanidad está en tus manos!"
            ]
        }
        story.append(final_page)
        
        return story
    
    def handle_event(self, event):
        """Maneja eventos de la pantalla de historia"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.button_hovered = None
            
            if self.next_button.collidepoint(mouse_pos):
                self.button_hovered = "next"
            elif self.skip_button.collidepoint(mouse_pos):
                self.button_hovered = "skip"
            elif self.prev_button.collidepoint(mouse_pos) and self.current_page > 0:
                self.button_hovered = "prev"
        
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = event.pos
            
            if self.next_button.collidepoint(mouse_pos):
                return self.next_page()
            elif self.skip_button.collidepoint(mouse_pos):
                self.finished = True
                return "start_game"
            elif self.prev_button.collidepoint(mouse_pos) and self.current_page > 0:
                self.current_page -= 1
                self.text_animation_progress = 0
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return self.next_page()
            elif event.key == pygame.K_ESCAPE:
                self.finished = True
                return "start_game"
            elif event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
                self.text_animation_progress = 0
            elif event.key == pygame.K_RIGHT:
                return self.next_page()
        
        return None
    
    def next_page(self):
        """Avanza a la siguiente página"""
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            self.text_animation_progress = 0
        else:
            self.finished = True
            return "start_game"
        return None
    
    def update(self):
        """Actualiza la animación del texto"""
        current_time = time.time()
        dt = current_time - self.last_animation_time
        self.last_animation_time = current_time
        
        # Calcular texto total de la página actual
        current_story = self.story_text[self.current_page]
        total_text = current_story["title"] + "\n\n" + "\n".join(current_story["text"])
        
        # Animar texto
        target_progress = len(total_text)
        if self.text_animation_progress < target_progress:
            self.text_animation_progress += self.animation_speed * dt
            self.text_animation_progress = min(self.text_animation_progress, target_progress)
    
    def draw(self):
        """Dibuja la pantalla de historia"""
        # Fondo gradiente
        self.draw_gradient_background()
        
        # Contenido de la página actual
        current_story = self.story_text[self.current_page]
        
        # Título
        title_text = self.font_title.render(current_story["title"], True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Texto principal con animación
        self.draw_animated_text(current_story["text"], 150)
        
        # Controles
        self.draw_controls()
        
        # Indicador de página
        page_info = f"{self.current_page + 1} / {self.max_pages}"
        page_text = self.font_small.render(page_info, True, (150, 150, 150))
        page_rect = page_text.get_rect(center=(self.screen.get_width() // 2, 650))
        self.screen.blit(page_text, page_rect)
    
    def draw_gradient_background(self):
        """Dibuja un fondo con gradiente"""
        screen_height = self.screen.get_height()
        for y in range(0, screen_height, 2):
            # Gradiente de azul oscuro a negro
            progress = y / screen_height
            color_value = int(30 * (1 - progress))
            color = (color_value, color_value, color_value + 10)
            pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y), 2)
    
    def draw_animated_text(self, text_lines, start_y):
        """Dibuja texto con efecto de animación"""
        y_offset = start_y
        chars_shown = int(self.text_animation_progress)
        chars_count = 0
        
        for line in text_lines:
            if chars_count >= chars_shown:
                break
            
            # Determinar cuántos caracteres mostrar de esta línea
            line_length = len(line)
            if chars_count + line_length <= chars_shown:
                # Mostrar línea completa
                display_text = line
                chars_count += line_length + 1  # +1 por el salto de línea
            else:
                # Mostrar línea parcial
                chars_to_show = chars_shown - chars_count
                display_text = line[:chars_to_show]
                chars_count = chars_shown
            
            # Renderizar línea
            if display_text.strip():  # Solo si no está vacía
                if line.startswith("•"):
                    # Líneas de lista con color diferente
                    text_color = (200, 255, 200)
                elif line.startswith("Ventajas") or line.startswith("Características") or line.startswith("Desafíos"):
                    text_color = (255, 255, 150)
                else:
                    text_color = (255, 255, 255)
                
                text_surface = self.font_text.render(display_text, True, text_color)
                text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_offset))
                self.screen.blit(text_surface, text_rect)
            
            y_offset += 35
            
            # Añadir espacio extra después de líneas vacías
            if not line.strip():
                y_offset += 15
    
    def draw_controls(self):
        """Dibuja los botones de control"""
        # Botón Anterior (solo si no estamos en la primera página)
        if self.current_page > 0:
            color = (100, 100, 150) if self.button_hovered == "prev" else (70, 70, 120)
            pygame.draw.rect(self.screen, color, self.prev_button)
            pygame.draw.rect(self.screen, (200, 200, 200), self.prev_button, 2)
            
            prev_text = self.font_text.render("Anterior", True, (255, 255, 255))
            prev_rect = prev_text.get_rect(center=self.prev_button.center)
            self.screen.blit(prev_text, prev_rect)
        
        # Botón Siguiente/Comenzar
        if self.current_page < self.max_pages - 1:
            button_text = "Siguiente"
        else:
            button_text = "¡Comenzar!"
        
        color = (100, 150, 100) if self.button_hovered == "next" else (70, 120, 70)
        pygame.draw.rect(self.screen, color, self.next_button)
        pygame.draw.rect(self.screen, (200, 200, 200), self.next_button, 2)
        
        next_text = self.font_text.render(button_text, True, (255, 255, 255))
        next_rect = next_text.get_rect(center=self.next_button.center)
        self.screen.blit(next_text, next_rect)
        
        # Botón Saltar
        color = (150, 100, 100) if self.button_hovered == "skip" else (120, 70, 70)
        pygame.draw.rect(self.screen, color, self.skip_button)
        pygame.draw.rect(self.screen, (200, 200, 200), self.skip_button, 2)
        
        skip_text = self.font_text.render("Saltar", True, (255, 255, 255))
        skip_rect = skip_text.get_rect(center=self.skip_button.center)
        self.screen.blit(skip_text, skip_rect)
        
        # Instrucciones
        instructions = [
            "Usa las flechas del teclado, ESPACIO o ENTER para navegar",
            "ESC para saltar la historia"
        ]
        
        y_offset = 760
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (150, 150, 150))
            inst_rect = inst_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 20