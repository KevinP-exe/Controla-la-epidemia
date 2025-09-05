import random
import pygame

class Decision:
    def __init__(self, id, name, description, cost_economy=0, cost_morale=0, 
                 requirements=None, cooldown=0, target_continent=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost_economy = cost_economy
        self.cost_morale = cost_morale
        self.requirements = requirements or []
        self.cooldown = cooldown
        self.target_continent = target_continent  # None = global, o índice específico
        self.last_used = -999  # Día en que se usó por última vez

class DecisionManager:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty
        self.decisions_available = []
        self.decisions_history = []
        
        # Definir todas las decisiones posibles
        self.all_decisions = [
            Decision("close_schools", "Cerrar Escuelas", 
                    "Cierra escuelas y universidades para reducir contagios",
                    cost_economy=5, cost_morale=3, cooldown=7),
            
            Decision("mask_mandate", "Uso Obligatorio de Mascarillas",
                    "Implementa el uso obligatorio de mascarillas en espacios públicos",
                    cost_economy=1, cost_morale=2, cooldown=14),
            
            Decision("quarantine", "Cuarentena Total",
                    "Implementa cuarentena total, reduciendo drasticamente los contagios",
                    cost_economy=20, cost_morale=15, cooldown=21),
            
            Decision("close_airports", "Cerrar Aeropuertos",
                    "Cierra los aeropuertos para evitar propagación internacional",
                    cost_economy=10, cost_morale=5, cooldown=14),
            
            Decision("invest_hospitals", "Invertir en Hospitales",
                    "Aumenta la capacidad hospitalaria para reducir mortalidad",
                    cost_economy=8, cost_morale=0, cooldown=30),
            
            Decision("vaccination_campaign", "Campaña de Vacunación",
                    "Inicia una campaña masiva de vacunación",
                    cost_economy=15, cost_morale=0, cooldown=60,
                    requirements=["day >= 30"]),
            
            Decision("communication_campaign", "Campaña de Comunicación",
                    "Mejora la moral pública con campañas informativas",
                    cost_economy=3, cost_morale=0, cooldown=14),
            
            Decision("transport_control", "Control de Transporte",
                    "Controla el transporte interno para reducir contagios",
                    cost_economy=12, cost_morale=8, cooldown=10),
            
            Decision("medicine_distribution", "Distribución de Medicamentos",
                    "Distribuye medicamentos para reducir la mortalidad temporalmente",
                    cost_economy=5, cost_morale=0, cooldown=21),
            
            Decision("border_control", "Control Fronterizo Estricto",
                    "Implementa controles fronterizos más estrictos",
                    cost_economy=7, cost_morale=4, cooldown=14),
        ]
        
        # Ajustar costos según dificultad
        if difficulty == "easy":
            for decision in self.all_decisions:
                decision.cost_economy *= 0.7
                decision.cost_morale *= 0.7
        elif difficulty == "expert":
            for decision in self.all_decisions:
                decision.cost_economy *= 1.5
                decision.cost_morale *= 1.3
    
    def get_available_decisions(self, day, continents, global_stats):
        """Obtiene las decisiones disponibles en el día actual"""
        available = []
        
        # Seleccionar 2-3 decisiones aleatorias que cumplan los requisitos
        possible_decisions = []
        
        for decision in self.all_decisions:
            # Verificar cooldown
            if day - decision.last_used < decision.cooldown:
                continue
            
            # Verificar requisitos
            requirements_met = True
            for req in decision.requirements:
                if not self._check_requirement(req, day, continents, global_stats):
                    requirements_met = False
                    break
            
            if requirements_met:
                possible_decisions.append(decision)
        
        # Seleccionar 2-3 decisiones aleatorias
        num_decisions = min(3, len(possible_decisions))
        if num_decisions > 0:
            available = random.sample(possible_decisions, num_decisions)
        
        return available
    
    def _check_requirement(self, requirement, day, continents, global_stats):
        """Verifica si se cumple un requisito específico"""
        if "day >=" in requirement:
            min_day = int(requirement.split(">=")[1].strip())
            return day >= min_day
        elif "economy >" in requirement:
            min_economy = float(requirement.split(">")[1].strip())
            return global_stats['economy'] > min_economy
        elif "infected >" in requirement:
            min_infected = int(requirement.split(">")[1].strip())
            return global_stats['infected'] > min_infected
        
        return True
    
    def apply_decision(self, decision_id, continents, target_continent_idx=None):
        """Aplica una decisión a los continentes"""
        decision = next((d for d in self.all_decisions if d.id == decision_id), None)
        if not decision:
            return False
        
        decision.last_used = len(self.decisions_history)
        self.decisions_history.append({
            'decision_id': decision_id,
            'day': len(self.decisions_history),
            'target': target_continent_idx
        })
        
        # Aplicar efectos
        if target_continent_idx is not None:
            # Decisión específica para un continente
            continent = continents[target_continent_idx]
            self._apply_decision_effects(decision, [continent])
        else:
            # Decisión global
            self._apply_decision_effects(decision, continents)
        
        return True
    
    def _apply_decision_effects(self, decision, continents):
        """Aplica los efectos de una decisión a los continentes especificados"""
        for continent in continents:
            # Aplicar costos
            continent.economy -= decision.cost_economy
            continent.morale -= decision.cost_morale
            
            # Aplicar efectos específicos
            if decision.id == "close_schools":
                continent.apply_decision("close_schools", True)
            
            elif decision.id == "mask_mandate":
                continent.apply_decision("mask_mandate", True)
            
            elif decision.id == "quarantine":
                continent.apply_decision("quarantine", True)
            
            elif decision.id == "close_airports":
                continent.apply_decision("close_airports", True)
            
            elif decision.id == "invest_hospitals":
                continent.apply_decision("invest_hospitals", True)
            
            elif decision.id == "vaccination_campaign":
                vaccination_rate = 0.01 if self.difficulty == "easy" else 0.007 if self.difficulty == "normal" else 0.005
                continent.apply_decision("vaccination", vaccination_rate)
            
            elif decision.id == "communication_campaign":
                continent.apply_decision("communication_campaign", True)
            
            elif decision.id == "transport_control":
                continent.beta_modifier *= 0.85
                
            elif decision.id == "medicine_distribution":
                continent.mu_modifier *= 0.7  # Reduce mortalidad temporalmente
                
            elif decision.id == "border_control":
                continent.beta_modifier *= 0.9

class DecisionUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        self.decision_buttons = []
        self.continent_buttons = []
        self.current_decisions = []
        self.selected_decision = None
        self.show_continent_selection = False
        
    def update_decisions(self, decisions):
        """Actualiza las decisiones disponibles"""
        self.current_decisions = decisions
        self.decision_buttons = []
        self.selected_decision = None
        self.show_continent_selection = False
        
        # Crear botones para cada decisión
        for i, decision in enumerate(decisions):
            button_y = 200 + i * 120
            button = pygame.Rect(520, button_y, 400, 100)
            self.decision_buttons.append({
                'rect': button,
                'decision': decision,
                'hovered': False
            })
    
    def handle_event(self, event):
        """Maneja eventos de la interfaz de decisiones"""
        if event.type == pygame.MOUSEMOTION:
            # Actualizar hover en botones de decisiones
            for button_info in self.decision_buttons:
                button_info['hovered'] = button_info['rect'].collidepoint(event.pos)
            
            # Actualizar hover en botones de continentes
            for button_info in self.continent_buttons:
                button_info['hovered'] = button_info['rect'].collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.show_continent_selection:
                # Selección de continente
                for button_info in self.continent_buttons:
                    if button_info['rect'].collidepoint(event.pos):
                        return {
                            'action': 'apply_decision',
                            'decision_id': self.selected_decision.id,
                            'continent_idx': button_info['continent_idx']
                        }
                
                # Click fuera = cancelar selección
                self.show_continent_selection = False
                self.selected_decision = None
            
            else:
                # Selección de decisión
                for button_info in self.decision_buttons:
                    if button_info['rect'].collidepoint(event.pos):
                        self.selected_decision = button_info['decision']
                        
                        # Si la decisión requiere seleccionar continente
                        if self._requires_continent_selection(button_info['decision']):
                            self.show_continent_selection = True
                            self._create_continent_buttons()
                        else:
                            return {
                                'action': 'apply_decision',
                                'decision_id': button_info['decision'].id,
                                'continent_idx': None
                            }
        
        return None
    
    def _requires_continent_selection(self, decision):
        """Determina si una decisión requiere seleccionar continente específico"""
        # La mayoría de decisiones son globales, pero algunas pueden ser específicas
        regional_decisions = ["invest_hospitals", "medicine_distribution"]
        return decision.id in regional_decisions
    
    def _create_continent_buttons(self):
        """Crea botones para seleccionar continente"""
        self.continent_buttons = []
        continent_names = ["América", "Europa-África", "Asia-Oceanía"]
        
        for i, name in enumerate(continent_names):
            button_x = 200 + i * 250
            button_y = 350
            button = pygame.Rect(button_x, button_y, 200, 60)
            
            self.continent_buttons.append({
                'rect': button,
                'continent_idx': i,
                'name': name,
                'hovered': False
            })
    
    def draw(self):
        """Dibuja la interfaz de decisiones"""
        if not self.current_decisions and not self.show_continent_selection:
            return
        
        if self.show_continent_selection:
            self._draw_continent_selection()
        else:
            self._draw_decision_selection()
    
    def _draw_decision_selection(self):
        """Dibuja los botones de selección de decisiones"""
        # Título
        title_text = self.font.render("Decisiones Disponibles:", True, (255, 255, 255))
        self.screen.blit(title_text, (520, 170))
        
        # Botones de decisiones
        for button_info in self.decision_buttons:
            decision = button_info['decision']
            rect = button_info['rect']
            hovered = button_info['hovered']
            
            # Color del botón
            if hovered:
                color = (80, 80, 120)
                border_color = (150, 150, 200)
            else:
                color = (60, 60, 90)
                border_color = (100, 100, 150)
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            # Texto de la decisión
            name_text = self.font.render(decision.name, True, (255, 255, 255))
            self.screen.blit(name_text, (rect.x + 10, rect.y + 10))
            
            # Descripción
            desc_text = self.font_small.render(decision.description, True, (200, 200, 200))
            self.screen.blit(desc_text, (rect.x + 10, rect.y + 35))
            
            # Costos
            cost_text = f"Costo: Economía -{decision.cost_economy}%, Moral -{decision.cost_morale}%"
            cost_surface = self.font_small.render(cost_text, True, (255, 200, 200))
            self.screen.blit(cost_surface, (rect.x + 10, rect.y + 60))
    
    def _draw_continent_selection(self):
        """Dibuja la selección de continentes"""
        # Fondo semi-transparente
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title_text = self.font.render(f"Selecciona continente para: {self.selected_decision.name}", 
                                     True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 300))
        self.screen.blit(title_text, title_rect)
        
        # Botones de continentes
        for button_info in self.continent_buttons:
            rect = button_info['rect']
            name = button_info['name']
            hovered = button_info['hovered']
            
            color = (0, 120, 0) if hovered else (0, 80, 0)
            border_color = (0, 200, 0) if hovered else (0, 150, 0)
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            text_surface = self.font.render(name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Instrucción para cancelar
        cancel_text = self.font_small.render("Click fuera para cancelar", True, (200, 200, 200))
        cancel_rect = cancel_text.get_rect(center=(self.screen.get_width() // 2, 450))
        self.screen.blit(cancel_text, cancel_rect)