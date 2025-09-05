import numpy as np
import random

class Continent:
    def __init__(self, name, population, initial_infected=100, difficulty="normal"):
        self.name = name
        self.population = population
        
        # Variables SEIR
        self.S = population - initial_infected  # Susceptibles
        self.E = 0  # Expuestos
        self.I = initial_infected  # Infectados
        self.R = 0  # Recuperados
        self.deaths = 0
        
        # Parámetros epidemiológicos basados en dificultad
        if difficulty == "easy":
            self.beta = 0.3  # Tasa de transmisión
            self.sigma = 1/5.1  # Tasa de incubación (1/período de incubación)
            self.gamma = 1/10  # Tasa de recuperación
            self.mu = 0.02  # Tasa de mortalidad
        elif difficulty == "normal":
            self.beta = 0.5
            self.sigma = 1/5.1
            self.gamma = 1/10
            self.mu = 0.03
        else:  # expert
            self.beta = 0.7
            self.sigma = 1/4
            self.gamma = 1/12
            self.mu = 0.05
        
        # Variables socioeconómicas
        if difficulty == "easy":
            self.economy = 90.0
            self.morale = 85.0
            self.hospital_capacity = population * 0.01
        elif difficulty == "normal":
            self.economy = 80.0
            self.morale = 75.0
            self.hospital_capacity = population * 0.008
        else:  # expert
            self.economy = 70.0
            self.morale = 65.0
            self.hospital_capacity = population * 0.005
        
        # Variables de control
        self.airports_open = True
        self.schools_open = True
        self.mask_mandate = False
        self.quarantine = False
        self.vaccination_rate = 0.0
        
        # Modificadores temporales
        self.beta_modifier = 1.0
        self.gamma_modifier = 1.0
        self.mu_modifier = 1.0
        self.economy_modifier = 1.0
        self.morale_modifier = 1.0
    
    def apply_decision(self, decision, value=True):
        """Aplica una decisión política al continente"""
        if decision == "close_schools":
            self.schools_open = not value
            if value:  # Cerrar escuelas
                self.beta_modifier *= 0.8
                self.economy_modifier *= 0.95
            else:  # Abrir escuelas
                self.beta_modifier /= 0.8
                self.economy_modifier /= 0.95
                
        elif decision == "mask_mandate":
            self.mask_mandate = value
            if value:
                self.beta_modifier *= 0.7
                self.morale_modifier *= 0.98
            else:
                self.beta_modifier /= 0.7
                self.morale_modifier /= 0.98
                
        elif decision == "quarantine":
            self.quarantine = value
            if value:
                self.beta_modifier *= 0.3
                self.economy_modifier *= 0.7
                self.morale_modifier *= 0.8
            else:
                self.beta_modifier /= 0.3
                self.economy_modifier /= 0.7
                self.morale_modifier /= 0.8
                
        elif decision == "close_airports":
            self.airports_open = not value
            if value:  # Cerrar aeropuertos
                self.economy_modifier *= 0.9
            else:  # Abrir aeropuertos
                self.economy_modifier /= 0.9
                
        elif decision == "invest_hospitals":
            if value:
                self.hospital_capacity *= 1.2
                self.economy_modifier *= 0.95
                
        elif decision == "vaccination":
            self.vaccination_rate = value
            
        elif decision == "communication_campaign":
            if value:
                self.morale_modifier *= 1.1
                self.economy_modifier *= 0.99
    
    def apply_event(self, event_type, intensity=1.0):
        """Aplica un evento aleatorio"""
        if event_type == "new_variant":
            self.beta_modifier *= (1.0 + 0.3 * intensity)
        elif event_type == "international_aid":
            self.hospital_capacity *= (1.0 + 0.2 * intensity)
        elif event_type == "recession":
            self.economy_modifier *= (1.0 - 0.2 * intensity)
        elif event_type == "fake_news":
            self.morale_modifier *= (1.0 - 0.15 * intensity)
            self.vaccination_rate *= (1.0 - 0.3 * intensity)
        elif event_type == "local_outbreak":
            new_infections = int(self.population * 0.001 * intensity)
            self.S -= new_infections
            self.E += new_infections
        elif event_type == "medical_breakthrough":
            self.gamma_modifier *= (1.0 + 0.2 * intensity)
            self.mu_modifier *= (1.0 - 0.3 * intensity)
    
    def step(self, dt=1.0):
        """Ejecuta un paso de la simulación SEIR"""
        # Parámetros efectivos
        beta_eff = self.beta * self.beta_modifier
        sigma_eff = self.sigma
        gamma_eff = self.gamma * self.gamma_modifier
        mu_eff = self.mu * self.mu_modifier
        
        # Ajustar mortalidad por capacidad hospitalaria
        if self.I > self.hospital_capacity:
            mu_eff *= (1 + (self.I - self.hospital_capacity) / self.hospital_capacity)
        
        # Ecuaciones SEIR
        N = self.S + self.E + self.I + self.R
        if N <= 0:
            N = 1  # Evitar división por cero
        
        dS_dt = -beta_eff * self.S * self.I / N - self.vaccination_rate * self.S
        dE_dt = beta_eff * self.S * self.I / N - sigma_eff * self.E
        dI_dt = sigma_eff * self.E - gamma_eff * self.I - mu_eff * self.I
        dR_dt = gamma_eff * self.I + self.vaccination_rate * self.S
        dDeaths_dt = mu_eff * self.I
        
        # Actualizar variables
        self.S += dS_dt * dt
        self.E += dE_dt * dt
        self.I += dI_dt * dt
        self.R += dR_dt * dt
        self.deaths += dDeaths_dt * dt
        
        # Asegurar que las variables no sean negativas
        self.S = max(0, self.S)
        self.E = max(0, self.E)
        self.I = max(0, self.I)
        self.R = max(0, self.R)
        
        # Actualizar economía y moral
        self.economy *= self.economy_modifier
        self.morale *= self.morale_modifier
        
        # Límites
        self.economy = max(0, min(100, self.economy))
        self.morale = max(0, min(100, self.morale))
        
        # Degradación natural de modificadores (vuelven gradualmente a 1.0)
        decay_rate = 0.02
        self.economy_modifier += (1.0 - self.economy_modifier) * decay_rate
        self.morale_modifier += (1.0 - self.morale_modifier) * decay_rate
    
    def get_infection_rate(self):
        """Retorna la tasa de infección actual"""
        return self.I / self.population if self.population > 0 else 0
    
    def can_export_infections(self):
        """Determina si el continente puede exportar infecciones"""
        return self.airports_open and self.I > 0
    
    def receive_imported_infections(self, num_infections):
        """Recibe infecciones importadas de otros continentes"""
        num_infections = min(num_infections, self.S)
        if num_infections > 0:
            self.S -= num_infections
            self.E += num_infections

