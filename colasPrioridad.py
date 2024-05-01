import random
from datetime import timedelta
import simpy
import math
import flet as ft
# Datos iniciales aleatorios
semilla = 30

#Parte del Backend

#Variables de los impus
tmp_min = None
tmp_max = None
tmp_prom_llegada = None
n_clientes = None
n_cajeros = None

# Variables globales
num_cajeros = n_cajeros
tiempo_atencion_min = 1
tiempo_atencion_max = 10
tiempo_prom_llegada = 5
total_clientes = 10
tiempo_total_espera = 0
duracion_servicio = 0
fin_servicio = 0
prioridad_dolares = 0.5 # Probabilidad de que un cliente pague en dólares



class Tiempos():

    def __init__(self, tiempo_atencion_min, tiempo_atencion_max, tiempo_prom_llegada,tiempo_total_espera,duracion_servicio,fin_servicio):
        self.tiempo_atencion_min = tiempo_atencion_min
        self.tiempo_atencion_max = tiempo_atencion_max
        self.tiempo_prom_llegada = tiempo_prom_llegada
        self.tiempo_total_espera = tiempo_total_espera
        self.duracion_servicio = duracion_servicio
        self.fin_servicio = fin_servicio
    def get_tiempo_atencion_min(self):
        return self.tiempo_atencion_min
    def get_tiempo_atencion_max(self):
        return self.tiempo_atencion_max
    def get_tiempo_prom_llegada(self):
        return self.tiempo_prom_llegada
    def get_tiempo_total_espera(self):
        return self.tiempo_total_espera
    def get_duracion_servicio(self):
        return self.duracion_servicio
    def get_fin_servicio(self):
        return self.fin_servicio
    def set_tiempo_total_espera(self, tiempo_total_espera):
        self.tiempo_total_espera = tiempo_total_espera
    def set_duracion_servicio(self, duracion_servicio):
        self.duracion_servicio = duracion_servicio
    def set_fin_servicio(self, fin_servicio):
        self.fin_servicio = fin_servicio
    def set_tiempo_prom_llegada(self, tiempo_prom_llegada):
        self.tiempo_prom_llegada = tiempo_prom_llegada
    def set_tiempo_atencion_max(self, tiempo_atencion_max):
        self.tiempo_atencion_max = tiempo_atencion_max
    def set_tiempo_atencion_min(self, tiempo_atencion_min):
        self.tiempo_atucion_min = tiempo_atencion_min

tiempos = Tiempos(tiempo_atencion_min, tiempo_atencion_max, tiempo_prom_llegada,tiempo_total_espera,duracion_servicio,fin_servicio)
class Cobrar:
    def __init__(self, env, name_cliente, prioridad):
        self.env = env
        self.name_cliente = name_cliente
        self.prioridad = prioridad
        time_max = tiempos.get_tiempo_atencion_max()
        time_min = tiempos.get_tiempo_atencion_min()
        self.tiempo =  time_max - time_min
        self.tiempo_atencion_cliente = tiempo_atencion_min + self.tiempo * random.random()

    def cobrar(self):
        yield self.env.timeout(self.tiempo_atencion_cliente)
        print(f"El cobro de {self.name_cliente} {'en BS' if self.prioridad == 0 else 'en $'} se realizó en: {self.tiempo_atencion_cliente:.2f}")
        global duracion_servicio
        duracion_servicio += self.tiempo_atencion_cliente



class Cliente:
    def __init__(self, env, name, cajero, prioridad):
        global tiempo_total_espera
        global fin_servicio
        self.env = env
        self.cajero = cajero
        self.prioridad = prioridad
        self.name = name

    def cliente(self):
        llegada = self.env.now
        with self.cajero.request() as req:
            yield req
            espera = self.env.now - llegada
            global tiempo_total_espera
            tiempo_total_espera += espera
            print(f"El cliente {self.name} se atendio a las: {self.env.now:.2f} y espero: {tiempo_total_espera:.2f}")
            nuevo_cobro =Cobrar(self.env, self.name, self.prioridad)
            yield self.env.process(nuevo_cobro.cobrar())
            global fin_servicio
            fin_servicio = self.env.now
            print(f"El cliente {self.name} se fue a las: {fin_servicio:.2f}\n")

class Principal:
    def __init__(self, env, cajeros,total_clientes):
        self.env = env
        self.cajeros = cajeros
        self.clientes_prioridad = []
        self.incremento = 0
        self.name = ''
        self.prioridad = 0
        self.total_clientes = total_clientes

    def inicio(self):
        for i in range(self.total_clientes):
            r = random.random()
            tiempo_prom_llegada_resultado = tiempos.get_tiempo_prom_llegada()
            llegada = -tiempo_prom_llegada_resultado * (math.log(r))
            yield self.env.timeout(llegada)
            self.incremento += 1
            self.name = f"cliente {i}"
            self.prioridad = 1 if random.random() < prioridad_dolares else 0
            self.clientes_prioridad.append((self.name, self.prioridad))
        # Ordenar los clientes por prioridad
        self.clientes_prioridad.sort(key=lambda x: x[1], reverse=True)
        for name, prioridad in self.clientes_prioridad:
            new_client = Cliente(self.env, name, self.cajeros, prioridad)
            self.env.process(new_client.cliente())


# Funciones para manejar los cambios en los TextField
def on_num_cajeros_change(e):
    global n_cajeros
    n_cajeros = int(e.control.value)


def on_tiempo_atencion_min_change(e):
    global tmp_min
    tmp_min = int(e.control.value)
    tiempos.set_tiempo_atencion_min(tmp_min)

