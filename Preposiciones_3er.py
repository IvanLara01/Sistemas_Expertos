import json
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk, filedialog
from itertools import product

# Lista para almacenar las reglas
reglas = []
mapa_proposiciones = {}  # Diccionario para mapear proposiciones a variables

# Función para abrir la ventana de reglas
def abrir_ventana_reglas():
    ventana_reglas = tk.Toplevel(ventana)
    ventana_reglas.title("Gestión de Reglas")
    ventana_reglas.geometry("400x300")
    
    # Listbox para mostrar reglas actuales
    lista_reglas = tk.Listbox(ventana_reglas)
    lista_reglas.pack(fill=tk.BOTH, expand=True)
    
    # Actualizar la lista al abrir la ventana
    actualizar_lista_reglas(lista_reglas)
    
    # Botón para guardar reglas en archivo
    boton_guardar = ttk.Button(ventana_reglas, text="Guardar Reglas", command=guardar_reglas)
    boton_guardar.pack(side=tk.LEFT, padx=10, pady=10)

    # Botón para cargar reglas desde archivo
    boton_cargar = ttk.Button(ventana_reglas, text="Cargar Reglas", command=lambda: cargar_reglas(lista_reglas))
    boton_cargar.pack(side=tk.RIGHT, padx=10, pady=10)
    
    # Conectar la selección de una regla a su modificación
    lista_reglas.bind('<Double-1>', lambda event: modificar_o_borrar_regla(event, lista_reglas))

# Función para abrir la ventana de átomos
def abrir_ventana_atomos():
    ventana_atomos = tk.Toplevel(ventana)
    ventana_atomos.title("Gestión de Átomos")
    ventana_atomos.geometry("400x300")
    
    # Listbox para mostrar átomos actuales
    lista_atomos = tk.Listbox(ventana_atomos)
    lista_atomos.pack(fill=tk.BOTH, expand=True)
    
    # Actualizar la lista al abrir la ventana
    actualizar_lista_atomos(lista_atomos)
    
    # Botón para actualizar la lista de átomos manualmente
    boton_actualizar = ttk.Button(ventana_atomos, text="Actualizar Lista", command=lambda: actualizar_lista_atomos(lista_atomos))
    boton_actualizar.pack(side=tk.BOTTOM, padx=10, pady=10)

# Función para actualizar la lista de reglas en el Listbox
# Función para actualizar la lista de reglas en el Listbox
def actualizar_lista_reglas(lista_reglas):
    lista_reglas.delete(0, tk.END)
    for index, regla in enumerate(reglas, start=1):  # Agrega un índice a cada regla, comenzando desde 1
        regla_texto = f"Proposición {index}: {regla['regla']}"  # Muestra el número de proposición y la regla
        lista_reglas.insert(tk.END, regla_texto)


# Función para actualizar la lista de átomos en el Listbox
def actualizar_lista_atomos(lista_atomos):
    lista_atomos.delete(0, tk.END)
    for proposicion, variable in mapa_proposiciones.items():
        lista_atomos.insert(tk.END, f"{variable}: {proposicion}")

# Función para guardar las reglas en un archivo JSON
def guardar_reglas():
    archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if archivo:
        with open(archivo, 'w') as f:
            json.dump(reglas, f)
        messagebox.showinfo("Guardar Reglas", "Reglas guardadas exitosamente.")

# Función para cargar reglas desde un archivo JSON
def cargar_reglas(lista_reglas):
    archivo = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if archivo:
        with open(archivo, 'r') as f:
            global reglas
            reglas = json.load(f)
        actualizar_lista_reglas(lista_reglas)
        messagebox.showinfo("Cargar Reglas", "Reglas cargadas exitosamente.")

# Función para identificar las proposiciones simples (átomos) en una regla
def identificar_proposiciones_simples(proposicion):
    proposiciones_simples = re.split(r' y | o ', proposicion)
    return [p.strip() for p in proposiciones_simples]