class SEIRSimulator:
    def __init__(self, continents, difficulty="normal"):
        self.continents = continents
        self.difficulty = difficulty
        
        # Parámetros de transmisión entre continentes
        if difficulty == "easy":
            self.flight_probability = 0.1
            self.infection_export_rate = 0.001
        elif difficulty == "normal":
            self.flight_probability = 0.15
            self.infection_export_rate = 0.002
        else:  # expert
            self.flight_probability = 0.2
            self.infection_export_rate = 0.003
    
    def simulate_international_spread(self):
        """Simula la propagación entre continentes"""
        for i, source in enumerate(self.continents):
            if not source.can_export_infections():
                continue
                
            for j, destination in enumerate(self.continents):
                if i == j or not destination.airports_open:
                    continue
                
                # Probabilidad de vuelo
                if random.random() < self.flight_probability:
                    # Número de infecciones exportadas
                    export_infections = int(source.I * self.infection_export_rate * random.random())
                    if export_infections > 0:
                        destination.receive_imported_infections(export_infections)
    
    def step(self):
        """Ejecuta un paso de simulación para todos los continentes"""
        # Simular propagación local en cada continente
        for continent in self.continents:
            continent.step()
        
        # Simular propagación internacional
        self.simulate_international_spread()
    
    def get_global_stats(self):
        """Calcula estadísticas globales"""
        total_pop = sum(c.population for c in self.continents)
        total_S = sum(c.S for c in self.continents)
        total_E = sum(c.E for c in self.continents)
        total_I = sum(c.I for c in self.continents)
        total_R = sum(c.R for c in self.continents)
        total_deaths = sum(c.deaths for c in self.continents)
        
        # Promedios ponderados por población
        avg_economy = sum(c.economy * c.population for c in self.continents) / total_pop
        avg_morale = sum(c.morale * c.population for c in self.continents) / total_pop
        
        return {
            'total_population': total_pop,
            'susceptible': int(total_S),
            'exposed': int(total_E),
            'infected': int(total_I),
            'recovered': int(total_R),
            'deaths': int(total_deaths),
            'economy': avg_economy,
            'morale': avg_morale
        }
    
    def is_epidemic_over(self):
        """Verifica si la epidemia ha terminado"""
        return all(c.I < 1 for c in self.continents)
    
    def check_victory_conditions(self):
        """Verifica las condiciones de victoria"""
        if not self.is_epidemic_over():
            return None
        
        stats = self.get_global_stats()
        if stats['economy'] >= 50 and stats['morale'] >= 50:
            return "victory"
        return None
    
    def check_defeat_conditions(self):
        """Verifica las condiciones de derrota"""
        stats = self.get_global_stats()
        
        # Demasiadas muertes
        death_rate = stats['deaths'] / stats['total_population']
        if death_rate > 0.1:  # 10% de la población
            return "too_many_deaths"
        
        # Colapso económico o de moral
        if stats['economy'] <= 0 or stats['morale'] <= 0:
            return "economic_or_morale_collapse"
        
        return None