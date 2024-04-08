import pygame
import random
import time
import threading
import sys
import matplotlib.pyplot as plt

#VARIABLES
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 5
signals = []
noOfSignals = 4
currentGreen = 0
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0
speedMultiplier = 1.0
currentSpeedKph = 50
vehicle_count = {'right': 0, 'down': 0, 'left': 0, 'up': 0}
global_energy_on = True
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}

x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

signalCoords = [(596, 293), (759, 293), (759, 500), (595, 500)]
signalTimerCoords = [(530, 210), (810, 210), (810, 550), (530, 550)]

stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

stoppingGap = 15
movingGap = 15

pygame.init()
simulation = pygame.sprite.Group()

#SEMAFOROS Y VALORES
class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green

def initialize():
    global signals
    signals = []
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()

def updateValues():
    global currentGreen, currentYellow, nextGreen
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

#GENERAR VEHICULOS
def generateVehicles():
    global global_energy_on
    while True:
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
        time.sleep(random.uniform(0.5, 1.5))

#vehiculos
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        global global_energy_on
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.energyOn = global_energy_on 
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path).convert_alpha()
        
        vehicle_count[self.direction] += 1
         
        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]
        if(direction=='right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)


    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        global speedMultiplier
        adjustedSpeed = self.speed * speedMultiplier
                # Ignorar los semáforos si la energía está apagada
        if not self.energyOn:
            if self.direction == 'right':
                self.x += adjustedSpeed
            elif self.direction == 'down':
                self.y += adjustedSpeed
            elif self.direction == 'left':
                self.x -= adjustedSpeed
            elif self.direction == 'up':
                self.y -= adjustedSpeed
            return 

        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
            if (self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and (self.index == 0 or self.x + self.image.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)):
                self.x += adjustedSpeed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
            if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and (self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)):
                self.y += adjustedSpeed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
            if (self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap)):
                self.x -= adjustedSpeed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
            if (self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap)):
                self.y -= adjustedSpeed
        