# Función para procesar y mostrar la proposición y agregarla como regla
def procesar_proposicion():
    proposicion = entrada_proposicion.get().lower()
    resultado = identificar_operadores(proposicion)
    if isinstance(resultado, tuple):
        global operadores, proposiciones_simples
        operadores, proposiciones_simples = resultado
        
        # Crear una lista para las variables
        variables = []
        
        for prop in proposiciones_simples:
            # Detectar negación si la proposición contiene "no"
            es_negada = "no " in prop
            prop_limpia = prop.replace("no ", "").strip()  # Elimina "no" para mapear correctamente
            
            # Si la proposición ya tiene una variable asignada, usarla
            if prop_limpia in mapa_proposiciones:
                variable = mapa_proposiciones[prop_limpia]
            else:
                # Crear una nueva variable
                variable = f'A{len(mapa_proposiciones) + 1}'
                mapa_proposiciones[prop_limpia] = variable
            
            # Agregar negación si corresponde
            variables.append(f"¬{variable}" if es_negada else variable)
        
        # Construir la fórmula
        formula = "{}".format(variables[0])
        for i in range(1, len(proposiciones_simples)):
            formula = f"({formula} {operadores[i-1]} {variables[i]})"
        
        detalle_proposiciones = "\n".join([f"{variables[i]}: {prop}" for i, prop in enumerate(proposiciones_simples)])
        
        # Guardar como nueva regla automáticamente
        reglas.append({'regla': proposicion, 'atomos': proposiciones_simples})
        etiqueta_resultado.config(text=f"Operadores identificados: {' '.join(op.upper() for op in operadores)}\n"
                                       f"Proposiciones simples:\n{detalle_proposiciones}\n"
                                       f"Fórmula: {formula}")
        boton_cerrar.pack()  # Mostrar el botón de cerrar
    else:
        etiqueta_resultado.config(text="Proposición no válida")

    print(formula)
    return formula 

# Función para identificar los operadores y separar en proposiciones simples
def identificar_operadores(proposicion):
    operadores = {' y ': '∧', ' o ': 'v'}
    proposiciones_simples = re.split(r' y | o ', proposicion)
    operadores_encontrados = [operadores[match.group()] for match in re.finditer(r' y | o ', proposicion)]
    if operadores_encontrados:
        return operadores_encontrados, [p.strip() for p in proposiciones_simples]
    else:
        return "Operador no reconocido. Usa 'y' para AND y 'o' para OR."

# (Continúa el # Función para modificar o borrar una regla
def modificar_o_borrar_regla(event, lista_reglas):
    indice_seleccionado = lista_reglas.curselection()
    if indice_seleccionado:
        indice = indice_seleccionado[0]
        regla_actual = reglas[indice]
        
        # Preguntar si modificar o borrar
        respuesta = messagebox.askquestion("Actualizar", f" Modificar (SI)  -  Borrar (NO)\n\n{regla_actual['regla']}", icon='question')
        
        if respuesta == 'yes':  # Modificar
            nueva_regla = simpledialog.askstring("Modificar Regla", "Introduce la nueva regla:", initialvalue=regla_actual['regla'])
            if nueva_regla:
                reglas[indice]['regla'] = nueva_regla
                reglas[indice]['atomos'] = identificar_proposiciones_simples(nueva_regla)
                actualizar_lista_reglas(lista_reglas)
                messagebox.showinfo("Regla Modificada", "Regla modificada exitosamente.")
        elif respuesta == 'no':  # Borrar
            reglas.pop(indice)
            actualizar_lista_reglas(lista_reglas)
            messagebox.showinfo("Regla Borrada", "Regla eliminada exitosamente.")
# Función para mostrar la tabla de verdad en una ventana
def mostrar_tabla_verdad(operadores):
    # Obtenemos las variables, asumiendo que `proposiciones_simples` está globalmente definido
    variables = [f'A{i+1}' for i in range(len(proposiciones_simples))]
    ventana_tabla = tk.Toplevel(ventana)
    ventana_tabla.title("Tabla de verdad")
    ventana_tabla.config(bg="#222222")

    texto = scrolledtext.ScrolledText(ventana_tabla, width=80, height=20, font=("Consolas", 12), bg="#333333", fg="#ffffff")
    texto.pack(padx=20, pady=20)

    # Encabezado de la tabla
    header = "".join(f"{v:<5}" for v in variables[:len(proposiciones_simples)]) + "Resultado\n"
    texto.insert(tk.END, header, "header")

    # Si solo hay una proposición, creamos la tabla básica para A1
    if len(proposiciones_simples) == 1:
        for valor in [1, 0]:
            resultado = valor
            texto.insert(tk.END, f"{valor:<5}{int(resultado)}\n", "row")
    else:
        # Si hay más de una proposición, procesamos con la lógica normal
        for valores in product([1, 0], repeat=len(proposiciones_simples)):
            valores_dict = dict(zip(variables[:len(proposiciones_simples)], valores))
            resultado = valores[0]
            for i in range(1, len(valores)):
                if operadores[i-1] == '∧':
                    resultado = resultado and valores[i]
                elif operadores[i-1] == 'v':
                    resultado = resultado or valores[i]
            texto.insert(tk.END, "".join([f"{val:<5}" for val in valores]) + f"{int(resultado)}\n", "row")

    texto.tag_configure("header", font=("Consolas", 12, "bold"), background="#555555")
    texto.tag_configure("row", font=("Consolas", 12), background="#333333")

    # Vinculamos el evento de cierre de la ventana para que abra la ventana del árbol
    ventana_tabla.protocol("WM_DELETE_WINDOW", lambda: [ventana_tabla.destroy(), mostrar_arbol()])


