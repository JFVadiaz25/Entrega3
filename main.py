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
SSID = "PAOLA"
PASSWORD = "4316298a"

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
    hora = (t[3] - 5) % 24  # UTC-5 Colombia
    anio = t[0] % 100
    return "{:02d}:{:02d}:{:02d}{:02d}/{:02d}/{} ".format(
        hora,
        t[4],
        t[5],
        t[2],  # día
        t[1],  # mes
        anio 
    )

def mostrar_hora():
    global ultimo_segundo

    t = localtime()
    segundo_actual = t[5]

    if segundo_actual != ultimo_segundo:
        ultimo_segundo = segundo_actual
        oled.fill_rect(0, 0, 80, 10, 0)
        hora = obtener_hora()
        oled.text(hora, 0, 0)
        oled.show()


# ---------------- SCROLL DERECHA ----------------
def scroll_derecha(texto, y):
    for x in range(-len(texto)*8, 128):
        controlRemoto()

        oled.fill_rect(0, 8, 128, 56, 0)
        oled.text(texto, x, y)
        oled.show()
        mostrar_hora()
        sleep(0.01)

# ---------------- MENSAJE ----------------
def mensaje_bienvenida():
    scroll_derecha("QUE MAS PUES PARCE :)", 30)

# ---------------- INTEGRANTES ----------------
def mostrar_integrantes():
    nombres = "JUAN PABLO GIRALDO - JUAN FELIPE VANEGAS DIAZ"
    scroll_derecha(nombres, 30)

# --- IMAGEN ---


#---------------- ICONO (matriz 0 y 1) ----------------
def mostrar_icono():
    oled.fill_rect(0, 8, 128, 56, 0)
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
    oled.fill_rect(0, 8, 128, 56, 0)  
    mostrar_hora()

    # Cuadrado frontal
    x = 30
    y = 25
    size = 25
    oled.rect(x, y, size, size, 1)

    dx = 10
    dy = -10

    oled.rect(x + dx, y + dy, size, size, 1)

    oled.line(x, y, x + dx, y + dy, 1)
    oled.line(x + size, y, x + size + dx, y + dy, 1)
    oled.line(x, y + size, x + dx, y + size + dy, 1)
    oled.line(x + size, y + size, x + size + dx, y + size + dy, 1)

    oled.show()

# -------------------------
# Vumetro
# -------------------------
mic = ADC(Pin(35))       # ADC en GPIO35
mic.atten(ADC.ATTN_11DB) # rango 0–3.6V


def mapear(valor, in_min, in_max, out_min, out_max):
    return int((valor - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def vumetro():
    muestras = []

    # Tomar exactamente 128 muestras (1 por pixel en X)
    for _ in range(ANCHO):
        muestras.append(mic.read())

    # Obtener offset (nivel medio)
    offset = sum(muestras) // len(muestras)

    oled.fill_rect(0, 8, 128, 56, 0)
    # Dibujar eje central
    oled.hline(0, CENTRO, ANCHO, 1)

    # Dibujar señal
    for x in range(ANCHO):
        valor = muestras[x] - offset  # quitar DC       
        y = mapear(valor, -1500, 1500, CENTRO + 20, CENTRO - 20)
        if y < 0:
            y = 0
        if y > ALTO - 1:
            y = ALTO - 1

        oled.pixel(x, y, 1)
    mostrar_hora()
    oled.show()
    sleep_ms(10)
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
    global rx_activo

    rx_activo = False  # apagar recepción

    for i, duracion in enumerate(color):
        if i % 2 == 0:
            ledIR.duty(512)
        else:
            ledIR.duty(0)
        sleep_us(duracion)

    ledIR.duty(0)

    sleep_ms(50) 
    rx_activo = True  #  reactivar recepción

#-------------------------
# CONTROL REMOTO
#-------------------------
codigo_ir = None

def ir_callback(data, addr, ctrl):
    global codigo_ir
    if not rx_activo:
        return
    if data < 0:
        return
    codigo_ir = data

ir = NEC_16(Pin(17, Pin.IN, Pin.PULL_UP), ir_callback)
def controlRemoto():
    global estado, codigo_ir
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
        elif codigo_ir == 8:
            estado = 0 if estado == 5 else 5
            print("Mensaje Bienvenida")
        elif codigo_ir == 1:
            estado = 0 if estado == 6 else 6
            print("Icono Bits")
        elif codigo_ir == 2:
            estado = 0 if estado == 7 else 7
            print("Imagen") 
        elif codigo_ir == 3:
            estado = 0 if estado == 8 else 8
            print("Dibujo")
        elif codigo_ir == 0:
            estado = 0 if estado == 9 else 9
            print("Integrantes")
        codigo_ir = None
    

#VARIABLES INICIALES
estado = 0  
tiempo_anterior = ticks_ms()
intervalo = 80
inicio_vumetro=0
color10 = convertir_ms(base_color_effects["GREEN_4"])
color56 = convertir_ms(base_color_effects["REDORANGE"])
weird = convertir_ms(special_effects["WEIRD_110"])

ANCHO = 128
ALTO = 64
CENTRO = ALTO // 2 + 10

ultimo_segundo = -1
contador_gc = 0
rx_activo=True
while True:
    ahora = ticks_ms()
    controlRemoto()
    # -------------------------
    # ANIMACIÓN
    # -------------------------
    if ticks_diff(ahora, tiempo_anterior) > intervalo:
        tiempo_anterior = ahora

        # -------------------------
        # MODO 0: BIENVENIDA
        # -------------------------
        if estado == 0:
            mostrar_hora()
            sleep_ms(200)
        elif estado == 9:
            mensaje_bienvenida()
            estado = 0
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
        if estado == 4:
            if inicio_vumetro == 0:
                inicio_vumetro = ticks_ms()  # registra cuándo empezó
            
            if ticks_diff(ticks_ms(), inicio_vumetro) > 15000:  # 15 segundos
                inicio_vumetro = 0  # resetea para la próxima vez
                estado = 0
                gc.collect()
            else:
                vumetro()
            continue

        elif estado == 5:
            print("Integrantes")
            mostrar_integrantes()
            estado = 0
        elif estado == 6:
            print("Icono Bits")
            mostrar_icono()
            estado = 0
        elif estado == 7:
            print("imagen")
            oled.fill_rect(0, 8, 128, 56, 0)  # Clear the display
            with open("ferrari.pbm", 'rb') as f:
                f.readline()  # Skip the first line (P4)
                f.readline()  # Skip the second line (width and height) 
                data=bytearray(f.read())  # Read the remaining binary data
            fbuf=framebuf.FrameBuffer(data, 64, 64, framebuf.MONO_HLSB)
            oled.blit(fbuf, 64, 0)  # Draw the image 
            oled.show()  # Update the display
            del data
            del fbuf
            estado = 0
            gc.collect()
        elif estado == 8:
            print("Dibujo")

            dibujo_geometrico()
            estado = 0
    contador_gc += 1
    if contador_gc > 200:
        gc.collect()
        contador_gc = 0