def on_tiempo_atencion_max_change(e):
    global tmp_max
    tmp_max = int(e.control.value)
    tiempos.set_tiempo_atencion_max(tmp_max)

def on_tiempo_prom_llegada_change(e):
    global tmp_prom_llegada
    tmp_prom_llegada = int(e.control.value)
    tiempos.set_tiempo_prom_llegada(tmp_prom_llegada)

def on_total_clientes_change(e):
    global n_clientes
    n_clientes = int(e.control.value)



#Accion del boton
def button_clicked(e):
    print("---------------Simulacion de colas de prioridad------------------------")
    random.seed(semilla)
    env = simpy.Environment()
    cajeros = simpy.Resource(env, n_cajeros)
    simulacion = Principal(env, cajeros,n_clientes)
    env.process(simulacion.inicio())
    env.run()

    # Salidas
    result_text = "indicadores de tiempo:\n"
    lpc = tiempo_total_espera / fin_servicio
    lpc = timedelta(minutes=lpc)
    result_text += f"Longitud promedio de la cola: {lpc} minutos\n"
    tep = tiempo_total_espera / total_clientes
    tep = timedelta(minutes=tep)
    result_text += f"Tiempo promedio de espera: {tep} minutos\n"
    upi = (duracion_servicio / fin_servicio) / n_cajeros
    upi = timedelta(minutes=upi)
    result_text += f"Utilizacion promedio de caja por cajero: {upi} minutos\n"
    print(result_text)
    # Actualizar el contenido del TextField de resultados



# Estilos principales de la app parte Frontend

first_column = ft.Column(
        [
            ft.Container(
                ft.Text(
                    'Farmatodo',
                    width=300,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                margin=ft.margin.only(top=15,bottom=10),
                padding= ft.padding.only(20,20),

            ),
            ft.Container(
                ft.TextField(
                    label="Numero de cajeros:",
                    width=280,
                    height=40,
                    border_radius=ft.border_radius.all(20),
                    prefix_icon=ft.icons.SUPERVISED_USER_CIRCLE_ROUNDED,
                    border_color=ft.colors.WHITE,
                    on_change=on_num_cajeros_change,                    
                ),
                padding= ft.padding.only(20,20),
                alignment= ft.alignment.center,
                margin=ft.margin.only(top=40),
            ),
            ft.Container(
                ft.TextField(
                    label="Tiempo atencion min:",
                    width=280,
                    height=40,
                    border_radius=ft.border_radius.all(20),
                    prefix_icon=ft.icons.ACCESS_TIME,
                    border_color=ft.colors.WHITE,
                    on_change=on_tiempo_atencion_min_change,
                ),
                alignment= ft.alignment.center,
                padding= ft.padding.only(20,20),
            ),
            ft.Container(
                ft.TextField(
                    label="Tiempo atencion max:",
                    width=280,
                    height=40,
                    border_radius=ft.border_radius.all(20),
                    prefix_icon=ft.icons.ACCESS_TIME_FILLED,
                    border_color=ft.colors.WHITE,
                    on_change=on_tiempo_atencion_max_change,

                ),
                padding= ft.padding.only(20,20),
                alignment= ft.alignment.center
            ),
            ft.Container(
                ft.TextField(
                    label="Tiempo de llegada:",
                    width=280,
                    height=40,
                    border_radius=ft.border_radius.all(20),
                    prefix_icon=ft.icons.ACCESS_TIME,
                    border_color=ft.colors.WHITE,
                    on_change=on_tiempo_prom_llegada_change,
                ),
                alignment= ft.alignment.center,
                padding= ft.padding.only(20,20),
            ),
            ft.Container(
                ft.TextField(
                    label="Total de clientes:",
                    width=280,
                    height=40,
                    border_radius=ft.border_radius.all(20),
                    prefix_icon=ft.icons.SUPERVISED_USER_CIRCLE_ROUNDED,
                    border_color=ft.colors.WHITE,
                    on_change=on_total_clientes_change,
                ),
                alignment= ft.alignment.center,
                padding= ft.padding.only(20,20),
            ),
            
            ft.Container(
                ft.ElevatedButton(
                    "Iniciar",
                    width=280,
                    height=40,
                    bgcolor=ft.colors.BLACK,
                    on_click=button_clicked,
                ),
                padding= ft.padding.only(20,20),
            )
        ],
        height= 610,
)

result_column = ft.Column(
        [
             ft.Container(
                ft.TextField(
                    width=350,
                    height=100,
                    border_radius=ft.border_radius.all(5),
                    multiline=True,
                    border_color=ft.colors.WHITE,
                ),
                 alignment= ft.alignment.center,
                padding= ft.padding.only(20,20),
                margin=ft.margin.only(top=-50,left=145),
            ),
            ft.Container(
                ft.Text(
                    'Resultados',
                    width=300,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                margin=ft.margin.only(top=-230,left=250, bottom=50),
                width= 165,
            ),
           


        ],
        alignment=ft.MainAxisAlignment.CENTER, 
    

)

# Crear la fila con las dos columnas
row_container = ft.Container(
    ft.Row([first_column]),
    #width = 920,
    width = 320,
    height= 610,
    gradient= ft.LinearGradient(
        [
            ft.colors.PURPLE,
            ft.colors.BLUE
        ]
    ),
    border_radius=ft.border_radius.all(20),

)

#contenedor principal
container = row_container

def main(page: ft.Page):

    page.title = "Simulacion de colas de prioridad"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(container)
    page.update()



ft.app(target=main)