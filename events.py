import random
import pygame

class Event:
    def __init__(self, id, name, description, probability, effects, requirements=None):
        self.id = id
        self.name = name
        self.description = description
        self.probability = probability
        self.effects = effects  # Dictionary con los efectos
        self.requirements = requirements or []

class EventManager:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty
        self.events_history = []
        
        # Ajustar probabilidades según dificultad
        prob_multiplier = 1.0
        if difficulty == "easy":
            prob_multiplier = 0.7
        elif difficulty == "expert":
            prob_multiplier = 1.3
        
        # Definir todos los eventos posibles
        self.all_events = [
            Event("new_variant", "Nueva Variante Detectada",
                  "Se ha detectado una nueva variante más contagiosa del virus",
                  probability=0.15 * prob_multiplier,
                  effects={"type": "new_variant", "intensity": 1.0},
                  requirements=["day >= 30", "infected > 1000"]),
            
            Event("international_aid", "Ayuda Internacional",
                  "Organizaciones internacionales envían ayuda médica",
                  probability=0.12 * prob_multiplier,
                  effects={"type": "international_aid", "intensity": 1.0},
                  requirements=["day >= 20"]),
            
            Event("global_recession", "Recesión Global",
                  "La economía mundial entra en recesión afectando todos los países",
                  probability=0.08 * prob_multiplier,
                  effects={"type": "recession", "intensity": 1.0},
                  requirements=["day >= 40"]),
            
            Event("fake_news_campaign", "Campaña de Desinformación",
                  "Se extienden noticias falsas sobre vacunas y tratamientos",
                  probability=0.10 * prob_multiplier,
                  effects={"type": "fake_news", "intensity": 1.0},
                  requirements=["day >= 15"]),
            
            Event("local_outbreak", "Brote Local",
                  "Se produce un brote masivo en una región específica",
                  probability=0.18 * prob_multiplier,
                  effects={"type": "local_outbreak", "intensity": 1.0},
                  requirements=["infected > 500"]),
            
            Event("mass_flight", "Vuelo Masivo de Infectados",
                  "Un vuelo con muchos pasajeros infectados propaga el virus",
                  probability=0.12 * prob_multiplier,
                  effects={"type": "mass_flight", "intensity": 1.0},
                  requirements=["day >= 10"]),
            
            Event("medical_breakthrough", "Avance Médico",
                  "Se descubre un tratamiento más efectivo",
                  probability=0.10 * prob_multiplier,
                  effects={"type": "medical_breakthrough", "intensity": 1.0},
                  requirements=["day >= 60"]),
            
            Event("social_unrest", "Disturbios Sociales",
                  "La población protesta contra las medidas restrictivas",
                  probability=0.14 * prob_multiplier,
                  effects={"type": "social_unrest", "intensity": 1.0},
                  requirements=["morale < 40"]),
            
            Event("vaccine_resistance", "Resistencia a Vacunas",
                  "Surge resistencia pública a las campañas de vacunación",
                  probability=0.11 * prob_multiplier,
                  effects={"type": "vaccine_resistance", "intensity": 1.0},
                  requirements=["day >= 30"]),
            
            Event("hospital_overflow", "Colapso Hospitalario",
                  "Los hospitales se saturan completamente",
                  probability=0.13 * prob_multiplier,
                  effects={"type": "hospital_overflow", "intensity": 1.0},
                  requirements=["infected > 10000"]),
            
            Event("successful_containment", "Contención Exitosa",
                  "Medidas de contención muestran resultados muy positivos",
                  probability=0.09 * prob_multiplier,
                  effects={"type": "successful_containment", "intensity": 1.0},
                  requirements=["day >= 45", "quarantine_active"]),
            
            Event("supply_shortage", "Escasez de Suministros",
                  "Escasez crítica de equipos médicos y medicamentos",
                  probability=0.12 * prob_multiplier,
                  effects={"type": "supply_shortage", "intensity": 1.0},
                  requirements=["day >= 25"]),
        ]
    
    def check_events(self, day, continents, global_stats):
        """Verifica y ejecuta eventos aleatorios"""
        events_triggered = []
        
        for event in self.all_events:
            # Verificar requisitos
            if not self._check_requirements(event, day, continents, global_stats):
                continue
            
            # Verificar si el evento ya ocurrió recientemente
            if self._event_recently_occurred(event.id, day, cooldown=30):
                continue
            
            # Verificar probabilidad
            if random.random() < event.probability:
                events_triggered.append(event)
                self._apply_event(event, continents)
                self.events_history.append({
                    'day': day,
                    'event_id': event.id,
                    'name': event.name,
                    'description': event.description
                })
        
        return events_triggered
    
    def _check_requirements(self, event, day, continents, global_stats):
        """Verifica si se cumplen los requisitos de un evento"""
        for req in event.requirements:
            if "day >=" in req:
                min_day = int(req.split(">=")[1].strip())
                if day < min_day:
                    return False
            
            elif "infected >" in req:
                min_infected = int(req.split(">")[1].strip())
                if global_stats['infected'] < min_infected:
                    return False
            
            elif "morale <" in req:
                max_morale = float(req.split("<")[1].strip())
                if global_stats['morale'] >= max_morale:
                    return False
            
            elif "economy <" in req:
                max_economy = float(req.split("<")[1].strip())
                if global_stats['economy'] >= max_economy:
                    return False
            
            elif req == "quarantine_active":
                if not any(c.quarantine for c in continents):
                    return False
        
        return True
    
    def _event_recently_occurred(self, event_id, current_day, cooldown=30):
        """Verifica si un evento ocurrió recientemente"""
        for event_record in reversed(self.events_history):
            if event_record['event_id'] == event_id:
                if current_day - event_record['day'] < cooldown:
                    return True
                break
        return False
    
    def _apply_event(self, event, continents):
        """Aplica los efectos de un evento"""
        effect_type = event.effects["type"]
        intensity = event.effects["intensity"]
        
        # Determinar continente(s) afectado(s)
        if effect_type in ["local_outbreak", "mass_flight", "hospital_overflow"]:
            # Eventos que afectan a un continente específico
            target_continent = random.choice(continents)
            self._apply_event_to_continent(effect_type, intensity, target_continent)
        else:
            # Eventos globales
            for continent in continents:
                self._apply_event_to_continent(effect_type, intensity, continent)
    
    def _apply_event_to_continent(self, effect_type, intensity, continent):
        """Aplica un evento específico a un continente"""
        if effect_type == "new_variant":
            continent.apply_event("new_variant", intensity)
        
        elif effect_type == "international_aid":
            continent.apply_event("international_aid", intensity)
        
        elif effect_type == "recession":
            continent.apply_event("recession", intensity)
        
        elif effect_type == "fake_news":
            continent.apply_event("fake_news", intensity)
        
        elif effect_type == "local_outbreak":
            continent.apply_event("local_outbreak", intensity * 2)  # Mayor impacto local
        
        elif effect_type == "mass_flight":
            # Importar infecciones de otros continentes
            import_infections = int(continent.population * 0.0005 * intensity)
            continent.receive_imported_infections(import_infections)
        
        elif effect_type == "medical_breakthrough":
            continent.apply_event("medical_breakthrough", intensity)
        
        elif effect_type == "social_unrest":
            continent.morale *= (1 - 0.2 * intensity)
            continent.economy *= (1 - 0.1 * intensity)
            # Reducir efectividad de medidas restrictivas
            if continent.quarantine:
                continent.beta_modifier *= (1 + 0.3 * intensity)
        
        elif effect_type == "vaccine_resistance":
            continent.vaccination_rate *= (1 - 0.5 * intensity)
            continent.morale *= (1 - 0.1 * intensity)
        
        elif effect_type == "hospital_overflow":
            # Reducir temporalmente la capacidad hospitalaria efectiva
            continent.hospital_capacity *= (1 - 0.3 * intensity)
            continent.mu_modifier *= (1 + 0.5 * intensity)  # Aumentar mortalidad
        
        elif effect_type == "successful_containment":
            continent.beta_modifier *= (1 - 0.3 * intensity)
            continent.morale *= (1 + 0.15 * intensity)
        
        elif effect_type == "supply_shortage":
            continent.mu_modifier *= (1 + 0.2 * intensity)
            continent.hospital_capacity *= (1 - 0.2 * intensity)
            continent.economy *= (1 - 0.08 * intensity)
    
    def get_recent_events(self, days=7):
        """Obtiene los eventos recientes"""
        if not self.events_history:
            return []
        
        current_day = max(event['day'] for event in self.events_history)
        recent_events = [
            event for event in self.events_history 
            if current_day - event['day'] < days
        ]
        
        return sorted(recent_events, key=lambda x: x['day'], reverse=True)

class EventUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.active_notifications = []
    
    def add_event_notification(self, event, duration=180):  # 3 segundos a 60 FPS
        """Añade una notificación de evento"""
        self.active_notifications.append({
            'event': event,
            'duration': duration,
            'max_duration': duration
        })
    
    def update(self):
        """Actualiza las notificaciones activas"""
        self.active_notifications = [
            notif for notif in self.active_notifications 
            if notif['duration'] > 0
        ]
        
        for notif in self.active_notifications:
            notif['duration'] -= 1
    
    def draw_event_notifications(self):
        """Dibuja las notificaciones de eventos activos"""
        screen_width = self.screen.get_width()
        
        for i, notif in enumerate(self.active_notifications):
            event = notif['event']
            duration = notif['duration']
            max_duration = notif['max_duration']
            
            # Posición de la notificación
            y_pos = 50 + i * 80
            
            # Calcular alpha para efecto de fade
            alpha = min(255, (duration / max_duration) * 255)
            
            # Crear superficie para la notificación
            notif_surface = pygame.Surface((400, 70))
            notif_surface.set_alpha(alpha)
            
            # Determinar color según tipo de evento
            if any(keyword in event.name.lower() for keyword in ['nueva variante', 'brote', 'colapso']):
                bg_color = (120, 40, 40)  # Rojo para eventos negativos
            elif any(keyword in event.name.lower() for keyword in ['ayuda', 'avance', 'exitosa']):
                bg_color = (40, 120, 40)  # Verde para eventos positivos
            else:
                bg_color = (60, 60, 120)  # Azul para eventos neutrales
            
            notif_surface.fill(bg_color)
            pygame.draw.rect(notif_surface, (200, 200, 200), notif_surface.get_rect(), 2)
            
            # Texto del evento
            title_text = self.font.render(event.name, True, (255, 255, 255))
            notif_surface.blit(title_text, (10, 8))
            
            # Descripción (truncada si es necesaria)
            desc = event.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            
            desc_text = self.font_small.render(desc, True, (220, 220, 220))
            notif_surface.blit(desc_text, (10, 32))
            
            # Dibujar la notificación en pantalla
            self.screen.blit(notif_surface, (screen_width - 420, y_pos))
    
    def draw_events_history(self, events_history, x, y, width, height):
        """Dibuja el historial de eventos en un panel"""
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (30, 30, 50), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        # Título
        title_text = self.font.render("Eventos Recientes", True, (255, 255, 255))
        self.screen.blit(title_text, (x + 10, y + 10))
        
        # Lista de eventos
        recent_events = events_history[-8:]  # Últimos 8 eventos
        
        y_offset = y + 40
        for event_record in reversed(recent_events):
            if y_offset + 20 > y + height - 10:
                break
            
            event_text = f"Día {event_record['day']}: {event_record['name']}"
            if len(event_text) > 35:
                event_text = event_text[:32] + "..."
            
            # Color según tipo de evento
            if any(keyword in event_record['name'].lower() for keyword in ['nueva variante', 'brote', 'colapso', 'recesión']):
                text_color = (255, 150, 150)  # Rojo claro
            elif any(keyword in event_record['name'].lower() for keyword in ['ayuda', 'avance', 'exitosa']):
                text_color = (150, 255, 150)  # Verde claro
            else:
                text_color = (200, 200, 255)  # Azul claro
            
            text_surface = self.font_small.render(event_text, True, text_color)
            self.screen.blit(text_surface, (x + 10, y_offset))
            y_offset += 20