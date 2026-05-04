from machine import Pin, SoftI2C, PWM, ADC
import framebuf, network, ntptime, gc
from time import sleep_ms, sleep_us, ticks_ms, ticks_diff, localtime
from ssd1306 import SSD1306_I2C
from effect_definitions import base_color_effects, special_effects
from ir_rx.nec import NEC_16

# ------------------------ WIFI ------------------------
SSID = "Pablo"
PASSWORD = "juan1234"

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            return True
        sleep_ms(500)
    return False

def sincronizar_hora():
    try:
        ntptime.settime()
    except:
        pass

def desconectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)

conectar_wifi()
sincronizar_hora()
desconectar_wifi()
gc.collect()

# ---------------- OLED ----------------
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

def obtener_hora():
    t = localtime()
    hora = (t[3] - 5) % 24
    return "{:02d}:{:02d}:{:02d}".format(hora, t[4], t[5])

ultimo_segundo = -1
def mostrar_hora():
    global ultimo_segundo
    t = localtime()
    if t[5] != ultimo_segundo:
        ultimo_segundo = t[5]
        oled.fill_rect(0, 0, 80, 10, 0)
        oled.text(obtener_hora(), 0, 0)

# ---------------- MIC ----------------
mic = ADC(Pin(35))
mic.atten(ADC.ATTN_11DB)

# ---------------- IR RX ----------------
codigo_ir = None

def ir_callback(data, addr, ctrl):
    global codigo_ir
    if data >= 0:
        codigo_ir = data

ir = NEC_16(Pin(17, Pin.IN), ir_callback)

# ---------------- IR TX (PIXMOB) ----------------
ledIR = PWM(Pin(5), freq=38000, duty=0)

def convertir_ms(color):
    res = []
    c = 1
    for i in range(1, len(color)):
        if color[i] == color[i-1]:
            c += 1
        else:
            res.append(c * 700)
            c = 1
    res.append(c * 700)
    return res

def enviar(color):
    # Bloquea poco (timing necesario), pero se llama espaciado por scheduler
    for i, d in enumerate(color):
        ledIR.duty(512 if i % 2 == 0 else 0)
        sleep_us(d)
    ledIR.duty(0)

color10 = convertir_ms(base_color_effects["GREEN_4"])
color56 = convertir_ms(base_color_effects["REDORANGE"])
weird   = convertir_ms(special_effects["WEIRD_110"])

# ---------------- CONTROL ----------------
estado = 0

def tarea_ir():
    global estado, codigo_ir
    if codigo_ir is None:
        return

    print("Boton:", codigo_ir)

    if codigo_ir == 4: estado = 1 , print("Pixmob")
    elif codigo_ir == 5: estado = 2 , print("Pixmob")
    elif codigo_ir == 7: estado = 3 , print("Pixmob")
    elif codigo_ir == 6: estado = 4 , print("Vumetro")
    elif codigo_ir == 0: estado = 5 ,   print("Scroll")
    elif codigo_ir == 1: estado = 6 ,  print("Icono")
    elif codigo_ir == 2: estado = 7 ,  print("Imagen")
    elif codigo_ir == 3: estado = 8 ,   print("Dibujo")
    elif codigo_ir == 8: estado = 9 ,   print("GC")

    codigo_ir = None

# ---------------- SCROLL (no bloqueante) ----------------
scroll_x = 128
scroll_texto = "QUE MAS PUES PARCE :)"

def tarea_scroll():
    global scroll_x

    if estado not in (0, 5):
        return

    oled.fill(0)
    mostrar_hora()
    oled.text(scroll_texto, scroll_x, 30)
    oled.show()

    scroll_x -= 2
    if scroll_x < -len(scroll_texto) * 8:
        scroll_x = 128

# ---------------- VUMETRO (no bloqueante real) ----------------
ANCHO = 128
ALTO = 64
CENTRO = ALTO // 2

x_vu = 0
offset = 0
contador_offset = 0
fase_offset = True

def mapear(v, in_min, in_max, out_min, out_max):
    return int((v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def tarea_vumetro():
    global x_vu, offset, contador_offset, fase_offset

    if estado != 4:
        return

    # Fase 1: calcular offset progresivo
    if fase_offset:
        offset += mic.read()
        contador_offset += 1

        if contador_offset >= 64:
            offset //= 64
            fase_offset = False
            x_vu = 0

            oled.fill(0)
            mostrar_hora()
            oled.hline(0, CENTRO, ANCHO, 1)
        return

    # Fase 2: dibujar punto por tick
    valor = mic.read() - offset
    y = mapear(valor, -1500, 1500, CENTRO + 20, CENTRO - 20)
    y = max(0, min(ALTO - 1, y))

    oled.pixel(x_vu, y, 1)
    x_vu += 1

    if x_vu % 16 == 0:
        oled.show()

    if x_vu >= ANCHO:
        oled.show()
        x_vu = 0
        offset = 0
        contador_offset = 0
        fase_offset = True

# ---------------- PIXMOB como tarea ----------------
t_anterior_ir_tx = 0

def tarea_pixmob():
    global t_anterior_ir_tx

    if estado not in (1, 2, 3):
        return

    ahora = ticks_ms()
    if ticks_diff(ahora, t_anterior_ir_tx) < 200:
        return

    t_anterior_ir_tx = ahora

    if estado == 1:
        enviar(color56)
    elif estado == 2:
        enviar(color10)
    elif estado == 3:
        enviar(weird)

# ---------------- IMAGEN ----------------
def modo_imagen():
    with open("ferrari.pbm", 'rb') as f:
        f.readline()
        f.readline()
        data = bytearray(f.read())

    fbuf = framebuf.FrameBuffer(data, 64, 64, framebuf.MONO_HLSB)
    oled.fill(0)
    mostrar_hora()
    oled.blit(fbuf, 32, 0)
    oled.show()

    del data
    del fbuf

# ---------------- DIBUJOS ----------------
def dibujo_geometrico():
    oled.fill(0)
    mostrar_hora()
    oled.rect(10, 10, 50, 30, 1)
    oled.fill_rect(70, 10, 40, 20, 1)
    oled.line(0, 63, 127, 0, 1)
    oled.line(0, 0, 127, 63, 1)
    oled.show()

def mostrar_icono():
    oled.fill(0)
    mostrar_hora()
    oled.text("ICONO", 30, 30)
    oled.show()

def tarea_display_estatico():
    if estado == 6:
        mostrar_icono()
    elif estado == 7:
        modo_imagen()
    elif estado == 8:
        dibujo_geometrico()

# ---------------- SCHEDULER ----------------
t_anterior_vu = 0
t_anterior_display = 0

INTERVALO_VU = 5
INTERVALO_DISPLAY = 40

# ---------------- LOOP PRINCIPAL ----------------
while True:

    ahora = ticks_ms()

    # 🔥 prioridad máxima
    tarea_ir()

    # tareas por tiempo
    if ticks_diff(ahora, t_anterior_vu) > INTERVALO_VU:
        t_anterior_vu = ahora
        tarea_vumetro()

    if ticks_diff(ahora, t_anterior_display) > INTERVALO_DISPLAY:
        t_anterior_display = ahora
        tarea_scroll()
        tarea_display_estatico()

    # independiente
    tarea_pixmob()

    sleep_ms(500)