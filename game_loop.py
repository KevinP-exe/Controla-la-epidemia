import pygame
from seir import Continent, SEIRSimulator
from ui import GameUI
from map import WorldMap
from events import EventManager, EventUI
from decisions import DecisionManager, DecisionUI

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
        
        # Interfaz de usuario
        self.ui = GameUI(screen)
        self.map = WorldMap(screen)
        self.event_ui = EventUI(screen)
        self.decision_ui = DecisionUI(screen)
        
        # Estado del juego
        self.game_state = "playing"  # "playing", "victory", "defeat"
        self.defeat_reason = None
        self.selected_continent = None
        
        # Historial para estadísticas
        self.history = []
        self.paused = False
        
        # Control de velocidad
        self.simulation_speed = 1  # Días por segundo
        self.last_simulation_time = pygame.time.get_ticks()
        
        # Guardar estado inicial
        self.save_daily_stats()
    
    def setup_continents(self):
        """Configura los continentes iniciales"""
        continent_data = [
            {"name": "América", "population": 1000000, "initial_infected": 150},
            {"name": "Europa-África", "population": 1800000, "initial_infected": 200},
            {"name": "Asia-Oceanía", "population": 4500000, "initial_infected": 300}
        ]
        
        self.continents = []
        for data in continent_data:
            continent = Continent(
                name=data["name"],
                population=data["population"],
                initial_infected=data["initial_infected"],
                difficulty=self.difficulty
            )
            self.continents.append(continent)
    
    def handle_event(self, event):
        """Maneja eventos del juego"""
        if self.game_state != "playing":
            return self.handle_game_over_events(event)
        
        # Eventos de UI principal
        ui_action = self.ui.handle_event(event)
        if ui_action == "next_day":
            self.advance_day()
        elif ui_action == "menu":
            return "menu"
        elif ui_action == "toggle_stats":
            pass  # Manejado por el UI
        
        # Eventos de decisiones
        decision_action = self.decision_ui.handle_event(event)
        if decision_action:
            if decision_action['action'] == 'apply_decision':
                self.apply_decision(
                    decision_action['decision_id'],
                    decision_action.get('continent_idx')
                )
        
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
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        
        return None
    
    def handle_game_over_events(self, event):
        """Maneja eventos cuando el juego ha terminado"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "menu"
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        
        if event.type == pygame.MOUSEBUTTONUP:
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
        
        # Generar nuevas decisiones disponibles
        available_decisions = self.decision_manager.get_available_decisions(
            self.day, self.continents, self.simulator.get_global_stats()
        )
        self.decision_ui.update_decisions(available_decisions)
        
        # Avanzar día
        self.day += 1
        
        # Guardar estadísticas del día
        self.save_daily_stats()
        
        # Verificar condiciones de victoria/derrota
        self.check_game_over()
    
    def apply_decision(self, decision_id, continent_idx=None):
        """Aplica una decisión política"""
        success = self.decision_manager.apply_decision(
            decision_id, self.continents, continent_idx
        )
        
        if success:
            # Actualizar decisiones disponibles
            available_decisions = self.decision_manager.get_available_decisions(
                self.day, self.continents, self.simulator.get_global_stats()
            )
            self.decision_ui.update_decisions(available_decisions)
        
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
            self.ui.stats_surface = None  # Forzar regeneración
    
    def check_game_over(self):
        """Verifica las condiciones de fin de juego"""
        # Verificar victoria
        victory = self.simulator.check_victory_conditions()
        if victory:
            self.game_state = "victory"
            return
        
        # Verificar derrota
        defeat = self.simulator.check_defeat_conditions()
        if defeat:
            self.game_state = "defeat"
            self.defeat_reason = defeat
            return
    
    def update(self):
        """Actualiza el estado del juego"""
        # Actualizar notificaciones de eventos
        self.event_ui.update()
        
        # Simulación automática (opcional)
        current_time = pygame.time.get_ticks()
        if (self.game_state == "playing" and not self.paused and 
            current_time - self.last_simulation_time > 2000):  # 2 segundos por día
            # self.advance_day()  # Desactivado para control manual
            self.last_simulation_time = current_time
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        self.screen.fill((10, 10, 30))  # Fondo azul oscuro
        
        if self.game_state == "playing":
            self.draw_playing_state()
        elif self.game_state == "victory":
            self.draw_victory_screen()
        elif self.game_state == "defeat":
            self.draw_defeat_screen()
    
    def draw_playing_state(self):
        """Dibuja el estado de juego normal"""
        # Mapa mundial
        self.map.draw(self.continents, self.selected_continent)
        
        # Interfaz principal
        global_stats = self.simulator.get_global_stats()
        self.ui.draw(self.day, global_stats, self.continents, self.history)
        
        # Interfaz de decisiones
        self.decision_ui.draw()
        
        # Notificaciones de eventos
        self.event_ui.draw_event_notifications()
        
        # Panel de eventos recientes
        recent_events = self.event_manager.get_recent_events()
        if recent_events:
            self.event_ui.draw_events_history(recent_events, 950, 500, 240, 200)
        
        # Información adicional si hay un continente seleccionado
        if self.selected_continent is not None:
            self.draw_continent_details()
        
        # Indicador de pausa
        if self.paused:
            self.draw_pause_indicator()
    
    def draw_continent_details(self):
        """Dibuja detalles del continente seleccionado"""
        continent = self.continents[self.selected_continent]
        
        # Panel de detalles
        panel_rect = pygame.Rect(10, 220, 300, 200)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        font = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 20)
        
        # Título
        title_text = font.render(f"Detalles: {continent.name}", True, (255, 255, 0))
        self.screen.blit(title_text, (20, 230))
        
        # Estadísticas detalladas
        y_offset = 260
        stats = [
            f"Población: {continent.population:,}",
            f"Susceptibles: {int(continent.S):,}",
            f"Expuestos: {int(continent.E):,}",
            f"Infectados: {int(continent.I):,}",
            f"Recuperados: {int(continent.R):,}",
            f"Muertes: {continent.deaths:,}",
            f"Tasa de infección: {continent.get_infection_rate():.3%}",
            f"Capacidad hospitalaria: {int(continent.hospital_capacity):,}"
        ]
        
        for stat in stats:
            text_surface = font_small.render(stat, True, (255, 255, 255))
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 18
    
    def draw_pause_indicator(self):
        """Dibuja el indicador de pausa"""
        pause_text = pygame.font.Font(None, 48).render("PAUSADO", True, (255, 255, 0))
        pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 100))
        
        # Fondo semi-transparente
        bg_surface = pygame.Surface((pause_rect.width + 20, pause_rect.height + 10))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        bg_rect = bg_surface.get_rect(center=pause_rect.center)
        self.screen.blit(bg_surface, bg_rect)
        
        self.screen.blit(pause_text, pause_rect)
    
    def draw_victory_screen(self):
        """Dibuja la pantalla de victoria"""
        # Fondo semi-transparente
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 50, 0))  # Verde oscuro
        self.screen.blit(overlay, (0, 0))
        
        # Texto de victoria
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        
        victory_text = font_large.render("¡VICTORIA!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.screen.get_width() // 2, 250))
        self.screen.blit(victory_text, victory_rect)
        
        # Estadísticas finales
        global_stats = self.simulator.get_global_stats()
        stats_text = [
            f"Controlaste la epidemia en {self.day} días",
            f"Muertes totales: {global_stats['deaths']:,}",
            f"Economía final: {global_stats['economy']:.1f}%",
            f"Moral final: {global_stats['morale']:.1f}%"
        ]
        
        y_offset = 350
        for text in stats_text:
            text_surface = font_medium.render(text, True, (200, 255, 200))
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 50
        
        # Instrucciones
        instruction_text = font_medium.render("Presiona cualquier tecla o click para volver al menú", 
                                            True, (150, 255, 150))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, 600))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_defeat_screen(self):
        """Dibuja la pantalla de derrota"""
        # Fondo semi-transparente
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((50, 0, 0))  # Rojo oscuro
        self.screen.blit(overlay, (0, 0))
        
        # Texto de derrota
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        defeat_text = font_large.render("DERROTA", True, (255, 0, 0))
        defeat_rect = defeat_text.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(defeat_text, defeat_rect)
        
        # Razón de la derrota
        defeat_messages = {
            "too_many_deaths": "Demasiadas muertes: La epidemia se salió de control",
            "economic_or_morale_collapse": "Colapso económico o de moral: La sociedad no pudo resistir",
        }
        
        reason_text = defeat_messages.get(self.defeat_reason, "La epidemia no pudo ser controlada")
        reason_surface = font_medium.render(reason_text, True, (255, 150, 150))
        reason_rect = reason_surface.get_rect(center=(self.screen.get_width() // 2, 280))
        self.screen.blit(reason_surface, reason_rect)
        
        # Estadísticas finales
        global_stats = self.simulator.get_global_stats()
        stats_text = [
            f"Duración: {self.day} días",
            f"Muertes totales: {global_stats['deaths']:,}",
            f"Tasa de mortalidad: {(global_stats['deaths'] / global_stats['total_population']) * 100:.2f}%",
            f"Economía final: {global_stats['economy']:.1f}%",
            f"Moral final: {global_stats['morale']:.1f}%",
            f"Infectados restantes: {global_stats['infected']:,}"
        ]
        
        y_offset = 350
        for text in stats_text:
            text_surface = font_small.render(text, True, (255, 200, 200))
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30
        
        # Consejos para mejorar
        tips = [
            "Consejos para la próxima vez:",
            "• Actúa rápido al inicio de la epidemia",
            "• Balancea las medidas restrictivas con la economía",
            "• Invierte en hospitales antes de que sea tarde",
            "• Mantén alta la moral con campañas de comunicación"
        ]
        
        y_offset += 20
        for tip in tips:
            color = (255, 255, 150) if tip.startswith("Consejos") else (200, 200, 200)
            text_surface = font_small.render(tip, True, color)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 25
        
        # Instrucciones
        instruction_text = font_medium.render("Presiona cualquier tecla o click para volver al menú", 
                                            True, (255, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, 700))
        self.screen.blit(instruction_text, instruction_rect)