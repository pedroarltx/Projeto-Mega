import googlemaps
from tkinter import LEFT, RIGHT, GROOVE, FLAT, CENTER
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import tkinter as tk
from tkinter import messagebox

def obter_coordenadas(endereco, api_key):
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(endereco)
    if geocode_result:
        return geocode_result[0]['geometry']['location']
    return None

def calcular_distancia(coordenada1, coordenada2, api_key):
    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.distance_matrix(coordenada1, coordenada2, mode="driving", units="metric")
    distancia = result["rows"][0]["elements"][0]["distance"]["value"]
    return distancia

def organizar_rota(enderecos, api_key):
    coordenadas = []

    for endereco in enderecos:
        try:
            coordenada = obter_coordenadas(endereco, api_key)
            if coordenada:
                coordenadas.append(coordenada)
        except Exception as e:
            print(f"Erro ao obter coordenadas para o endereço {endereco}: {str(e)}")

    gerenciador = pywrapcp.RoutingIndexManager(len(coordenadas), 1, 0)
    modelo = pywrapcp.RoutingModel(gerenciador)

    def distance_callback(from_index, to_index):
        from_node = gerenciador.IndexToNode(from_index)
        to_node = gerenciador.IndexToNode(to_index)
        return calcular_distancia(coordenadas[from_node], coordenadas[to_node], api_key)

    transit_callback_index = modelo.RegisterTransitCallback(distance_callback)
    modelo.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    busca_parametros = pywrapcp.DefaultRoutingSearchParameters()
    busca_parametros.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    busca_parametros.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    busca_parametros.time_limit.FromSeconds(5)  # Limite de tempo de 5 segundos

    solucao = modelo.SolveWithParameters(busca_parametros)

    if solucao:
        rota_organizada = []
        indice = modelo.Start(0)
        while not modelo.IsEnd(indice):
            rota_organizada.append(enderecos[gerenciador.IndexToNode(indice)])
            indice = solucao.Value(modelo.NextVar(indice))
        return rota_organizada
    else:
        messagebox.showinfo("Erro", "Não foi possível calcular a rota.")
        return []


def adicionar_endereco():
    endereco = entry_endereco.get()

    if endereco:
        lista_enderecos.insert(tk.END, endereco)
        entry_endereco.delete(0, tk.END)

def limpar_enderecos():
    lista_enderecos.delete(0, tk.END)

def limpar_enderecos_e_resultado():
    limpar_enderecos()
    resultado.delete(1.0, tk.END)

def organizar_rota_interface():
    ponto_inicio = entry_ponto_inicio.get()
    enderecos = list(lista_enderecos.get(0, tk.END))

    if ponto_inicio and enderecos:
        rota_organizada = organizar_rota([ponto_inicio] + enderecos, api_key)
        resultado.config(state=tk.NORMAL)
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, "\n".join(rota_organizada))
        resultado.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Erro", "Informe o ponto de início e pelo menos um endereço.")


# Cria a janela principal
janela = tk.Tk()
janela.iconphoto(False, tk.PhotoImage(file='ROTAS MEGA/imagens/brasil.png'))
janela.title("ROTAS MEGALINK")
janela.geometry('415x555')
janela.config(bg='#04003b')
janela.resizable(width=0, height=0)

#Imagens
add_icon = tk.PhotoImage(file='ROTAS MEGA/imagens/botaoadd.png')
org_icon = tk.PhotoImage(file='ROTAS MEGA/imagens/button_organizar.png')
in_icon = tk.PhotoImage(file='ROTAS MEGA/imagens/inicio.png')
ende_icon = tk.PhotoImage(file='ROTAS MEGA/imagens/enderecos.png')
rota_icon = tk.PhotoImage(file='ROTAS MEGA/imagens/rota.png')
fundo_img = tk.PhotoImage(file='ROTAS MEGA/imagens/fundo.png')
limp_img = tk.PhotoImage(file='ROTAS MEGA/imagens/button_limpar.png')



#digite o ponto de inicio:
label_ponto_inicio = tk.Label(janela, image=in_icon, bg=('#04003b'))
label_ponto_inicio.grid(row=0, column=0, pady=2, padx=10)

#entrar com o ponto de inicio:
entry_ponto_inicio = tk.Entry(janela, width=65, bg=('white'))
entry_ponto_inicio.grid(row=1,column=0, pady=2, padx=10)

#digite os enderecos:
label_endereco = tk.Label(janela, image=ende_icon, bg=('#04003b'))
label_endereco.grid(row=2, column=0, pady=2, padx=10)

#entra com os enderecos:
entry_endereco = tk.Entry(janela, width=65, bg=('white'))
entry_endereco.grid(row=3, column=0, pady=2, padx=10)

#botao adicionar:
botao_adicionar = tk.Button(janela, command=adicionar_endereco, image=add_icon, compound=LEFT, bd=0, relief=FLAT, bg='#04003b', activebackground='#04003b')
botao_adicionar.grid(row=4, column=0, pady=2, padx=10)

#lista de enderecos:
lista_enderecos = tk.Listbox(janela, selectmode=tk.MULTIPLE, width=65, height=10, bg=('white'))
lista_enderecos.grid(row=5, column=0, pady=2, padx=10)

#botao organizar:
botao_organizar = tk.Button(janela, image=org_icon, compound=LEFT, command=organizar_rota_interface, bd=0, relief=GROOVE, bg='#04003b', activebackground='#04003b')
botao_organizar.grid(row=6, column=0, pady=2, padx=25, sticky='nsew')


#rota organizada:
label_resultado = tk.Label(janela, image=rota_icon, bg=('#04003b'))
label_resultado.grid(row=8, column=0, pady=2, padx=10)

#tela de resultados:
resultado = tk.Text(janela, width=55, height=10, state=tk.DISABLED, bg=('white'),font=('Open Sans', 9))
resultado.grid(row=9, column=0, pady=2, padx=10)

#botao limpar:
botao_limpar = tk.Button(janela, command=limpar_enderecos_e_resultado, image=limp_img, compound=LEFT, bd=0, relief=FLAT, bg='#04003b', activebackground='#04003b')
botao_limpar.grid(row=10, column=0, pady=2, padx=10, sticky='e')

resultado.grid()

# Chave da API do Google Maps
api_key = 'AIzaSyBRWG3EviGoCS4RERrpVSD9olqSer04wWg'
# Inicia a execução da interface


janela.mainloop()
