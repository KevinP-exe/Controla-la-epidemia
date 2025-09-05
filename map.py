import pygame
import math

class WorldMap:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # Definir regiones de los continentes en el mapa
        self.continent_regions = {
            0: {  # América
                'name': 'América',
                'center': (250, 400),
                'points': [
                    (150, 200), (200, 180), (280, 190), (320, 220),
                    (350, 300), (340, 450), (320, 550), (280, 580),
                    (220, 570), (180, 520), (160, 450), (140, 350),
                    (130, 280), (140, 220)
                ]
            },
            1: {  # Europa-África
                'name': 'Europa-África',
                'center': (600, 350),
                'points': [
                    (500, 180), (650, 160), (720, 180), (750, 220),
                    (780, 300), (790, 400), (780, 500), (750, 580),
                    (700, 620), (620, 630), (550, 610), (500, 570),
                    (480, 500), (470, 400), (480, 300), (490, 220)
                ]
            },
            2: {  # Asia-Oceanía
                'name': 'Asia-Oceanía',
                'center': (950, 320),
                'points': [
                    (800, 150), (950, 140), (1050, 160), (1100, 200),
                    (1130, 250), (1120, 320), (1100, 400), (1050, 450),
                    (1000, 480), (950, 500), (900, 520), (880, 480),
                    (870, 420), (860, 360), (850, 280), (840, 220),
                    (820, 180)
                ]
            }
        }
        
        # Posiciones de aeropuertos
        self.airports = {
            0: (280, 350),  # América
            1: (620, 300),  # Europa-África  
            2: (980, 280)   # Asia-Oceanía
        }
        
        # Líneas de conexión entre aeropuertos
        self.flight_connections = [
            (0, 1),  # América - Europa-África
            (1, 2),  # Europa-África - Asia-Oceanía
            (0, 2)   # América - Asia-Oceanía
        ]
        
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
    
    def get_continent_color(self, continent):
        """Determina el color de un continente basado en su estado"""
        infection_rate = continent.get_infection_rate()
        
        if infection_rate < 0.001:  # Muy bajo
            return (0, 150, 0)  # Verde oscuro
        elif infection_rate < 0.005:  # Bajo
            return (100, 200, 0)  # Verde claro
        elif infection_rate < 0.01:  # Moderado
            return (200, 200, 0)  # Amarillo
        elif infection_rate < 0.03:  # Alto
            return (255, 150, 0)  # Naranja
        elif infection_rate < 0.05:  # Muy alto
            return (255, 100, 50)  # Rojo-naranja
        else:  # Crítico
            return (200, 0, 0)  # Rojo oscuro
    
    def draw_continent(self, continent_idx, continent, selected=False):
        """Dibuja un continente individual"""
        region = self.continent_regions[continent_idx]
        color = self.get_continent_color(continent)
        
        # Dibujar el continente
        pygame.draw.polygon(self.screen, color, region['points'])
        
        # Borde
        border_color = (255, 255, 255) if selected else (100, 100, 100)
        border_width = 3 if selected else 2
        pygame.draw.polygon(self.screen, border_color, region['points'], border_width)
        
        # Nombre del continente
        name_text = self.font.render(region['name'], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=region['center'])
        
        # Fondo semi-transparente para el texto
        bg_surface = pygame.Surface((name_rect.width + 10, name_rect.height + 4))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        bg_rect = bg_surface.get_rect(center=region['center'])
        self.screen.blit(bg_surface, bg_rect)
        
        self.screen.blit(name_text, name_rect)
        
        # Estadísticas básicas
        stats_y = region['center'][1] + 25
        
        # Infectados
        infected_text = f"Infectados: {int(continent.I):,}"
        infected_surface = self.font_small.render(infected_text, True, (255, 200, 200))
        infected_rect = infected_surface.get_rect(center=(region['center'][0], stats_y))
        
        # Fondo para estadísticas
        stats_bg = pygame.Surface((infected_rect.width + 8, infected_rect.height + 2))
        stats_bg.set_alpha(160)
        stats_bg.fill((0, 0, 0))
        stats_bg_rect = stats_bg.get_rect(center=infected_rect.center)
        self.screen.blit(stats_bg, stats_bg_rect)
        self.screen.blit(infected_surface, infected_rect)
    
    def draw_airports(self, continents):
        """Dibuja los aeropuertos y sus estados"""
        for i, (continent_idx, pos) in enumerate(self.airports.items()):
            continent = continents[continent_idx]
            
            # Color del aeropuerto según su estado
            if continent.airports_open:
                airport_color = (0, 200, 0)  # Verde si está abierto
            else:
                airport_color = (200, 0, 0)  # Rojo si está cerrado
            
            # Dibujar aeropuerto
            pygame.draw.circle(self.screen, airport_color, pos, 8)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 8, 2)
            
            # Símbolo de avión
            pygame.draw.polygon(self.screen, (255, 255, 255), [
                (pos[0] - 4, pos[1]),
                (pos[0] + 4, pos[1] - 2),
                (pos[0] + 4, pos[1] + 2)
            ])
    
    def draw_flight_connections(self, continents):
        """Dibuja las conexiones aéreas entre continentes"""
        for connection in self.flight_connections:
            continent1_idx, continent2_idx = connection
            continent1 = continents[continent1_idx]
            continent2 = continents[continent2_idx]
            
            pos1 = self.airports[continent1_idx]
            pos2 = self.airports[continent2_idx]
            
            # Solo dibujar conexión si ambos aeropuertos están abiertos
            if continent1.airports_open and continent2.airports_open:
                # Línea punteada animada
                self.draw_dashed_line(pos1, pos2, (100, 150, 255), 2)
                
                # Indicar flujo de infectados si existe
                if continent1.I > 0 or continent2.I > 0:
                    # Pequeños puntos moviéndose por la línea
                    self.draw_infection_flow(pos1, pos2)
    
    def draw_dashed_line(self, start, end, color, width):
        """Dibuja una línea punteada entre dos puntos"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return
        
        # Normalizar dirección
        dx /= distance
        dy /= distance
        
        # Dibujar segmentos
        current_pos = [start[0], start[1]]
        dash_length = 10
        gap_length = 5
        
        while True:
            # Punto final del siguiente segmento
            next_pos = [
                current_pos[0] + dx * dash_length,
                current_pos[1] + dy * dash_length
            ]
            
            # Verificar si llegamos al final
            remaining_dist = math.sqrt(
                (end[0] - current_pos[0])**2 + (end[1] - current_pos[1])**2
            )
            
            if remaining_dist <= dash_length:
                pygame.draw.line(self.screen, color, current_pos, end, width)
                break
            
            # Dibujar segmento
            pygame.draw.line(self.screen, color, current_pos, next_pos, width)
            
            # Mover al siguiente punto (después del gap)
            current_pos[0] += dx * (dash_length + gap_length)
            current_pos[1] += dy * (dash_length + gap_length)
    
    def draw_infection_flow(self, start, end):
        """Dibuja puntos animados que representan el flujo de infecciones"""
        import time
        
        # Usar tiempo para animar
        t = (time.time() * 2) % 1.0  # Ciclo de 0.5 segundos
        
        # Interpolar posición
        flow_x = start[0] + (end[0] - start[0]) * t
        flow_y = start[1] + (end[1] - start[1]) * t
        
        # Dibujar punto de infección
        pygame.draw.circle(self.screen, (255, 0, 0), (int(flow_x), int(flow_y)), 3)
    
    def draw_legend(self):
        """Dibuja la leyenda del mapa"""
        legend_x = 50
        legend_y = 600
        
        # Fondo de la leyenda
        legend_bg = pygame.Rect(legend_x - 10, legend_y - 10, 300, 150)
        pygame.draw.rect(self.screen, (20, 20, 40), legend_bg)
        pygame.draw.rect(self.screen, (100, 100, 100), legend_bg, 2)
        
        # Título
        title_text = self.font.render("Leyenda", True, (255, 255, 255))
        self.screen.blit(title_text, (legend_x, legend_y))
        
        # Colores de infección
        legend_items = [
            ((0, 150, 0), "Muy bajo (< 0.1%)"),
            ((100, 200, 0), "Bajo (0.1% - 0.5%)"),
            ((200, 200, 0), "Moderado (0.5% - 1%)"),
            ((255, 150, 0), "Alto (1% - 3%)"),
            ((255, 100, 50), "Muy alto (3% - 5%)"),
            ((200, 0, 0), "Crítico (> 5%)")
        ]
        
        y_offset = legend_y + 30
        for color, description in legend_items:
            # Cuadrado de color
            color_rect = pygame.Rect(legend_x, y_offset, 15, 15)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 1)
            
            # Descripción
            desc_text = self.font_small.render(description, True, (200, 200, 200))
            self.screen.blit(desc_text, (legend_x + 25, y_offset))
            
            y_offset += 20
    
    def draw_ocean_background(self):
        """Dibuja el fondo del océano"""
        # Gradiente azul para simular océano
        for y in range(0, self.screen_height, 4):
            blue_intensity = 30 + (y / self.screen_height) * 20
            color = (0, 0, int(blue_intensity))
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y), 4)
    
    def get_continent_at_position(self, pos):
        """Devuelve el índice del continente en la posición dada"""
        x, y = pos
        
        for continent_idx, region in self.continent_regions.items():
            # Verificación simple usando distancia al centro
            center_x, center_y = region['center']
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # Radio aproximado para cada continente
            if distance < 120:  # Radio de detección
                return continent_idx
        
        return None
    
    def draw(self, continents, selected_continent=None):
        """Dibuja el mapa completo"""
        # Fondo del océano
        self.draw_ocean_background()
        
        # Dibujar conexiones aéreas primero (para que estén detrás)
        self.draw_flight_connections(continents)
        
        # Dibujar continentes
        for i, continent in enumerate(continents):
            selected = (selected_continent == i)
            self.draw_continent(i, continent, selected)
        
        # Dibujar aeropuertos encima
        self.draw_airports(continents)
        
        # Leyenda
        self.draw_legend()
        
        # Título del mapa
        title_text = pygame.font.Font(None, 36).render("Situación Global de la Pandemia", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 30))
        
        # Fondo para el título
        title_bg = pygame.Surface((title_rect.width + 20, title_rect.height + 8))
        title_bg.set_alpha(200)
        title_bg.fill((0, 0, 0))
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        self.screen.blit(title_bg, title_bg_rect)
        self.screen.blit(title_text, title_rect)