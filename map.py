import pygame
import math
import time
import random

class InfectionParticle:
    def __init__(self, start_pos, end_pos, infection_level):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.progress = 0.0
        self.speed = random.uniform(0.008, 0.015)  # Velocidad aleatoria
        self.infection_level = infection_level
        self.size = random.uniform(2, 4)
        self.life_time = random.uniform(1.0, 2.0)
        self.age = 0.0
        self.active = True
    
    def update(self, dt):
        if not self.active:
            return
        
        self.age += dt
        self.progress += self.speed * dt
        
        if self.progress >= 1.0 or self.age >= self.life_time:
            self.active = False
            return
        
        # Interpolación con curva suave
        t = self.progress
        smooth_t = t * t * (3.0 - 2.0 * t)  # Suavizado suave
        
        self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * smooth_t
        self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * smooth_t
        
        # Pequeña oscilación vertical
        oscillation = math.sin(self.progress * math.pi * 4) * 5
        self.current_pos[1] += oscillation
    
    def draw(self, screen):
        if not self.active:
            return
        
        # Alpha basado en la edad
        alpha = max(0, min(255, int(255 * (1.0 - self.age / self.life_time))))
        
        # Color basado en nivel de infección
        if self.infection_level < 0.01:
            color = (255, 255, 0, alpha)  # Amarillo para bajo
        elif self.infection_level < 0.05:
            color = (255, 150, 0, alpha)  # Naranja para medio
        else:
            color = (255, 50, 50, alpha)  # Rojo para alto
        
        # Crear superficie con alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (self.size, self.size), self.size)
        
        # Efecto de brillo
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        glow_color = (*color[:3], alpha // 3)
        pygame.draw.circle(glow_surface, glow_color, (self.size * 2, self.size * 2), self.size * 2)
        
        screen.blit(glow_surface, (self.current_pos[0] - self.size * 2, self.current_pos[1] - self.size * 2))
        screen.blit(particle_surface, (self.current_pos[0] - self.size, self.current_pos[1] - self.size))

class WorldMap:
    def __init__(self, screen):
        self.screen = screen  
        self.map_rect = pygame.Rect(10, 200, 500, 400)  
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_title = pygame.font.Font(None, 24)
        
        # Inicializar listas vacías
        self.infection_particles = []
        self.airports = {}
        self.flight_connections = []
        self.continent_colors = [None, None, None]
        self.target_colors = [None, None, None]
        self.warning_continents = set()
        self.pulse_time = 0
        self.last_particle_time = time.time()
        self.color_transition_speed = 2.0

        # --- INICIALIZACIÓN DE REGIONES, AEROPUERTOS Y CONEXIONES ---
        map_x, map_y = self.map_rect.x, self.map_rect.y
        map_w, map_h = self.map_rect.width, self.map_rect.height

        self.continent_regions = {
            0: {  # América
                'name': 'América',
                'center': (map_x + int(map_w * 0.25), map_y + int(map_h * 0.5)),
                'points': [
                    (map_x + int(map_w * 0.1), map_y + int(map_h * 0.2)),
                    (map_x + int(map_w * 0.15), map_y + int(map_h * 0.15)),
                    (map_x + int(map_w * 0.25), map_y + int(map_h * 0.18)),
                    (map_x + int(map_w * 0.32), map_y + int(map_h * 0.25)),
                    (map_x + int(map_w * 0.38), map_y + int(map_h * 0.45)),
                    (map_x + int(map_w * 0.35), map_y + int(map_h * 0.75)),
                    (map_x + int(map_w * 0.30), map_y + int(map_h * 0.85)),
                    (map_x + int(map_w * 0.20), map_y + int(map_h * 0.88)),
                    (map_x + int(map_w * 0.12), map_y + int(map_h * 0.85)),
                    (map_x + int(map_w * 0.08), map_y + int(map_h * 0.65)),
                    (map_x + int(map_w * 0.06), map_y + int(map_h * 0.35)),
                ]
            },
            1: {  # Europa-África
                'name': 'Europa-África',
                'center': (map_x + int(map_w * 0.55), map_y + int(map_h * 0.5)),
                'points': [
                    (map_x + int(map_w * 0.45), map_y + int(map_h * 0.18)),
                    (map_x + int(map_w * 0.60), map_y + int(map_h * 0.12)),
                    (map_x + int(map_w * 0.68), map_y + int(map_h * 0.15)),
                    (map_x + int(map_w * 0.72), map_y + int(map_h * 0.25)),
                    (map_x + int(map_w * 0.75), map_y + int(map_h * 0.45)),
                    (map_x + int(map_w * 0.72), map_y + int(map_h * 0.75)),
                    (map_x + int(map_w * 0.65), map_y + int(map_h * 0.88)),
                    (map_x + int(map_w * 0.52), map_y + int(map_h * 0.85)),
                    (map_x + int(map_w * 0.42), map_y + int(map_h * 0.75)),
                    (map_x + int(map_w * 0.40), map_y + int(map_h * 0.45)),
                ]
            },
            2: {  # Asia-Oceanía
                'name': 'Asia-Oceanía',
                'center': (map_x + int(map_w * 0.85), map_y + int(map_h * 0.45)),
                'points': [
                    (map_x + int(map_w * 0.78), map_y + int(map_h * 0.12)),
                    (map_x + int(map_w * 0.92), map_y + int(map_h * 0.10)),
                    (map_x + int(map_w * 0.98), map_y + int(map_h * 0.18)),
                    (map_x + int(map_w * 0.96), map_y + int(map_h * 0.35)),
                    (map_x + int(map_w * 0.98), map_y + int(map_h * 0.55)),
                    (map_x + int(map_w * 0.94), map_y + int(map_h * 0.75)),
                    (map_x + int(map_w * 0.88), map_y + int(map_h * 0.82)),
                    (map_x + int(map_w * 0.82), map_y + int(map_h * 0.78)),
                    (map_x + int(map_w * 0.78), map_y + int(map_h * 0.55)),
                    (map_x + int(map_w * 0.76), map_y + int(map_h * 0.28)),
                ]
            }
        }

        self.airports = {
            0: (map_x + int(map_w * 0.28), map_y + int(map_h * 0.45)),
            1: (map_x + int(map_w * 0.58), map_y + int(map_h * 0.42)),
            2: (map_x + int(map_w * 0.88), map_y + int(map_h * 0.38))
        }

        self.flight_connections = [(0, 1), (1, 2), (0, 2)]
        # ----------------------------------------------------------

        # El resto de tu inicialización...

    def draw_selection_info(self, selected_continent):
        # Ya NO inicialices self.continent_regions, self.airports ni self.flight_connections aquí.
        # Solo usa los datos ya inicializados en __init__.

        # Ejemplo de uso:
        if selected_continent is not None:
            region = self.continent_regions[selected_continent]
            # ...resto del código para mostrar información de la región...
        # ...resto del método...

    def update(self, dt, continents):
        # Actualiza todas las partículas de infección activas
        for particle in self.infection_particles:
            particle.update(dt)
        # Elimina las partículas que ya no están activas
        self.infection_particles = [p for p in self.infection_particles if p.active]

    def draw(self, continents, selected_continent):
        # Dibuja el mapa base
        pygame.draw.rect(self.screen, (40, 60, 100), self.map_rect, border_radius=20)

        # Dibuja las regiones de los continentes
        for idx, region in self.continent_regions.items():
            color = (100, 180, 220) if idx != selected_continent else (255, 220, 100)
            pygame.draw.polygon(self.screen, color, region['points'])
            # Puedes agregar más detalles aquí

        # Dibuja los aeropuertos
        for idx, pos in self.airports.items():
            pygame.draw.circle(self.screen, (200, 200, 200), pos, 8)

        # Dibuja las conexiones de vuelo
        for a, b in self.flight_connections:
            pygame.draw.line(self.screen, (180, 180, 180), self.airports[a], self.airports[b], 3)

        # Dibuja partículas de infección
        for particle in self.infection_particles:
            particle.draw(self.screen)

        # Dibuja información de selección
        self.draw_selection_info(selected_continent)

    def get_continent_at_position(self, pos):
        """Devuelve el índice del continente bajo la posición dada, o None si no hay ninguno."""
        for idx, region in self.continent_regions.items():
            polygon = region['points']
            if self._point_in_polygon(pos, polygon):
                return idx
        return None

    def _point_in_polygon(self, point, polygon):
        """Algoritmo de ray casting para saber si un punto está dentro de un polígono."""
        x, y = point
        inside = False
        n = len(polygon)
        px1, py1 = polygon[0]
        for i in range(n + 1):
            px2, py2 = polygon[i % n]
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1 + 1e-12) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2
        return inside