# Función para mostrar el diagrama de árbol
def mostrar_arbol():
    # Crear la ventana principal
    ventana_arbol = tk.Tk()
    ventana_arbol.title("Diagrama de árbol")

    # Crear un canvas para dibujar el árbol
    canvas = tk.Canvas(ventana_arbol, width=1200, height=1000, bg="#444444")
    canvas.pack()

    # Coordenadas iniciales y mayor espaciado entre nodos
    x0, y0 = 600, 50
    dx, dy = 200, 120

    # Mover las proposiciones simples a un costado y abajo del diagrama
    offset_x, offset_y = 50, 650
    for i, prop in enumerate(proposiciones_simples):
        canvas.create_text(offset_x, offset_y + (i * 20), 
                           text=f"A{i + 1}: {prop}", font=("Arial", 12, "bold"), fill="white", anchor="w")

    # Función auxiliar para calcular el resultado
    def evaluar_formula(valores):
        resultado = valores[0]
        for i in range(1, len(valores)):
            if operadores[i - 1] == '∧':
                resultado = resultado and valores[i]
            elif operadores[i - 1] == 'v':
                resultado = resultado or valores[i]
        return resultado

    # Función recursiva para dibujar el árbol
    def dibujar_nodo(x, y, nivel, valores_anteriores):
        if nivel < len(proposiciones_simples):
            # Nombre de la proposición actual y sus ramas
            nombre_proposicion = f"A{nivel + 1}"
            prop_text = proposiciones_simples[nivel]

            # Coordenadas para las ramas izquierda (valor 0) y derecha (valor 1) con mayor separación
            x_izq, x_der = x - dx / (2 ** (nivel - 1)), x + dx / (2 ** (nivel - 1))
            y_nuevo = y + dy

            # Ramas del lado izquierdo (0) y derecho (1)
            for valor, x_nuevo in [(0, x_izq), (1, x_der)]:
                etiqueta = f"{nombre_proposicion}={valor}"
                canvas.create_text(x_nuevo, y_nuevo, text=etiqueta, font=("Arial", 12), fill="white")
                canvas.create_line(x, y, x_nuevo, y_nuevo, fill="white")
                
                # Continuar dibujando hacia el siguiente nivel
                dibujar_nodo(x_nuevo, y_nuevo, nivel + 1, valores_anteriores + [valor])
        else:
            # Calcular y mostrar el resultado final al llegar al último nivel
            resultado = evaluar_formula(valores_anteriores)
            canvas.create_text(x, y + dy, text=f"R={resultado}", font=("Arial", 12), fill="white")
            canvas.create_line(x, y, x, y + dy, fill="white")

    # Dibujar el nodo raíz
    canvas.create_text(x0, y0, text=f"A1: {proposiciones_simples[0]}", font=("Arial", 12, "bold"), fill="white")
    
    # Iniciar la creación del árbol desde el primer nodo
    dibujar_nodo(x0, y0, 1, [])

    # Ejecutar el bucle principal de la ventana
    ventana_arbol.mainloop()
    
# Ventana principal
ventana = tk.Tk()
ventana.title("Lógica Proposicional")
ventana.geometry("800x600")
ventana.config(bg="#1e1e1e")

tk.Label(ventana, text="Introduce una proposición separada por 'y' (AND) y 'o' (OR):", font=("Helvetica", 12, "bold"), bg="#1e1e1e", fg="#ffffff").pack(pady=20)
entrada_proposicion = ttk.Entry(ventana, width=50, font=("Helvetica", 12))
entrada_proposicion.pack(pady=10)
boton_procesar = ttk.Button(ventana, text="Procesar", command=procesar_proposicion, style="TButton")
boton_procesar.pack(pady=10)
etiqueta_resultado = tk.Label(ventana, text="", font=("Helvetica", 12), bg="#ffffff", fg="#1e1e1e")
etiqueta_resultado.pack(pady=10)

# Botón para cerrar la ventana y mostrar la tabla y el diagrama
boton_cerrar = ttk.Button(ventana, text="Mostrar resultados", command=lambda: mostrar_tabla_verdad(operadores), style="TButton")
boton_cerrar.pack_forget()

# Botón para abrir la ventana de gestión de reglas
boton_reglas = ttk.Button(ventana, text="Reglas", command=abrir_ventana_reglas, style="TButton")
boton_reglas.pack(pady=10)

# Botón para abrir la ventana de gestión de átomos
boton_atomos = ttk.Button(ventana, text="Átomos", command=abrir_ventana_atomos, style="TButton")
boton_atomos.pack(pady=10)

ventana.mainloop()