def repeat():
    global currentGreen, currentYellow, nextGreen
    while signals[currentGreen].green > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 1
    for i in range(3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while signals[currentGreen].yellow > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 0
    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()
    
def print_vehicle_count():
    print("Conteo de vehículos generados por carril:")
    for direction in vehicle_count:
        if direction == 'right':
            print(f"Carril Derecho: {vehicle_count[direction]}")
        elif direction == 'down':
            print(f"Carril Inferior: {vehicle_count[direction]}")
        elif direction == 'left':
            print(f"Carril Izquierdo {vehicle_count[direction]}")
        elif direction == 'up':
            print(f"Carril Superior: {vehicle_count[direction]}")
class Main:
    def __init__(self):
        global global_energy_on
        pygame.init()
        self.screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption("Simulador de tráfico vehicular")
        self.isRunning = True
        #Inicializacion de botones
        self.speedUpButtonImg = pygame.image.load('images/speed_up_button.png').convert_alpha()
        self.speedUpButtonImg = pygame.transform.scale(self.speedUpButtonImg, (int(self.speedUpButtonImg.get_width() * 0.8), int(self.speedUpButtonImg.get_height() * 0.8)))
        self.speedDownButtonImg = pygame.image.load('images/speed_down_button.png').convert_alpha()
        self.speedDownButtonImg = pygame.transform.scale(self.speedDownButtonImg, (int(self.speedDownButtonImg.get_width() * 0.8), int(self.speedDownButtonImg.get_height() * 0.8)))
        self.originalUpButtonImg = self.speedUpButtonImg
        self.originalDownButtonImg = self.speedDownButtonImg

        self.stopButtonImg = pygame.image.load('images/stop_button.png').convert_alpha()
        self.startButtonImg = pygame.image.load('images/start_button.png').convert_alpha()
        self.stopButtonImg = pygame.transform.scale(self.stopButtonImg, (int(self.stopButtonImg.get_width() * 0.8), int(self.stopButtonImg.get_height() * 0.8)))
        self.startButtonImg = pygame.transform.scale(self.startButtonImg, (int(self.startButtonImg.get_width() * 0.8), int(self.startButtonImg.get_height() * 0.8)))
        self.originalStopButtonImg = self.stopButtonImg
        self.originalStartButtonImg = self.startButtonImg
        self.stopButtonRect = self.stopButtonImg.get_rect(topleft=(500, 90))
        self.startButtonRect = self.startButtonImg.get_rect(topleft=(500, 190))
        
        self.speedUpButtonRect = self.speedUpButtonImg.get_rect(topleft=(30, 90))
        self.speedDownButtonRect = self.speedDownButtonImg.get_rect(topleft=(30, 190))
        self.font = pygame.font.Font(None, 30)
        self.background = pygame.image.load('images/Fondo.jpg').convert()
        self.redSignal = pygame.image.load('images/signals/red.png').convert_alpha()
        self.redSignal = pygame.transform.scale(self.redSignal, (int(self.redSignal.get_width() * 0.8), int(self.redSignal.get_height() * 0.8)))
        self.yellowSignal = pygame.image.load('images/signals/yellow.png').convert_alpha()
        self.yellowSignal = pygame.transform.scale(self.yellowSignal, (int(self.yellowSignal.get_width() * 0.8), int(self.yellowSignal.get_height() * 0.8)))
        self.greenSignal = pygame.image.load('images/signals/green.png').convert_alpha()
        self.greenSignal = pygame.transform.scale(self.greenSignal, (int(self.greenSignal.get_width() * 0.8), int(self.greenSignal.get_height() * 0.8)))
        self.clock = pygame.time.Clock()

            
        self.yesEnergyButtonImg = pygame.image.load('images/yes_energy_button.png').convert_alpha()
        self.notEnergyButtonImg = pygame.image.load('images/not_energy_button.png').convert_alpha()
        
        
        self.yesEnergyButtonImg = pygame.transform.scale(self.yesEnergyButtonImg, (100, 50))  # Ajusta según necesidad
        self.notEnergyButtonImg = pygame.transform.scale(self.notEnergyButtonImg, (100, 50))  # Ajusta según necesidad
        
        
        self.energyButtonRect = self.yesEnergyButtonImg.get_rect(topleft=(500, 290))
        
        # Sprite de semáforo "apagado" o negro
        self.blackSignal = pygame.image.load('images/signals/black.png').convert_alpha()
        self.blackSignal = pygame.transform.scale(self.blackSignal, (int(self.blackSignal.get_width() * 0.8), int(self.blackSignal.get_height() * 0.8)))

        # Estado de la energía
        self.energyOn = True  # Comienza con energía encendida
        
        threading.Thread(target=initialize, daemon=True).start()
        threading.Thread(target=generateVehicles, daemon=True).start()
        self.isPaused = False
        self.run()
        
    def plot_vehicle_count(self, total_vehicle_count, elapsed_time_seconds):
        # Convertir el tiempo a minutos y redondear al minuto más cercano
        elapsed_time_minutes = round(elapsed_time_seconds / 60)


        vehicle_counts = [0] * (elapsed_time_minutes + 1)
        vehicle_counts[-1] = total_vehicle_count

        # Tiempo en minutos para el eje X
        time_minutes = list(range(elapsed_time_minutes + 1))
#Datos para el grafico en matplotlib
        plt.plot(time_minutes, vehicle_counts, marker='o')
        plt.title('Cantidad de vehículos vs. Tiempo')
        plt.xlabel('TIEMPO (minutos)')
        plt.ylabel('CANTIDAD DE VEHÍCULOS')
        plt.xticks(time_minutes)
        plt.yticks(range(0, max(vehicle_counts) + 50, 50))
        plt.grid(True)
        plt.show()
    def run(self):
        global global_energy_on
        global speedMultiplier, currentSpeedKph
        button_pressed = None
        maxSpeedKph = 80
        minSpeedKph = 50

        # Ajuste de velocidad inicial
        currentSpeedKph = 50
        speedMultiplier = 1.0
        
        # Inicializamos aquí las variables para el temporizador
        timer_start = 0
        timer_paused = 0
        paused_time = 0
        elapsed_time = 0
        while True:
            self.screen.blit(self.background, (0, 0))
            current_time = pygame.time.get_ticks()
            if self.isRunning and not self.isPaused:
                if timer_start == 0:
                    # Iniciar el temporizador
                    timer_start = current_time
                timer_paused = 0
                elapsed_time = current_time - timer_start - paused_time
            else:
                if timer_paused == 0:
                    # Pausar el temporizador
                    timer_paused = current_time
                paused_time += current_time - timer_paused
                timer_paused = current_time

            # Convertir tiempo transcurrido en horas, minutos y segundos
            seconds = (elapsed_time / 1000) % 60
            minutes = (elapsed_time / (1000 * 60)) % 60
            hours = (elapsed_time / (1000 * 60 * 60)) % 24

            # Renderizar el temporizador
            timer_text = self.font.render('{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)), True, (255, 255, 255))
            timer_rect = timer_text.get_rect(center=(1000, 130))  # Ajusta las coordenadas si es necesario
            self.screen.blit(timer_text, timer_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Convertir el tiempo transcurrido en horas, minutos y segundos
                    seconds = int(elapsed_time / 1000) % 60
                    minutes = int(elapsed_time / (1000 * 60)) % 60
                    hours = int(elapsed_time / (1000 * 60 * 60)) % 24
                    # Calcular el total de vehículos
                    total_vehicle_count = sum(vehicle_count.values())
                    
                    # Imprimir la información
                    print_vehicle_count()
                    print(f"Tiempo transcurrido: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    self.plot_vehicle_count(total_vehicle_count, elapsed_time / 1000)
                    sys.exit()


                elif event.type == pygame.MOUSEBUTTONUP:
                    if button_pressed == 'up':
                        self.speedUpButtonImg = self.originalUpButtonImg
                    elif button_pressed == 'down':
                        self.speedDownButtonImg = self.originalDownButtonImg
                    elif button_pressed == 'stop':
                        # Restablecer la imagen del botón de stop al tamaño original.
                        self.stopButtonImg = self.originalStopButtonImg
                    elif button_pressed == 'start':
                        # Restablecer la imagen del botón de start al tamaño original.
                        self.startButtonImg = self.originalStartButtonImg
                    if self.energyButtonRect.collidepoint(event.pos):
                        global_energy_on = not global_energy_on  # Cambiar el estado de la energía
                        # Actualizar el estado de energía para todos los vehículos
                        for vehicle in simulation.sprites():
                            vehicle.energyOn = global_energy_on
                    

                     #Al presionar aumenta o reduce la velocidad   
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.speedUpButtonRect.collidepoint(event.pos) and currentSpeedKph < maxSpeedKph:
                        self.speedUpButtonImg = pygame.transform.scale(self.originalUpButtonImg, (int(self.speedUpButtonRect.width * 0.9), int(self.speedUpButtonRect.height * 0.9)))
                        currentSpeedKph = min(maxSpeedKph, currentSpeedKph + 5)
                        speedMultiplier = currentSpeedKph / 50.0
                        button_pressed = 'up'
                    elif self.speedDownButtonRect.collidepoint(event.pos) and currentSpeedKph > minSpeedKph:
                        self.speedDownButtonImg = pygame.transform.scale(self.originalDownButtonImg, (int(self.speedDownButtonRect.width * 0.9), int(self.speedDownButtonRect.height * 0.9)))
                        currentSpeedKph = max(minSpeedKph, currentSpeedKph - 5)
                        speedMultiplier = currentSpeedKph / 50.0
                        button_pressed = 'down'
                    elif self.stopButtonRect.collidepoint(event.pos):
                        # Al presionar stop, cambia la imagen para reflejar el estado presionado
                        self.stopButtonImg = pygame.transform.scale(self.originalStopButtonImg, (int(self.stopButtonRect.width * 0.9), int(self.stopButtonRect.height * 0.9)))
                        self.isRunning = False
                        button_pressed = 'stop'
                    elif self.startButtonRect.collidepoint(event.pos):
                        # Al presionar start, cambia la imagen para reflejar el estado presionado
                        self.startButtonImg = pygame.transform.scale(self.originalStartButtonImg, (int(self.startButtonRect.width * 0.9), int(self.startButtonRect.height * 0.9)))
                        self.isRunning = True
                        button_pressed = 'start'
                elif event.type == pygame.MOUSEBUTTONUP:
                    if button_pressed == 'up':
                        self.speedUpButtonImg = self.originalUpButtonImg
                    elif button_pressed == 'down':
                        self.speedDownButtonImg = self.originalDownButtonImg
                    elif button_pressed == 'stop':
                        # Al soltar el botón, restablece la imagen al tamaño original
                        self.stopButtonImg = self.originalStopButtonImg
                    elif button_pressed == 'start':
                        # Al soltar el botón, restablece la imagen al tamaño original
                        self.startButtonImg = self.originalStartButtonImg
                    if self.energyButtonRect.collidepoint(event.pos):
                        self.energyOn = not self.energyOn  # Cambio del estado de la energía al hacer clic en el botón

            if self.isRunning:
                # Si la simulación está corriendo, actualiza los semáforos y mueve los vehículos
                if self.isRunning:
                    for i in range(noOfSignals):
                        # Revisa si la energía está apagada para mostrar el semáforo "apagado".
                        if not global_energy_on:
                            self.screen.blit(self.blackSignal, signalCoords[i])
                        else:
                            # Si la energía está encendida, muestra el estado actual de cada semáforo.
                            if i == currentGreen:
                                if currentYellow == 1:
                                    self.screen.blit(self.yellowSignal, signalCoords[i])
                                else:
                                    self.screen.blit(self.greenSignal, signalCoords[i])
                            else:
                                self.screen.blit(self.redSignal, signalCoords[i])
                    
                    # Renderiza y mueve cada vehículo en la simulación.
                    for vehicle in simulation.sprites():
                        vehicle.render(self.screen)
                        vehicle.move() 


                    if self.isPaused:
                        pause_text = self.font.render("Simulación Pausada", True, (255, 0, 0))
                        pause_text_rect = pause_text.get_rect(center=(700, 400))
                        self.screen.blit(pause_text, pause_text_rect)

                    # Actualizar botones y otros elementos de la interfaz aquí.
                    self.screen.blit(self.speedUpButtonImg, self.speedUpButtonRect)
                    self.screen.blit(self.speedDownButtonImg, self.speedDownButtonRect)
                    self.screen.blit(self.stopButtonImg, self.stopButtonRect)
                    self.screen.blit(self.startButtonImg, self.startButtonRect)
                    if global_energy_on:
                        self.screen.blit(self.yesEnergyButtonImg, self.energyButtonRect)
                    else:
                        self.screen.blit(self.notEnergyButtonImg, self.energyButtonRect)
                    self.screen.blit(self.speedUpButtonImg, self.speedUpButtonRect)
                    self.screen.blit(self.speedDownButtonImg, self.speedDownButtonRect)
                    self.screen.blit(self.stopButtonImg, self.stopButtonRect)
                    self.screen.blit(self.startButtonImg, self.startButtonRect)
                    speed_text = self.font.render(f"Velocidad: {currentSpeedKph} km/h", True, (255, 255, 255))
                    self.screen.blit(speed_text, (170, 155))
                    self.font = pygame.font.SysFont("arial", 28, bold=True, italic=False)


                    # Mostrar la velocidad actual.
                    speed_text = self.font.render(f"Velocidad: {currentSpeedKph} km/h", True, (255, 255, 255))
                    self.screen.blit(speed_text, (170, 155))
                    
                    # Actualizar la pantalla y mantener la frecuencia de actualización deseada.
                    pygame.display.flip()
                    self.clock.tick(60)
if __name__ == "__main__":
    Main()
