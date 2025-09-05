import random
import pygame

class Decision:
    def __init__(self, id, name, description, cost_economy=0, cost_morale=0, 
                 requirements=None, cooldown=0, target_continent=None, priority=1):
        self.id = id
        self.name = name
        self.description = description
        self.cost_economy = cost_economy
        self.cost_morale = cost_morale
        self.requirements = requirements or []
        self.cooldown = cooldown
        self.target_continent = target_continent
        self.priority = priority  # 1=baja, 2=media, 3=alta
        self.last_used = -999

class DecisionManager:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty
        self.decisions_available = []
        self.decisions_history = []
        self.decisions_used_today = 0
        self.max_decisions_per_day = 2  # Límite de decisiones por día
        self.current_day = 1
        
        # Definir todas las decisiones con prioridades
        self.all_decisions = [
            Decision("close_schools", "Cerrar Escuelas", 
                    "Cierra escuelas y universidades para reducir contagios.\nReduce transmisión en 20%, afecta economía y moral.",
                    cost_economy=5, cost_morale=3, cooldown=7, priority=2),
            
            Decision("mask_mandate", "Uso Obligatorio de Mascarillas",
                    "Implementa el uso obligatorio de mascarillas en espacios públicos.\nReduce transmisión significativamente con bajo costo.",
                    cost_economy=1, cost_morale=2, cooldown=14, priority=3),
            
            Decision("quarantine", "Cuarentena Total",
                    "Implementa cuarentena total, reduciendo drásticamente los contagios.\nMuy efectivo pero alto costo económico y social.",
                    cost_economy=20, cost_morale=15, cooldown=21, priority=3),
            
            Decision("close_airports", "Cerrar Aeropuertos",
                    "Cierra los aeropuertos para evitar propagación internacional.\nPreviene importación de casos pero afecta economía.",
                    cost_economy=10, cost_morale=5, cooldown=14, priority=2),
            
            Decision("invest_hospitals", "Invertir en Hospitales",
                    "Aumenta la capacidad hospitalaria para reducir mortalidad.\nMejora la atención médica y reduce muertes.",
                    cost_economy=8, cost_morale=0, cooldown=30, priority=3),
            
            Decision("vaccination_campaign", "Campaña de Vacunación",
                    "Inicia una campaña masiva de vacunación.\nReduce susceptibles pero requiere tiempo y recursos.",
                    cost_economy=15, cost_morale=0, cooldown=60, priority=3,
                    requirements=["day >= 30"]),
            
            Decision("communication_campaign", "Campaña de Comunicación",
                    "Mejora la moral pública con campañas informativas.\nAumenta la confianza y cooperación ciudadana.",
                    cost_economy=3, cost_morale=0, cooldown=14, priority=1),
            
            Decision("transport_control", "Control de Transporte",
                    "Controla el transporte interno para reducir contagios.\nLimita movilidad y reduce transmisión.",
                    cost_economy=12, cost_morale=8, cooldown=10, priority=2),
            
            Decision("medicine_distribution", "Distribución de Medicamentos",
                    "Distribuye medicamentos para reducir la mortalidad temporalmente.\nTratamientos que mejoran supervivencia.",
                    cost_economy=5, cost_morale=0, cooldown=21, priority=2),
            
            Decision("border_control", "Control Fronterizo Estricto",
                    "Implementa controles fronterizos más estrictos.\nReduce casos importados con impacto moderado.",
                    cost_economy=7, cost_morale=4, cooldown=14, priority=2),
            
            Decision("economic_stimulus", "Estímulo Económico",
                    "Proporciona ayuda económica a sectores afectados.\nMejora economía pero consume recursos públicos.",
                    cost_economy=10, cost_morale=0, cooldown=21, priority=1,
                    requirements=["economy < 60"]),
            
            Decision("mental_health_support", "Apoyo de Salud Mental",
                    "Proporciona servicios de salud mental a la población.\nMejora moral y resistencia al estrés.",
                    cost_economy=4, cost_morale=0, cooldown=14, priority=1,
                    requirements=["morale < 50"]),
        ]
        
        # Ajustar costos según dificultad
        cost_multiplier = {"easy": 0.7, "normal": 1.0, "expert": 1.5}[difficulty]
        for decision in self.all_decisions:
            decision.cost_economy *= cost_multiplier
            decision.cost_morale *= cost_multiplier
    
    def new_day(self, day):
        """Reinicia el contador de decisiones para un nuevo día"""
        self.current_day = day
        self.decisions_used_today = 0
    
    def can_make_decision(self):
        """Verifica si se pueden tomar más decisiones hoy"""
        return self.decisions_used_today < self.max_decisions_per_day
    
    def get_decisions_remaining(self):
        """Devuelve cuántas decisiones quedan disponibles hoy"""
        return max(0, self.max_decisions_per_day - self.decisions_used_today)
    
    def get_available_decisions(self, day, continents, global_stats):
        """Obtiene las decisiones disponibles con sistema de prioridades"""
        if not self.can_make_decision():
            return []
        
        available = []
        possible_decisions = []
        
        for decision in self.all_decisions:
            # Verificar cooldown
            if day - decision.last_used < decision.cooldown:
                continue
            
            # Verificar requisitos
            if not self._check_requirements(decision.requirements, day, continents, global_stats):
                continue
            
            possible_decisions.append(decision)
        
        if not possible_decisions:
            return []
        
        # Priorizar decisiones según la situación
        critical_situation = (
            global_stats['infected'] > global_stats['total_population'] * 0.05 or
            global_stats['economy'] < 30 or
            global_stats['morale'] < 30
        )
        
        if critical_situation:
            # En situación crítica, priorizar decisiones de alta prioridad
            high_priority = [d for d in possible_decisions if d.priority >= 2]
            if high_priority:
                possible_decisions = high_priority
        
        # Seleccionar 3-4 decisiones, priorizando las más importantes
        num_decisions = min(4, len(possible_decisions))
        
        # Peso basado en prioridad
        weights = [d.priority ** 2 for d in possible_decisions]
        available = self._weighted_sample(possible_decisions, weights, num_decisions)
        
        return available
    
    def _weighted_sample(self, population, weights, k):
        """Selecciona k elementos con probabilidades ponderadas"""
        if len(population) <= k:
            return population
        
        selected = []
        temp_pop = population.copy()
        temp_weights = weights.copy()
        
        for _ in range(k):
            total_weight = sum(temp_weights)
            if total_weight == 0:
                break
            
            # Selección ponderada
            rand_val = random.random() * total_weight
            cumulative = 0
            
            for i, weight in enumerate(temp_weights):
                cumulative += weight
                if rand_val <= cumulative:
                    selected.append(temp_pop[i])
                    temp_pop.pop(i)
                    temp_weights.pop(i)
                    break
        
        return selected
    
    def _check_requirements(self, requirements, day, continents, global_stats):
        """Verifica si se cumplen los requisitos"""
        for req in requirements:
            if "day >=" in req:
                min_day = int(req.split(">=")[1].strip())
                if day < min_day:
                    return False
            elif "economy <" in req:
                max_economy = float(req.split("<")[1].strip())
                if global_stats['economy'] >= max_economy:
                    return False
            elif "morale <" in req:
                max_morale = float(req.split("<")[1].strip())
                if global_stats['morale'] >= max_morale:
                    return False
            elif "infected >" in req:
                min_infected = int(req.split(">")[1].strip())
                if global_stats['infected'] < min_infected:
                    return False
        
        return True
    
    def apply_decision(self, decision_id, continents, target_continent_idx=None):
        """Aplica una decisión"""
        if not self.can_make_decision():
            return False
        
        decision = next((d for d in self.all_decisions if d.id == decision_id), None)
        if not decision:
            return False
        
        # Marcar decisión como usada
        decision.last_used = self.current_day
        self.decisions_used_today += 1
        
        self.decisions_history.append({
            'decision_id': decision_id,
            'day': self.current_day,
            'target': target_continent_idx,
            'name': decision.name
        })
        
        # Aplicar efectos
        if target_continent_idx is not None:
            self._apply_decision_effects(decision, [continents[target_continent_idx]])
        else:
            self._apply_decision_effects(decision, continents)
        
        return True
    
    def _apply_decision_effects(self, decision, continents):
        """Aplica los efectos de una decisión"""
        for continent in continents:
            # Aplicar costos
            continent.economy = max(0, continent.economy - decision.cost_economy)
            continent.morale = max(0, continent.morale - decision.cost_morale)
            
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
                vaccination_rate = {"easy": 0.012, "normal": 0.008, "expert": 0.005}[self.difficulty]
                continent.apply_decision("vaccination", vaccination_rate)
            elif decision.id == "communication_campaign":
                continent.apply_decision("communication_campaign", True)
            elif decision.id == "transport_control":
                continent.beta_modifier *= 0.85
            elif decision.id == "medicine_distribution":
                continent.mu_modifier *= 0.7
            elif decision.id == "border_control":
                continent.beta_modifier *= 0.9
            elif decision.id == "economic_stimulus":
                continent.economy = min(100, continent.economy + 15)
            elif decision.id == "mental_health_support":
                continent.morale = min(100, continent.morale + 12)

class DecisionUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 26)
        
        self.decision_buttons = []
        self.continent_buttons = []
        self.current_decisions = []
        self.selected_decision = None
        self.show_continent_selection = False
        
        # Área de decisiones
        self.decisions_rect = pygame.Rect(520, 200, 400, 450)
    
    def update_decisions(self, decisions, decisions_used_today, max_decisions):
        """Actualiza las decisiones disponibles"""
        self.current_decisions = decisions
        self.decision_buttons = []
        self.selected_decision = None
        self.show_continent_selection = False
        
        # Información de decisiones disponibles
        self.decisions_remaining = max_decisions - decisions_used_today
        
        # Crear botones para cada decisión
        button_height = 90
        start_y = self.decisions_rect.y + 60
        
        for i, decision in enumerate(decisions):
            if start_y + i * (button_height + 10) + button_height > self.decisions_rect.bottom - 10:
                break  # No mostrar más decisiones si no caben
            
            button_y = start_y + i * (button_height + 10)
            button = pygame.Rect(self.decisions_rect.x + 10, button_y, 
                               self.decisions_rect.width - 20, button_height)
            
            self.decision_buttons.append({
                'rect': button,
                'decision': decision,
                'hovered': False
            })
    
    def handle_event(self, event):
        """Maneja eventos de la interfaz de decisiones"""
        if event.type == pygame.MOUSEMOTION:
            # Actualizar hover
            for button_info in self.decision_buttons:
                button_info['hovered'] = button_info['rect'].collidepoint(event.pos)
            
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
        """Determina si una decisión requiere seleccionar continente"""
        regional_decisions = ["invest_hospitals", "medicine_distribution", "economic_stimulus"]
        return decision.id in regional_decisions
    
    def _create_continent_buttons(self):
        """Crea botones para seleccionar continente"""
        self.continent_buttons = []
        continent_names = ["América", "Europa-África", "Asia-Oceanía"]
        
        button_width = 180
        start_x = (self.screen.get_width() - len(continent_names) * button_width - 20) // 2
        
        for i, name in enumerate(continent_names):
            button_x = start_x + i * (button_width + 10)
            button_y = 350
            button = pygame.Rect(button_x, button_y, button_width, 60)
            
            self.continent_buttons.append({
                'rect': button,
                'continent_idx': i,
                'name': name,
                'hovered': False
            })
    
    def draw(self):
        """Dibuja la interfaz de decisiones"""
        if self.show_continent_selection:
            self._draw_continent_selection()
        else:
            self._draw_decision_panel()
    
    def _draw_decision_panel(self):
        """Dibuja el panel principal de decisiones"""
        # Fondo del panel
        pygame.draw.rect(self.screen, (25, 25, 45), self.decisions_rect)
        pygame.draw.rect(self.screen, (100, 100, 150), self.decisions_rect, 2)
        
        # Título
        title_text = self.font_title.render("Decisiones Políticas", True, (255, 255, 255))
        title_x = self.decisions_rect.x + 10
        title_y = self.decisions_rect.y + 10
        self.screen.blit(title_text, (title_x, title_y))
        
        # Contador de decisiones restantes
        if hasattr(self, 'decisions_remaining'):
            if self.decisions_remaining > 0:
                remaining_text = f"Decisiones restantes hoy: {self.decisions_remaining}"
                color = (150, 255, 150) if self.decisions_remaining > 1 else (255, 255, 150)
            else:
                remaining_text = "Sin decisiones disponibles hoy"
                color = (255, 150, 150)
            
            remaining_surface = self.font_small.render(remaining_text, True, color)
            self.screen.blit(remaining_surface, (title_x, title_y + 30))
        
        # Botones de decisiones
        if not self.current_decisions:
            no_decisions_text = "No hay decisiones disponibles"
            text_surface = self.font.render(no_decisions_text, True, (150, 150, 150))
            text_rect = text_surface.get_rect(center=(self.decisions_rect.centerx, 
                                                    self.decisions_rect.centery))
            self.screen.blit(text_surface, text_rect)
            return
        
        for button_info in self.decision_buttons:
            self._draw_decision_button(button_info)
    
    def _draw_decision_button(self, button_info):
        """Dibuja un botón de decisión individual"""
        decision = button_info['decision']
        rect = button_info['rect']
        hovered = button_info['hovered']
        
        # Color basado en prioridad
        priority_colors = {
            1: (60, 60, 90),    # Baja prioridad - azul oscuro
            2: (90, 90, 60),    # Media prioridad - amarillo oscuro
            3: (90, 60, 60)     # Alta prioridad - rojo oscuro
        }
        
        base_color = priority_colors.get(decision.priority, (60, 60, 90))
        
        if hovered:
            color = tuple(min(255, c + 25) for c in base_color)
            border_color = (200, 200, 200)
            border_width = 3
        else:
            color = base_color
            border_color = (120, 120, 120)
            border_width = 2
        
        # Dibujar botón
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, border_color, rect, border_width)
        
        # Indicador de prioridad
        priority_colors_bright = {1: (100, 150, 255), 2: (255, 255, 100), 3: (255, 100, 100)}
        priority_color = priority_colors_bright.get(decision.priority, (255, 255, 255))
        priority_rect = pygame.Rect(rect.right - 15, rect.y + 5, 10, 20)
        pygame.draw.rect(self.screen, priority_color, priority_rect)
        
        # Texto de la decisión
        y_offset = rect.y + 8
        
        # Nombre
        name_surface = self.font.render(decision.name, True, (255, 255, 255))
        if name_surface.get_width() > rect.width - 30:
            # Truncar nombre si es muy largo
            truncated_name = decision.name[:25] + "..."
            name_surface = self.font.render(truncated_name, True, (255, 255, 255))
        self.screen.blit(name_surface, (rect.x + 8, y_offset))
        y_offset += 22
        
        # Descripción (primera línea)
        desc_lines = decision.description.split('\n')
        first_line = desc_lines[0]
        if len(first_line) > 45:
            first_line = first_line[:42] + "..."
        
        desc_surface = self.font_small.render(first_line, True, (200, 200, 200))
        self.screen.blit(desc_surface, (rect.x + 8, y_offset))
        y_offset += 18
        
        # Segunda línea de descripción si existe
        if len(desc_lines) > 1:
            second_line = desc_lines[1]
            if len(second_line) > 45:
                second_line = second_line[:42] + "..."
            desc2_surface = self.font_small.render(second_line, True, (180, 180, 180))
            self.screen.blit(desc2_surface, (rect.x + 8, y_offset))
            y_offset += 18
        
        # Costos
        costs = []
        if decision.cost_economy > 0:
            costs.append(f"Economía -{decision.cost_economy:.0f}%")
        if decision.cost_morale > 0:
            costs.append(f"Moral -{decision.cost_morale:.0f}%")
        
        if costs:
            cost_text = "Costo: " + ", ".join(costs)
            cost_surface = self.font_small.render(cost_text, True, (255, 180, 180))
            self.screen.blit(cost_surface, (rect.x + 8, rect.bottom - 16))
        
        # Indicador de cooldown si corresponde
        if decision.cooldown > 0:
            cooldown_text = f"Espera: {decision.cooldown}d"
            cooldown_surface = self.font_small.render(cooldown_text, True, (150, 150, 255))
            cooldown_rect = cooldown_surface.get_rect()
            cooldown_rect.topright = (rect.right - 8, rect.y + 8)
            self.screen.blit(cooldown_surface, cooldown_rect.topleft)
    
    def _draw_continent_selection(self):
        """Dibuja la interfaz de selección de continentes"""
        # Fondo semi-transparente
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Panel de selección
        panel_width = 600
        panel_height = 200
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        pygame.draw.rect(self.screen, (40, 40, 70), panel_rect)
        pygame.draw.rect(self.screen, (150, 150, 200), panel_rect, 3)
        
        # Título
        title_text = self.font_title.render("Seleccionar Región de Aplicación", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(panel_rect.centerx, panel_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo con nombre de decisión
        if self.selected_decision:
            subtitle_text = f"Decisión: {self.selected_decision.name}"
            subtitle_surface = self.font.render(subtitle_text, True, (200, 200, 255))
            subtitle_rect = subtitle_surface.get_rect(center=(panel_rect.centerx, panel_y + 60))
            self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Botones de continentes
        for button_info in self.continent_buttons:
            rect = button_info['rect']
            name = button_info['name']
            hovered = button_info['hovered']
            
            color = (50, 120, 50) if hovered else (30, 80, 30)
            border_color = (100, 200, 100) if hovered else (80, 160, 80)
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            # Texto del continente
            text_surface = self.font.render(name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Instrucciones
        instructions = [
            "Selecciona el continente donde aplicar la decisión",
            "Click fuera para cancelar"
        ]
        
        y_offset = panel_rect.bottom + 20
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 20
    
    def get_decisions_info_text(self):
        """Devuelve texto informativo sobre el sistema de decisiones"""
        info_lines = [
            "Sistema de Decisiones:",
            "• Máximo 2 decisiones por día",
            "• Colores indican prioridad:",
            "  - Azul: Baja prioridad",
            "  - Amarillo: Media prioridad", 
            "  - Rojo: Alta prioridad",
            "• Algunas decisiones requieren",
            "  seleccionar región específica"
        ]
        return info_lines