import time
import tracemalloc
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import os
from colorama import init, Fore, Style


# Detectamos si estamos en Windows
if os.name == "nt":
    init()

grafo_prueba = {
    'A': {'B': 4, 'C': 2},
    'B': {'C': 5, 'D': 10},
    'C': {'D': 3},
    'D': {}
}


def dijkstra(grafo, inicio, objetivo):
    """Calcula la distancia más corta usando Dijkstra para verificar optimalidad"""
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    cola_prioridad = [(0, inicio)]

    while cola_prioridad:
        dist_actual, nodo_actual = heapq.heappop(cola_prioridad)

        if nodo_actual == objetivo:
            return dist_actual

        for vecino, peso in grafo[nodo_actual].items():
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                heapq.heappush(cola_prioridad, (nueva_dist, vecino))

    return float('inf')  # No se encontró camino


def formatear_tiempo(tiempo_segundos):
    if tiempo_segundos >= 1:
        return f"{tiempo_segundos:.2f} s"
    elif tiempo_segundos >= 1e-3:
        return f"{tiempo_segundos * 1e3:.2f} ms"
    elif tiempo_segundos >= 1e-6:
        return f"{tiempo_segundos * 1e6:.2f} µs"
    else:
        return f"{tiempo_segundos * 1e9:.2f} ns"


def mostrar_estadisticas(stats):
    print(
        f"\n{Fore.CYAN + Style.BRIGHT}📊 Estadísticas del Recorrido:{Style.RESET_ALL}\n")

    print(
        f"{Fore.YELLOW}🔵 Nodos visitados:{Style.RESET_ALL} {stats['Nodos visitados']}")
    print(
        f"{Fore.YELLOW}🟣 Nodos explorados:{Style.RESET_ALL} {stats['Nodos explorados']}")
    print(
        f"{Fore.GREEN}⏱️ Tiempo de ejecución:{Style.RESET_ALL} {stats['Tiempo de ejecución (s)']}")
    print(
        f"{Fore.MAGENTA}🧠 Memoria utilizada:{Style.RESET_ALL} {stats['Memoria utilizada (bytes)']} bytes")

    if stats['Es solución óptima']:
        print(
            f"{Fore.GREEN}✅ Es solución óptima:{Style.RESET_ALL} {stats['Es solución óptima']}")
    else:
        print(
            f"{Fore.RED}❌ Es solución óptima:{Style.RESET_ALL} {stats['Es solución óptima']}")

    if stats['Distancia DLS'] != float('inf'):
        print(
            f"{Fore.CYAN}📏 Distancia DLS:{Style.RESET_ALL} {stats['Distancia DLS']}")
    else:
        print(f"{Fore.RED}📏 Distancia DLS:{Style.RESET_ALL} No se encontró un camino")

    print(
        f"{Fore.BLUE}🎯 Distancia óptima (Dijkstra):{Style.RESET_ALL} {stats['Distancia óptima']}\n")


def algoritmo_busqueda(grafo, inicio, meta):
    """
    Implementación del algoritmo de búsqueda en profundidad limitada (DLS).

    :param grafo: Diccionario con listas de adyacencia.
    :param inicio: Nodo inicial.
    :param meta: Nodo meta.
    :return: Tupla con el camino encontrado (o None si no se encuentra) y estadísticas de rendimiento.
    """
    limite = int(input("Ingrese el límite de profundidad: "))
    tiempo_inicio = time.time()
    tracemalloc.start()  # Inicia el monitoreo de memoria

    def dls(nodo, meta, limite, visitados, camino, nodos_explorados):
        visitados.add(nodo)
        camino.append(nodo)
        nodos_explorados.append(nodo)

        if nodo == meta:
            return True

        if limite == 0:
            camino.pop()
            return False

        for vecino in grafo.get(nodo, {}):
            if vecino not in visitados:
                if dls(vecino, meta, limite - 1, visitados, camino, nodos_explorados):
                    return True

        camino.pop()
        return False

    visitados = set()
    camino = []
    nodos_explorados = []
    encontrado = dls(inicio, meta, limite, visitados, camino, nodos_explorados)

    # Estadísticas
    tiempo_total = time.time() - tiempo_inicio
    memoria_usada = tracemalloc.get_traced_memory()[1]  # Máximo uso de memoria
    tracemalloc.stop()

    distancia_dls = sum(grafo[camino[i]][camino[i + 1]]
                        for i in range(len(camino) - 1)) if encontrado else float('inf')
    distancia_optima = dijkstra(grafo, inicio, meta)
    es_optimo = distancia_dls == distancia_optima

    estadisticas = {
        "Nodos visitados": len(visitados),
        "Nodos explorados": len(nodos_explorados),
        "Tiempo de ejecución (s)": formatear_tiempo(tiempo_total),
        "Memoria utilizada (bytes)": memoria_usada,
        "Es solución óptima": es_optimo,
        "Distancia DLS": distancia_dls,
        "Distancia óptima": distancia_optima
    }

    return (camino if encontrado else None, nodos_explorados, estadisticas)


def graficar_recorrido(grafo, nodos_explorados, camino):
    """Genera una imagen con el recorrido del algoritmo y la guarda como PNG evitando que los recorridos choquen."""
    G = nx.DiGraph()

    # Agregar nodos y aristas con pesos
    for nodo, vecinos in grafo.items():
        for vecino, peso in vecinos.items():
            G.add_edge(nodo, vecino, weight=peso)

    pos = nx.kamada_kawai_layout(G)  # Usar un layout que minimice cruces

    # Dibujar todos los nodos y aristas
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color="lightgray",
            edge_color="gray", node_size=1500, font_size=12, arrows=True)

    # Resaltar nodos explorados
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_explorados,
                           node_color="blue", node_size=1500)

    # Resaltar camino final si existe
    if camino:
        edges_camino = [(camino[i], camino[i+1])
                        for i in range(len(camino) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges_camino,
                               edge_color="red", width=2.5, arrows=True, arrowstyle="-|>")
        nx.draw_networkx_nodes(G, pos, nodelist=camino,
                               node_color="red", node_size=1500)

    labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.title("Recorrido de Búsqueda en Profundidad Limitada")
    plt.savefig("recorrido_dls.png")  # Guardar imagen en archivo PNG
    plt.close()


# Entrada del usuario
inicio = input("Ingrese el nodo inicial: ").strip().upper()
meta = input("Ingrese el nodo meta: ").strip().upper()

# Ejecutar el algoritmo
resultado, explorados, stats = algoritmo_busqueda(grafo_prueba, inicio, meta)

# Mostrar resultados
if resultado:
    print(f"\nCamino encontrado: {' → '.join(resultado)}")
else:
    print("\nNo se encontró un camino dentro del límite especificado.")

mostrar_estadisticas(stats)

# Generar la imagen del recorrido
graficar_recorrido(grafo_prueba, explorados, resultado)
print("La imagen del recorrido ha sido guardada como 'recorrido_dls.png'")
