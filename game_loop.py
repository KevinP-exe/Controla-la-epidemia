import pygame
from seir import Continent, SEIRSimulator
from ui import GameUI, ConfirmDialog
from map import WorldMap
from events import EventManager, EventUI
from decisions import DecisionManager, DecisionUI

class GameOverScreen:
    def __init__(self, screen, game_state, stats, day, defeat_reason=None):
        self.screen = screen
        self.game_state = game_state
        self.stats = stats
        self.day = day
        self.defeat_reason = defeat_reason
        
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Animación
        self.animation_time = 0
        self.particles = []
        
        # Generar partículas de celebración o lamentación
        self.generate_particles()
    
    def generate_particles(self):
        """Genera partículas para el fondo animado"""
        import random
        
        if self.game_state == "victory":
            colors = [(255, 215, 0), (0, 255, 127), (30, 144, 255), (255, 105, 180)]
        else:
            colors = [(139, 69, 19), (105, 105, 105), (128, 128, 128), (169, 169, 169)]
        
        for _ in range(50):
            particle = {
                'x': random.randint(0, self.screen.get_width()),
                'y': random.randint(0, self.screen.get_height()),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-2, 0) if self.game_state == "victory" else random.uniform(-0.5, 0.5),
                'color': random.choice(colors),
                'size': random.randint(2, 6),
                'life': random.uniform(3, 6)
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Actualiza la animación"""
        self.animation_time += dt
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * 60 * dt
            particle['y'] += particle['vy'] * 60 * dt
            particle['life'] -= dt
            
            # Envolver partículas
            if particle['x'] < 0:
                particle['x'] = self.screen.get_width()
            elif particle['x'] > self.screen.get_width():
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = self.screen.get_height()
            elif particle['y'] > self.screen.get_height():
                particle['y'] = 0
            
            # Remover partículas muertas
            if particle['life'] <= 0:
                self.particles.remove(particle)
                # Generar nueva partícula
                import random
                colors = [(255, 215, 0), (0, 255, 127), (30, 144, 255)] if self.game_state == "victory" else [(139, 69, 19), (105, 105, 105)]
                new_particle = {
                    'x': random.randint(0, self.screen.get_width()),
                    'y': self.screen.get_height(),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-2, 0) if self.game_state == "victory" else random.uniform(-0.5, 0.5),
                    'color': random.choice(colors),
                    'size': random.randint(2, 6),
                    'life': random.uniform(3, 6)
                }
                self.particles.append(new_particle)
    
    def draw(self):
        """Dibuja la pantalla de fin de juego"""
        # Fondo animado
        self.draw_animated_background()
        
        if self.game_state == "victory":
            self.draw_victory_screen()
        else:
            self.draw_defeat_screen()
        
        # Instrucciones
        instruction_text = "Presiona cualquier tecla o click para volver al menú principal"
        instruction_surface = self.font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(self.screen.get_width() // 2, 
                                                               self.screen.get_height() - 30))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_animated_background(self):
        """Dibuja fondo animado con partículas"""
        if self.game_state == "victory":
            # Fondo de victoria con gradiente dorado
            for y in range(0, self.screen.get_height(), 4):
                progress = y / self.screen.get_height()
                gold_intensity = int(50 + progress * 30)
                color = (gold_intensity, gold_intensity//2, 20)
                pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y), 4)
        else:
            # Fondo de derrota con gradiente sombrío
            for y in range(0, self.screen.get_height(), 4):
                progress = y / self.screen.get_height()
                dark_intensity = int(20 + progress * 15)
                color = (dark_intensity, dark_intensity//2, dark_intensity//3)
                pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y), 4)
        
        # Dibujar partículas
        for particle in self.particles:
            alpha = max(50, min(255, int(particle['life'] * 85)))
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            color_with_alpha = (*particle['color'], alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                             (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def draw_victory_screen(self):
        """Dibuja pantalla de victoria"""
        import math
        
        # Título animado
        scale = 1.0 + 0.1 * math.sin(self.animation_time * 2)
        title_text = "¡VICTORIA!"
        
        # Crear superficie escalada para el título
        base_title = self.font_huge.render(title_text, True, (255, 215, 0))
        scaled_width = int(base_title.get_width() * scale)
        scaled_height = int(base_title.get_height() * scale)
        scaled_title = pygame.transform.scale(base_title, (scaled_width, scaled_height))
        
        title_rect = scaled_title.get_rect(center=(self.screen.get_width() // 2, 150))
        
        # Sombra del título
        shadow_title = self.font_huge.render(title_text, True, (100, 80, 0))
        shadow_scaled = pygame.transform.scale(shadow_title, (scaled_width, scaled_height))
        shadow_rect = shadow_scaled.get_rect(center=(title_rect.centerx + 4, title_rect.centery + 4))
        self.screen.blit(shadow_scaled, shadow_rect)
        self.screen.blit(scaled_title, title_rect)
        
        # Subtítulo
        subtitle_text = "Has controlado exitosamente la pandemia"
        subtitle_surface = self.font_large.render(subtitle_text, True, (200, 255, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen.get_width() // 2, 220))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Logros
        self.draw_achievements()
        
        # Estadísticas finales
        self.draw_final_stats(victory=True)
    
    def draw_defeat_screen(self):
        """Dibuja pantalla de derrota"""
        # Título
        title_text = "DERROTA"
        title_surface = self.font_huge.render(title_text, True, (220, 50, 50))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 150))
        
        # Sombra del título
        shadow_title = self.font_huge.render(title_text, True, (80, 20, 20))
        shadow_rect = shadow_title.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
        self.screen.blit(shadow_title, shadow_rect)
        self.screen.blit(title_surface, title_rect)
        
        # Razón de la derrota
        defeat_messages = {
            "too_many_deaths": "La pandemia causó demasiadas víctimas",
            "economic_collapse": "El colapso económico fue inevitable", 
            "morale_collapse": "La sociedad perdió toda esperanza",
            "uncontrolled_spread": "El virus se propagó sin control",
            "time_limit": "Se agotó el tiempo para controlar la crisis"
        }
        
        reason_text = defeat_messages.get(self.defeat_reason, "La pandemia no pudo ser controlada")
        reason_surface = self.font_large.render(reason_text, True, (255, 150, 150))
        reason_rect = reason_surface.get_rect(center=(self.screen.get_width() // 2, 220))
        self.screen.blit(reason_surface, reason_rect)
        
        # Estadísticas finales
        self.draw_final_stats(victory=False)
        
        # Consejos para mejorar
        self.draw_improvement_tips()
    
    def draw_achievements(self):
        """Dibuja logros obtenidos en caso de victoria"""
        achievements = []
        
        # Determinar logros basados en estadísticas
        death_rate = self.stats['deaths'] / self.stats['total_population']
        
        if death_rate < 0.001:
            achievements.append("🏆 Héroe Mundial - Menos del 0.1% de muertes")
        elif death_rate < 0.01:
            achievements.append("🥇 Líder Excepcional - Menos del 1% de muertes")
        elif death_rate < 0.02:
            achievements.append("🥈 Buen Líder - Menos del 2% de muertes")
        
        if self.stats['economy'] > 80:
            achievements.append("💰 Economía Sólida - Mantuvo economía fuerte")
        
        if self.stats['morale'] > 70:
            achievements.append("❤️ Esperanza del Pueblo - Mantuvo alta moral")
        
        if self.day < 100:
            achievements.append("⚡ Respuesta Rápida - Control en menos de 100 días")
        
        if not achievements:
            achievements.append("🌟 Crisis Superada - Controlaste la pandemia")
        
        # Dibujar logros
        y_offset = 280
        for achievement in achievements:
            achievement_surface = self.font_medium.render(achievement, True, (255, 215, 0))
            achievement_rect = achievement_surface.get_rect(center=(self.screen.get_width() // 2, y_offset))
            
            # Fondo para el logro
            bg_rect = pygame.Rect(achievement_rect.x - 10, achievement_rect.y - 5,
                                achievement_rect.width + 20, achievement_rect.height + 10)
            pygame.draw.rect(self.screen, (50, 50, 20), bg_rect)
            pygame.draw.rect(self.screen, (200, 200, 0), bg_rect, 2)
            
            self.screen.blit(achievement_surface, achievement_rect)
            y_offset += 50
    
    def draw_final_stats(self, victory=True):
        """Dibuja estadísticas finales"""
        stats_y = 400 if victory else 280
        
        # Panel de estadísticas
        panel_width = 600
        panel_height = 200
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_rect = pygame.Rect(panel_x, stats_y, panel_width, panel_height)
        
        bg_color = (30, 60, 30) if victory else (60, 30, 30)
        border_color = (100, 200, 100) if victory else (200, 100, 100)
        
        pygame.draw.rect(self.screen, bg_color, panel_rect)
        pygame.draw.rect(self.screen, border_color, panel_rect, 3)
        
        # Título del panel
        panel_title = "Resumen Final"
        title_surface = self.font_large.render(panel_title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 25))
        self.screen.blit(title_surface, title_rect)
        
        # Estadísticas
        death_rate = (self.stats['deaths'] / self.stats['total_population']) * 100
        final_stats = [
            f"Duración de la crisis: {self.day} días",
            f"Población mundial: {self.stats['total_population']:,}",
            f"Total de muertes: {self.stats['deaths']:,} ({death_rate:.2f}%)",
            f"Infectados finales: {self.stats['infected']:,}",
            f"Recuperados: {self.stats['recovered']:,}",
            f"Estado económico final: {self.stats['economy']:.1f}%",
            f"Moral final de la población: {self.stats['morale']:.1f}%"
        ]
        
        y_offset = stats_y + 60
        for i, stat in enumerate(final_stats):
            # Color según tipo de estadística
            if "muertes" in stat.lower():
                color = (255, 150, 150) if death_rate > 1 else (255, 255, 150)
            elif "económico" in stat.lower():
                color = (150, 255, 150) if self.stats['economy'] > 50 else (255, 150, 150)
            elif "moral" in stat.lower():
                color = (150, 255, 150) if self.stats['morale'] > 50 else (255, 150, 150)
            else:
                color = (255, 255, 255)
            
            stat_surface = self.font_small.render(stat, True, color)
            stat_rect = stat_surface.get_rect(center=(panel_rect.centerx, y_offset))
            self.screen.blit(stat_surface, stat_rect)
            y_offset += 22
    
    def draw_improvement_tips(self):
        """Dibuja consejos para mejorar en caso de derrota"""
        tips_y = 500
        
        # Panel de consejos
        panel_width = 700
        panel_height = 180
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_rect = pygame.Rect(panel_x, tips_y, panel_width, panel_height)
        
        pygame.draw.rect(self.screen, (40, 40, 20), panel_rect)
        pygame.draw.rect(self.screen, (150, 150, 100), panel_rect, 2)
        
        # Título
        title_surface = self.font_medium.render("Consejos para la próxima partida:", True, (255, 255, 150))
        title_rect = title_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 25))
        self.screen.blit(title_surface, title_rect)
        
        # Consejos específicos según razón de derrota
        tips = self.get_specific_tips()
        
        y_offset = tips_y + 50
        for tip in tips:
            tip_surface = self.font_small.render(tip, True, (200, 200, 200))
            tip_rect = tip_surface.get_rect(center=(panel_rect.centerx, y_offset))
            self.screen.blit(tip_surface, tip_rect)
            y_offset += 25
    
    def get_specific_tips(self):
        """Devuelve consejos específicos según la razón de derrota"""
        base_tips = [
            "• Actúa rápidamente al detectar los primeros casos",
            "• Balancea las medidas de salud pública con la economía",
            "• Invierte en hospitales antes de que sea demasiado tarde",
            "• Usa campañas de comunicación para mantener la moral",
            "• No uses todas las decisiones el mismo día, planifica"
        ]
        
        if self.defeat_reason == "too_many_deaths":
            specific_tips = [
                "• Implementa cuarentenas tempranas cuando sea necesario",
                "• Cierra aeropuertos para prevenir propagación internacional",
                "• Aumenta la capacidad hospitalaria rápidamente"
            ]
        elif self.defeat_reason == "economic_collapse":
            specific_tips = [
                "• Evita medidas demasiado restrictivas por mucho tiempo",
                "• Usa estímulos económicos cuando la economía baje",
                "• Balancea la protección de salud con la actividad económica"
            ]
        elif self.defeat_reason == "morale_collapse":
            specific_tips = [
                "• Implementa campañas de comunicación frecuentemente",
                "• Evita restricciones excesivas que frustren a la población",
                "• Proporciona apoyo de salud mental cuando sea necesario"
            ]
        else:
            specific_tips = [
                "• Estudia los patrones de propagación del virus",
                "• Adapta tu estrategia según evolucione la situación",
                "• Recuerda que tienes límite de decisiones por día"
            ]
        
        return base_tips[:3] + specific_tips[:2]

class GameLoop:
    def __init__(self, screen, difficulty="normal"):
        self.screen = screen
        self.difficulty = difficulty
        self.day = 1
        
        # Inicializar componentes del juego
        self.setup_continents()
        self.simulator = SEIRSimulator(self.continents, difficulty)
        self.event_manager = EventManager(difficulty)
        self.decision_manager = DecisionManager(difficulty)
        
        # Interfaz de usuario mejorada
        self.ui = GameUI(screen)
        self.map = WorldMap(screen)
        self.event_ui = EventUI(screen)
        self.decision_ui = DecisionUI(screen)
        
        # Estado del juego
        self.game_state = "playing"  # "playing", "victory", "defeat"
        self.defeat_reason = None
        self.selected_continent = None
        self.game_over_screen = None
        
        # Historial para estadísticas
        self.history = []
        self.paused = False
        
        # Límites de tiempo para partida
        self.max_days = 365  # Máximo un año
        
        # Guardar estado inicial
        self.save_daily_stats()
        
        # Actualizar decisiones iniciales
        self.update_available_decisions()
    
    def setup_continents(self):
        """Configura los continentes iniciales"""
        continent_configs = {
            "easy": [
                {"name": "América", "population": 800000, "initial_infected": 100},
                {"name": "Europa-África", "population": 1500000, "initial_infected": 120},
                {"name": "Asia-Oceanía", "population": 3500000, "initial_infected": 150}
            ],
            "normal": [
                {"name": "América", "population": 1000000, "initial_infected": 150},
                {"name": "Europa-África", "population": 1800000, "initial_infected": 200},
                {"name": "Asia-Oceanía", "population": 4500000, "initial_infected": 300}
            ],
            "expert": [
                {"name": "América", "population": 1200000, "initial_infected": 250},
                {"name": "Europa-África", "population": 2200000, "initial_infected": 350},
                {"name": "Asia-Oceanía", "population": 5500000, "initial_infected": 500}
            ]
        }
        
        continent_data = continent_configs[self.difficulty]
        
        self.continents = []
        for data in continent_data:
            continent = Continent(
                name=data["name"],
                population=data["population"],
                initial_infected=data["initial_infected"],
                difficulty=self.difficulty
            )
            self.continents.append(continent)
    
    def update_available_decisions(self):
        """Actualiza las decisiones disponibles"""
        available_decisions = self.decision_manager.get_available_decisions(
            self.day, self.continents, self.simulator.get_global_stats()
        )
        self.decision_ui.update_decisions(
            available_decisions, 
            self.decision_manager.decisions_used_today,
            self.decision_manager.max_decisions_per_day
        )
    
    def handle_event(self, event):
        """Maneja eventos del juego"""
        if self.game_state != "playing":
            return self.handle_game_over_events(event)
        
        # Eventos de UI principal
        ui_result = self.ui.handle_event(event)
        if ui_result == "next_day":
            self.advance_day()
        elif ui_result == "menu":
            return "menu"
        elif ui_result == "toggle_stats":
            # Deshabilitar otros botones cuando se muestran estadísticas
            self.ui.set_buttons_enabled(not self.ui.stats_panel_visible)
        
        # Solo permitir otros eventos si las estadísticas no están visibles
        if not self.ui.stats_panel_visible:
            # Eventos de decisiones
            decision_result = self.decision_ui.handle_event(event)
            if decision_result:
                if decision_result['action'] == 'apply_decision':
                    success = self.apply_decision(
                        decision_result['decision_id'],
                        decision_result.get('continent_idx')
                    )
                    if success:
                        # Actualizar botón de siguiente día
                        can_continue = (self.decision_manager.decisions_used_today > 0 or 
                                      not self.decision_manager.get_available_decisions(
                                          self.day, self.continents, self.simulator.get_global_stats()))
                        self.ui.next_day_button.set_enabled(can_continue)
            
            # Click en mapa para seleccionar continente
            if event.type == pygame.MOUSEBUTTONUP:
                continent_idx = self.map.get_continent_at_position(event.pos)
                if continent_idx is not None:
                    self.selected_continent = continent_idx
            
            # Teclas de control
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.advance_day()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
        
        return None
    
    def handle_game_over_events(self, event):
        """Maneja eventos cuando el juego ha terminado"""
        if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONUP]:
            return "menu"
        return None
    
    def advance_day(self):
        """Avanza un día en la simulación"""
        if self.game_state != "playing" or self.paused:
            return
        
        # Ejecutar simulación
        self.simulator.step()
        
        # Verificar y procesar eventos aleatorios
        events = self.event_manager.check_events(self.day, self.continents, 
                                                self.simulator.get_global_stats())
        
        # Añadir notificaciones de eventos
        for event in events:
            self.event_ui.add_event_notification(event)
        
        # Avanzar día y reiniciar contador de decisiones
        self.day += 1
        self.decision_manager.new_day(self.day)
        
        # Actualizar decisiones disponibles
        self.update_available_decisions()
        
        # Habilitar botón de siguiente día si hay decisiones o no se pueden tomar más
        self.ui.next_day_button.set_enabled(True)
        
        # Guardar estadísticas del día
        self.save_daily_stats()
        
        # Verificar condiciones de fin de juego
        self.check_game_over()
    
    def apply_decision(self, decision_id, continent_idx=None):
        """Aplica una decisión política"""
        success = self.decision_manager.apply_decision(
            decision_id, self.continents, continent_idx
        )
        
        if success:
            # Actualizar decisiones disponibles
            self.update_available_decisions()
        
        return success
    
    def save_daily_stats(self):
        """Guarda las estadísticas del día actual"""
        global_stats = self.simulator.get_global_stats()
        
        day_data = {
            'day': self.day,
            'global': global_stats,
            'continents': []
        }
        
        for continent in self.continents:
            continent_data = {
                'name': continent.name,
                'susceptible': int(continent.S),
                'exposed': int(continent.E),
                'infected': int(continent.I),
                'recovered': int(continent.R),
                'deaths': int(continent.deaths),
                'economy': continent.economy,
                'morale': continent.morale
            }
            day_data['continents'].append(continent_data)
        
        self.history.append(day_data)
        
        # Regenerar gráficos si las estadísticas están visibles
        if self.ui.stats_panel_visible:
            self.ui.stats_surface = None
    
    def check_game_over(self):
        """Verifica las condiciones de fin de juego"""
        global_stats = self.simulator.get_global_stats()
        
        # Verificar victoria - epidemia controlada
        if self.check_victory_conditions():
            self.game_state = "victory"
            self.game_over_screen = GameOverScreen(
                self.screen, "victory", global_stats, self.day
            )
            return
        
        # Verificar derrota
        defeat_reason = self.check_defeat_conditions()
        if defeat_reason:
            self.game_state = "defeat"
            self.defeat_reason = defeat_reason
            self.game_over_screen = GameOverScreen(
                self.screen, "defeat", global_stats, self.day, defeat_reason
            )
            return
    
    def check_victory_conditions(self):
        """Verifica las condiciones de victoria"""
        global_stats = self.simulator.get_global_stats()
        
        # Condición 1: Muy pocos infectados activos
        if global_stats['infected'] < global_stats['total_population'] * 0.0001:  # 0.01%
            # Condición 2: Economía y moral en niveles aceptables
            if global_stats['economy'] >= 40 and global_stats['morale'] >= 35:
                # Condición 3: La situación ha sido estable por varios días
                if self.day > 30 and len(self.history) >= 7:
                    recent_infections = [day['global']['infected'] for day in self.history[-7:]]
                    if all(infections < global_stats['total_population'] * 0.001 for infections in recent_infections):
                        return True
        
        # Victoria alternativa: control prolongado con bajas cifras
        if self.day > 100:
            if (global_stats['infected'] < global_stats['total_population'] * 0.002 and
                global_stats['economy'] >= 30 and global_stats['morale'] >= 25):
                return True
        
        return False
    
    def check_defeat_conditions(self):
        """Verifica las condiciones de derrota"""
        global_stats = self.simulator.get_global_stats()
        
        # Derrota 1: Demasiadas muertes
        death_rate = global_stats['deaths'] / global_stats['total_population']
        if death_rate > 0.15:  # 15% de la población
            return "too_many_deaths"
        
        # Derrota 2: Colapso económico total
        if global_stats['economy'] <= 5:
            return "economic_collapse"
        
        # Derrota 3: Colapso de moral total
        if global_stats['morale'] <= 5:
            return "morale_collapse"
        
        # Derrota 4: Propagación incontrolable
        infection_rate = global_stats['infected'] / global_stats['total_population']
        if infection_rate > 0.5:  # 50% de la población infectada simultáneamente
            return "uncontrolled_spread"
        
        # Derrota 5: Límite de tiempo
        if self.day > self.max_days:
            return "time_limit"
        
        # Derrota 6: Situación crítica sostenida
        if self.day > 50 and len(self.history) >= 30:
            recent_stats = self.history[-30:]
            critical_days = sum(1 for day in recent_stats 
                              if (day['global']['economy'] < 20 or 
                                  day['global']['morale'] < 20 or
                                  day['global']['infected'] / day['global']['total_population'] > 0.2))
            if critical_days >= 25:  # 25 de los últimos 30 días en situación crítica
                return "uncontrolled_spread"
        
        return None
    
    def update(self):
        """Actualiza el estado del juego"""
        if self.game_state == "playing":
            # Actualizar notificaciones de eventos
            self.event_ui.update()
            
            # Actualizar mapa (animaciones)
            dt = 1.0 / 60.0  # Asumir 60 FPS
            self.map.update(dt, self.continents)
        
        elif self.game_over_screen:
            dt = 1.0 / 60.0
            self.game_over_screen.update(dt)
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        self.screen.fill((10, 10, 30))
        
        if self.game_state == "playing":
            self.draw_playing_state()
        elif self.game_over_screen:
            self.game_over_screen.draw()
    
    def draw_playing_state(self):
        """Dibuja el estado de juego normal"""
        # Mapa mundial (área definida)
        self.map.draw(self.continents, self.selected_continent)
        
        # Interfaz principal
        global_stats = self.simulator.get_global_stats()
        self.ui.draw(self.day, global_stats, self.continents, self.history)
        
        # Interfaz de decisiones (área definida)
        self.decision_ui.draw()
        
        # Notificaciones de eventos
        self.event_ui.draw_event_notifications()
        
        # Panel de eventos recientes (área definida)
        recent_events = self.event_manager.get_recent_events()
        if recent_events:
            self.event_ui.draw_events_history(recent_events, 930, 200, 260, 450)
        
        # Indicador de progreso de la partida
        self.draw_progress_indicator()
        
        # Indicador de pausa
        if self.paused:
            self.draw_pause_indicator()
    
    def draw_progress_indicator(self):
        """Dibuja indicador de progreso de la partida"""
        progress_rect = pygame.Rect(520, 680, 400, 20)
        
        # Fondo
        pygame.draw.rect(self.screen, (50, 50, 50), progress_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), progress_rect, 2)
        
        # Barra de progreso
        progress = min(1.0, self.day / self.max_days)
        fill_width = int(progress_rect.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, progress_rect.height)
            
            # Color según progreso
            if progress < 0.5:
                color = (100, 200, 100)  # Verde
            elif progress < 0.8:
                color = (200, 200, 100)  # Amarillo
            else:
                color = (200, 100, 100)  # Rojo
            
            pygame.draw.rect(self.screen, color, fill_rect)
        
        # Texto de progreso
        progress_text = f"Día {self.day} / {self.max_days}"
        text_surface = pygame.font.Font(None, 18).render(progress_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=progress_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_pause_indicator(self):
        """Dibuja el indicador de pausa"""
        pause_text = pygame.font.Font(None, 48).render("PAUSADO", True, (255, 255, 100))
        pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 100))
        
        # Fondo semi-transparente
        bg_surface = pygame.Surface((pause_rect.width + 20, pause_rect.height + 10))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 0))
        bg_rect = bg_surface.get_rect(center=pause_rect.center)
        self.screen.blit(bg_surface, bg_rect)
        
        self.screen.blit(pause_text, pause_rect)