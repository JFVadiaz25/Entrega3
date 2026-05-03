# main.py -- put your code here!
from machine import Pin, SoftI2C, PWM, ADC
import framebuf, network, ntptime, gc
from time import sleep, sleep_ms, sleep_us,ticks_ms, ticks_diff, localtime
from ssd1306 import SSD1306_I2C
from effect_definitions import base_color_effects, special_effects
from ir_rx.nec import NEC_16

# ------------------------ WIFI ------------------------
gc.collect()
print(gc.mem_free())
SSID = "Pablo"
PASSWORD = "juan1234"

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando a WiFi...")
    intentos = 0
    while not wlan.isconnected() and intentos < 20:
        sleep(0.5)
        intentos += 1
    if wlan.isconnected():
        print("Conectado:", wlan.ifconfig())
        return True
    else:
        print("No se pudo conectar al WiFi")
        return False

def sincronizar_hora():
    try:
        ntptime.settime()
        print("Hora sincronizada con servidor NTP")
    except Exception as e:
        print("Error NTP:", e)
conectar_wifi()
sincronizar_hora()
# --- OLED ---

i2c=SoftI2C(scl=Pin(22), sda=Pin(21))
oled=SSD1306_I2C(128, 64, i2c)

# ---------------- HORA ----------------
def obtener_hora():
    t = localtime()
    hora = (t[3] - 5) % 24  # Ajuste UTC-5 Colombia
    return "{:02d}:{:02d}:{:02d}".format(hora, t[4], t[5])

def mostrar_hora():
    hora = obtener_hora()
    oled.text(hora, 80, 0)

# ---------------- SCROLL DERECHA ----------------
def scroll_derecha(texto, y):
    for x in range(-len(texto)*8, 128):
        oled.fill(0)
        mostrar_hora()
        oled.text(texto, x, y)
        oled.show()
        sleep(0.02)

# ---------------- MENSAJE ----------------
def mensaje_bienvenida():
    scroll_derecha("QUE MAS PUES PARCE :)", 30)

# ---------------- INTEGRANTES ----------------
def mostrar_integrantes():
    nombres = "JUAN PABLO GIRALDO - JUAN FELIPE VANEGAS DIAZ"
    scroll_derecha(nombres, 30)

# --- IMAGEN ---
with open("ferrari.pbm", 'rb') as f:
    f.readline()  # Skip the first line (P4)
    f.readline()  # Skip the second line (width and height) 
    data=bytearray(f.read())  # Read the remaining binary data
fbuf=framebuf.FrameBuffer(data, 64, 64, framebuf.MONO_HLSB)

#---------------- ICONO (matriz 0 y 1) ----------------
def mostrar_icono():
    oled.fill(0)
    mostrar_hora()

    icono = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ]

    for y, fila in enumerate(icono):
        for x, val in enumerate(fila):
            oled.pixel(x+50, y+20, val)

    oled.show()

# ---------------- FIGURAS GEOMÉTRICAS ----------------
def dibujo_geometrico():
    oled.fill(0)
    mostrar_hora()

    # Rectángulo
    oled.rect(10, 10, 50, 30, 1)

    # Rectángulo relleno
    oled.fill_rect(70, 10, 40, 20, 1)

    # Líneas
    oled.line(0, 63, 127, 0, 1)
    oled.line(0, 0, 127, 63, 1)

    # Líneas horizontales
    for y in range(40, 60, 3):
        oled.line(0, y, 127, y, 1)

    oled.show()

# -------------------------
# Vumetro
# -------------------------
mic = ADC(Pin(35))       # ADC en GPIO35
mic.atten(ADC.ATTN_11DB) # rango 0–3.6V
#mic.width(ADC.WIDTH_12BIT) # resolución 12 bits (0-4095)

def mapear(valor, in_min, in_max, out_min, out_max):
    return int((valor - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# -------------------------
# CONTROL IR PIXMOB
# -------------------------

ledIR=PWM(Pin(5), freq=38000, duty=0)

def convertir_ms(color):
    if not color:
        return []

    resultado = []
    contador = 1

    for i in range(1, len(color)):
        if color[i] == color[i-1]:
            contador += 1
        else:
            resultado.append(contador * 700)
            contador = 1

    # agregar el último tramo
    resultado.append(contador * 700)

    return resultado

def enviar(color):
    global ir
    
    ir.close()
    for i, duracion in enumerate(color):
        if i % 2 == 0:  # High signal
            ledIR.duty(512)  # 50% duty cycle
        else:  # Low signal
            ledIR.duty(0)  # Turn off the LED
        sleep_us(duracion)  # Wait for the specified duration 

    ledIR.duty(0)  # Ensure the LED is off before starting
    ir = NEC_16(Pin(17, Pin.IN), ir_callback)

#-------------------------
# CONTROL REMOTO
#-------------------------
codigo_ir = None

def ir_callback(data, addr, ctrl):
    global codigo_ir
    if data < 0:
        return
    codigo_ir = data

ir = NEC_16(Pin(17, Pin.IN), ir_callback)

#VARIABLES INICIALES
estado = 0  
tiempo_anterior = ticks_ms()
intervalo = 80

color10 = convertir_ms(base_color_effects["GREEN_4"])
color56 = convertir_ms(base_color_effects["REDORANGE"])
weird = convertir_ms(special_effects["WEIRD_110"])

ANCHO = 128
ALTO = 64
CENTRO = ALTO // 2


while True:
    ahora = ticks_ms()

    # -------------------------
    # CONTROL REMOTO
    # -------------------------
    if codigo_ir is not None:

        print("Boton:", codigo_ir)

        # PIXMOB
        if codigo_ir == 4:
            estado = 0 if estado == 1 else 1
            print("RedOrange")
        elif codigo_ir == 5:
            estado = 0 if estado == 2 else 2
            print("Green4")
        elif codigo_ir == 7:
            estado = 0 if estado == 3 else 3
            print("Weird110")
        elif codigo_ir == 6:
            estado = 0 if estado == 4 else 4
            print("Vumetro")
        elif codigo_ir == 0:
            estado = 0 if estado == 5 else 5
            print("Integrantes")
        elif codigo_ir == 1:
            estado = 0 if estado == 6 else 6
            print("Icono Bits")
        elif codigo_ir == 2:
            estado = 0 if estado == 7 else 7
            print("Imagen") 
        elif codigo_ir == 3:
            estado = 0 if estado == 8 else 8
            print("Dibujo")
        
        codigo_ir = None

    # -------------------------
    # ANIMACIÓN
    # -------------------------
    if ticks_diff(ahora, tiempo_anterior) > intervalo:
        tiempo_anterior = ahora

        # -------------------------
        # MODO 0: BIENVENIDA
        # -------------------------
        if estado == 0:
            print("Bienvenida")
            mensaje_bienvenida()

        # -------------------------
        # MODOS: PIXMOB
        # -------------------------
        elif estado == 1:
            mostrar_hora()
            enviar(color56)
            sleep_ms(200)
        elif estado == 2:
            mostrar_hora()
            enviar(color10)
            sleep_ms(200)
        elif estado == 3:
            mostrar_hora()
            enviar(weird)
            sleep_ms(200)
        # -------------------------
        # MODO: VUMETRO
        # -------------------------
        elif estado == 4:
            muestras = []

            # Tomar exactamente 128 muestras (1 por pixel en X)
            for _ in range(ANCHO):
                muestras.append(mic.read())
            # Obtener offset (nivel medio)
            offset = sum(muestras) // len(muestras)
             
            oled.fill(0)
            mostrar_hora()
            # Dibujar eje central
            oled.hline(0, CENTRO, ANCHO, 1)

            # Dibujar señal
            for x in range(ANCHO):
                valor = muestras[x] - offset  # quitar DC
                
                # Escalar (ajusta estos valores)
                y = mapear(valor, -1500, 1500, CENTRO + 20, CENTRO - 20)

                # Limitar dentro de pantalla
                if y < 0:
                    y = 0
                if y > ALTO - 1:
                    y = ALTO - 1

                oled.pixel(x, y, 1)

            oled.show()
            sleep(0.05)

        elif estado == 5:
            print("Integrantes")
            mostrar_integrantes()
        elif estado == 6:
            print("Icono Bits")
            mostrar_icono()
        elif estado == 7:
            print("imagen")
            oled.fill(0)  # Clear the display
            mostrar_hora()
            oled.blit(fbuf, 32, 0)  # Draw the image 
            oled.show()  # Update the display
        elif estado == 8:
            print("Dibujo")
            dibujo_geometrico()
