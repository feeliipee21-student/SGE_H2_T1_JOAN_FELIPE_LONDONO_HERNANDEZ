import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables globales para la conexión y el canvas del gráfico
db_connection = None
grafico_canvas = None  # Variable para el canvas del gráfico

# Colores de la paleta
BG_COLOR = "#f0f4f8"   # Fondo de la ventana
BUTTON_COLOR = "#6c8ebf"  # Botones y acentos
TEXT_COLOR = "#2d3e50"  # Color del texto
ENTRY_BG_COLOR = "#d9e3f0"  # Fondo de las entradas
LABEL_COLOR = "#4a6881"  # Color de las etiquetas
HIGHLIGHT_COLOR = "#f9e5e5"  # Fondo de las entradas seleccionadas o destacadas

# Configurar estilo de la aplicación con ttk.Style
def configurar_estilo():
    estilo = ttk.Style()
    estilo.theme_use("clam")  # Utilizar tema 'clam' para mejor personalización
    estilo.configure("TLabel", background=BG_COLOR, foreground=LABEL_COLOR, font=("Arial", 10))
    estilo.configure("TButton", background=BUTTON_COLOR, foreground="white", font=("Arial", 10, "bold"))
    estilo.configure("Treeview", background="white", fieldbackground="white", foreground=TEXT_COLOR)
    estilo.configure("TCombobox", background=ENTRY_BG_COLOR, fieldbackground=ENTRY_BG_COLOR, font=("Arial", 10))

# Solicitar credenciales y conectar a la base de datos al inicio
def iniciar_conexion():
    global db_connection
    # Usuario y contraseñas de tu base de datos
    usuario = "root"
    contrasena = "campusfp"

    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            user=usuario,
            password=contrasena,
            database="ENCUESTAS"
        )
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Error de conexión", f"Error al conectar con la base de datos: {err}")
        return False
    
# Ventana para agregar un nuevo registro
def abrir_ventana_agregar():
    ventana_agregar = tk.Toplevel(root)
    ventana_agregar.title("Agregar Nuevo Registro")
    ventana_agregar.geometry("400x450")
    # Crear campos de entrada para cada columna de la tabla
    fields = {
        "Edad": tk.IntVar(),
        "BebidasSemana": tk.IntVar(),
        "CervezasSemana": tk.IntVar(),
        "BebidasFinSemana": tk.IntVar(),
        "BebidasDestiladasSemana": tk.IntVar(),
        "VinosSemana": tk.IntVar(),
        "PerdidasControl": tk.IntVar()
    }
    
    # Crear entradas para los campos numéricos
    for i, (label, var) in enumerate(fields.items()):
        tk.Label(ventana_agregar, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(ventana_agregar, textvariable=var).grid(row=i, column=1, padx=10, pady=5, sticky="w")
    
    # Crear ComboBoxes para los campos con opciones específicas
    options = {
        "Sexo": ["", "Hombre", "Mujer"],
        "DiversionDependenciaAlcohol": ["", "Sí", "No"],
        "ProblemasDigestivos": ["", "Sí", "No"],
        "TensionAlta": ["", "Sí", "No", "No lo se"],
        "DolorCabeza": ["", "A menudo", "Alguna vez", "Nunca", "Muy a menudo"]
    }
    
    combo_vars = {}
    row_offset = len(fields)  # Para posicionar debajo de los campos numéricos

    for i, (label, values) in enumerate(options.items()):
        combo_vars[label] = tk.StringVar()
        tk.Label(ventana_agregar, text=label).grid(row=row_offset + i, column=0, padx=10, pady=5, sticky="e")
        combobox = ttk.Combobox(ventana_agregar, values=values, textvariable=combo_vars[label], state="readonly")
        combobox.grid(row=row_offset + i, column=1, padx=10, pady=5, sticky="w")

   # Función para insertar el nuevo registro en la base de datos, incluyendo idEncuesta
    def agregar_registro():
        try:
            # Validar que los campos numéricos contengan valores válidos
            for field_name, var in fields.items():
                if var.get() < 0:
                    messagebox.showerror("Error de Validación", f"El campo '{field_name}' debe ser un número positivo o cero.")
                    return

            # Validar que los campos de opciones no estén vacíos
            for field_name, var in combo_vars.items():
                if not var.get():
                    messagebox.showerror("Error de Validación", f"El campo '{field_name}' es obligatorio.")
                    return
            
            cursor = db_connection.cursor()
            
            # Obtener el último idEncuesta registrado en la base de datos
            cursor.execute("SELECT MAX(idEncuesta) FROM ENCUESTA")
            result = cursor.fetchone()
            ultimo_id = result[0] if result[0] is not None else 0
            nuevo_id = ultimo_id + 1  # Asignar el siguiente id disponible
            
            # Consulta de inserción con idEncuesta
            query = """
                INSERT INTO ENCUESTA (idEncuesta, edad, Sexo, BebidasSemana, CervezasSemana, BebidasFinSemana,
                BebidasDestiladasSemana, VinosSemana, PerdidasControl, DiversionDependenciaAlcohol,
                ProblemasDigestivos, TensionAlta, DolorCabeza)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Recolectar valores de campos numéricos y comboboxes
            data = (
                nuevo_id,
                fields["Edad"].get(),
                combo_vars["Sexo"].get(),
                fields["BebidasSemana"].get(),
                fields["CervezasSemana"].get(),
                fields["BebidasFinSemana"].get(),
                fields["BebidasDestiladasSemana"].get(),
                fields["VinosSemana"].get(),
                fields["PerdidasControl"].get(),
                combo_vars["DiversionDependenciaAlcohol"].get(),
                combo_vars["ProblemasDigestivos"].get(),
                combo_vars["TensionAlta"].get(),
                combo_vars["DolorCabeza"].get()
            )
            
            cursor.execute(query, data)
            db_connection.commit()
            messagebox.showinfo("Éxito", "Registro agregado exitosamente")
            ventana_agregar.destroy()
            realizar_consulta()  # Refresca la tabla principal
        except tk.TclError:
            messagebox.showerror("Error de Validación", "Todos los campos numéricos deben contener un número válido.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo agregar el registro: {err}")

    # Botón para agregar el registro
    tk.Button(ventana_agregar, text="Agregar Registro", command=agregar_registro).grid(row=row_offset + len(options), columnspan=2, pady=10)

# Consulta a la base de datos
def consultar_encuestas(edad=None, sexo=None, bebidas_semana=None, cervezas_semana=None,
                        bebidas_fin_semana=None, bebidas_destiladas_semana=None, vinos_semana=None,
                        perdidas_control=None, diversion_dependencia=None, problemas_digestivos=None,
                        tension_alta=None, dolor_cabeza=None):
    if not db_connection:
        messagebox.showerror("Error", "No hay conexión a la base de datos.")
        return []

    query = "SELECT * FROM ENCUESTA WHERE 1=1"
    params = []
    
    # Condicionales para hacer la consulta
    if edad:
        query += " AND edad >= %s"
        params.append(edad)
    if sexo:
        query += " AND Sexo = %s"
        params.append(sexo)
    if bebidas_semana:
        query += " AND BebidasSemana >= %s"
        params.append(bebidas_semana)
    if cervezas_semana:
        query += " AND CervezasSemana >= %s"
        params.append(cervezas_semana)
    if bebidas_fin_semana:
        query += " AND BebidasFinSemana >= %s"
        params.append(bebidas_fin_semana)
    if bebidas_destiladas_semana:
        query += " AND BebidasDestiladasSemana >= %s"
        params.append(bebidas_destiladas_semana)
    if vinos_semana:
        query += " AND VinosSemana >= %s"
        params.append(vinos_semana)
    if perdidas_control:
        query += " AND PerdidasControl >= %s"
        params.append(perdidas_control)
    if diversion_dependencia:
        query += " AND DiversionDependenciaAlcohol = %s"
        params.append(diversion_dependencia)
    if problemas_digestivos:
        query += " AND ProblemasDigestivos = %s"
        params.append(problemas_digestivos)
    if tension_alta:
        query += " AND TensionAlta = %s"
        params.append(tension_alta)
    if dolor_cabeza:
        query += " AND DolorCabeza = %s"
        params.append(dolor_cabeza)
    
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(query, params)
    data = cursor.fetchall()
    return data

# Exportar a Excel
def export_to_excel(data):
    if not data:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    df = pd.DataFrame(data)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Exportación", "Datos exportados a Excel exitosamente.")

# Exportar a PDF
def export_to_pdf(data):
    if not data:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica", 8)  # Fuente más pequeña

        c.drawString(50, height - 50, "Datos de Encuesta Consultados")

        y = height - 80
        headers = ["ID", "Edad", "Sexo", "Bebidas/Semana", "Cervezas/Semana", "Bebidas Fin Semana", 
                   "Bebidas Destiladas / Semana", "Vino/Semana", "Pérdidas de Control", 
                   "Diversión/Dependencia", "Problemas Digestivos", "Tensión Alta", "Dolor de Cabeza"]

        # Ajustar espaciado entre columnas
        x_positions = [50, 80, 120, 160, 200, 250, 300, 350, 400, 450, 500, 550, 600]

        # Dibujar encabezados
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y, header)
        y -= 15

        # Dibujar filas de datos
        for row in data:
            for i, value in enumerate(row.values()):
                c.drawString(x_positions[i], y, str(value))
            y -= 12

            # Crear nueva página si el espacio se acaba
            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 8)  # Reestablecer fuente en nueva página
                y = height - 80

        c.save()
        messagebox.showinfo("Exportación", "Datos exportados a PDF exitosamente.")


# def actualizar registros
def actualizar_registro():
    selected_item = tree.focus()  # Obtener el registro seleccionado en el Treeview
    if not selected_item:
        messagebox.showerror("Error", "Por favor, selecciona un registro para actualizar.")
        return

    # Obtener valores actuales del registro seleccionado
    item_values = tree.item(selected_item, "values")
    record_id = item_values[0]

    # Crear un nuevo cuadro de diálogo para actualizar todos los campos a la vez
    top = tk.Toplevel(root)
    top.title("Actualizar Registro")
    
    # Etiquetas y campos de entrada para actualizar los valores
    tk.Label(top, text="ID (No editable):").grid(row=0, column=0, sticky="w")
    id_label = tk.Label(top, text=record_id)
    id_label.grid(row=0, column=1)

    tk.Label(top, text="Nueva Edad:").grid(row=1, column=0, sticky="w")
    nueva_edad = tk.Entry(top)
    nueva_edad.insert(0, item_values[1])
    nueva_edad.grid(row=1, column=1)

    tk.Label(top, text="Nuevo Sexo:").grid(row=2, column=0, sticky="w")
    nuevo_sexo = ttk.Combobox(top, values=["Hombre", "Mujer"])
    nuevo_sexo.set(item_values[2])
    nuevo_sexo.grid(row=2, column=1)

    tk.Label(top, text="Nuevas Bebidas por Semana:").grid(row=3, column=0, sticky="w")
    nuevas_bebidas = tk.Entry(top)
    nuevas_bebidas.insert(0, item_values[3])
    nuevas_bebidas.grid(row=3, column=1)

    # Botón para guardar los cambios
    def guardar_cambios():
        # Validar entradas
        if not nueva_edad.get().isdigit() or nuevo_sexo.get() not in ["Hombre", "Mujer"] or not nuevas_bebidas.get().isdigit():
            messagebox.showerror("Error", "Por favor, ingrese datos válidos.")
            return

        # Actualizar en la base de datos
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE ENCUESTA
                SET Edad = %s, Sexo = %s, BebidasSemana = %s
                WHERE idEncuesta = %s
            """, (int(nueva_edad.get()), nuevo_sexo.get(), int(nuevas_bebidas.get()), record_id))
            db_connection.commit()
            messagebox.showinfo("Éxito", "Registro actualizado exitosamente.")
            top.destroy()
            
            # Actualizar la tabla
            realizar_consulta()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {err}")
                # Botón para guardar los cambios
    guardar_button = tk.Button(top, text="Guardar Cambios", command=guardar_cambios)
    guardar_button.grid(row=4, columnspan=2, pady=10)

# Función para eliminar un registro
def eliminar_registro():
    selected_item = tree.focus()  # Obtener el registro seleccionado en el Treeview
    if not selected_item:
        messagebox.showerror("Error", "Por favor, selecciona un registro para eliminar.")
        return

    # Confirmación de eliminación
    if not messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este registro? Esta acción no se puede deshacer."):
        return

    # Obtener el ID del registro seleccionado
    item_values = tree.item(selected_item, "values")
    record_id = item_values[0]

    # Eliminar de la base de datos
    try:
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM ENCUESTA WHERE idEncuesta = %s", (record_id,))
        db_connection.commit()
        messagebox.showinfo("Éxito", "Registro eliminado exitosamente.")
        
        # Actualizar la tabla
        realizar_consulta()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo eliminar el registro: {err}")

# Función para limpiar los campos de filtro y mostrar todos los datos
def limpiar_campos():
    # Limpiar campos de entrada
    edad_entry.delete(0, tk.END)
    bebidas_entry.delete(0, tk.END)
    cervezas_entry.delete(0, tk.END)
    bebidas_fin_semana_entry.delete(0, tk.END)
    bebidas_destiladas_entry.delete(0, tk.END)
    vinos_entry.delete(0, tk.END)
    control_entry.delete(0, tk.END)

    # Limpiar Comboboxes
    sexo_combobox.set("")
    diversion_combobox.set("")
    digestivos_combobox.set("")
    tension_combobox.set("")
    cabeza_combobox.set("")
    order_combobox.set("")

    # Actualizar la tabla después de limpiar los filtros
    realizar_consulta()


def realizar_consulta():
    # Obtener valores de los campos de filtro
    edad = edad_entry.get()
    sexo = sexo_combobox.get()
    bebidas_semana = bebidas_entry.get()
    cervezas_semana = cervezas_entry.get()
    bebidas_fin_semana = bebidas_fin_semana_entry.get()
    bebidas_destiladas_semana = bebidas_destiladas_entry.get()
    vinos_semana = vinos_entry.get()
    perdidas_control = control_entry.get()
    diversion_dependencia = diversion_combobox.get()
    problemas_digestivos = digestivos_combobox.get()
    tension_alta = tension_combobox.get()
    dolor_cabeza = cabeza_combobox.get()
    
    # Convertir los valores numéricos a enteros si están definidos
    edad = int(edad) if edad else None
    bebidas_semana = int(bebidas_semana) if bebidas_semana else None
    cervezas_semana = int(cervezas_semana) if cervezas_semana else None
    bebidas_fin_semana = int(bebidas_fin_semana) if bebidas_fin_semana else None
    bebidas_destiladas_semana = int(bebidas_destiladas_semana) if bebidas_destiladas_semana else None
    vinos_semana = int(vinos_semana) if vinos_semana else None
    perdidas_control = int(perdidas_control) if perdidas_control else None
    
    # Llamar a la función para consultar todos los registros
    data = consultar_encuestas(
        edad=edad, sexo=sexo, bebidas_semana=bebidas_semana, cervezas_semana=cervezas_semana,
        bebidas_fin_semana=bebidas_fin_semana, bebidas_destiladas_semana=bebidas_destiladas_semana,
        vinos_semana=vinos_semana, perdidas_control=perdidas_control,
        diversion_dependencia=diversion_dependencia, problemas_digestivos=problemas_digestivos,
        tension_alta=tension_alta, dolor_cabeza=dolor_cabeza
    )

    # Limpiar el Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Insertar datos en el Treeview
    for record in data:
        tree.insert("", "end", values=tuple(record.values()))

    # Guardar los datos de la consulta en una variable global para otros usos
    global consulta_data
    consulta_data = data

# Función para realizar la consulta de orden
def ordenar_datos():
    global consulta_data  # Declaración global al inicio de la función

    # Obtiene el campo de orden del Combobox
    campo_orden = order_combobox.get()
    if campo_orden:
        query = f"SELECT * FROM ENCUESTA ORDER BY {campo_orden}"
        
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute(query)
            consulta_data = cursor.fetchall()
            
            # Limpiar el Treeview antes de mostrar los datos ordenados
            for item in tree.get_children():
                tree.delete(item)

            # Insertar los datos ordenados en el Treeview
            for record in consulta_data:
                tree.insert("", "end", values=tuple(record.values()))

            # Mostrar un mensaje de éxito si todo sale bien
            messagebox.showinfo("Éxito", f"Datos ordenados por {campo_orden} correctamente.")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo ordenar los datos: {err}")

# Crear gráficos
def mostrar_grafico(data, tipo):
    global grafico_canvas

    if not data:
        messagebox.showerror("Error", "No hay datos para mostrar en el gráfico.")
        return
    
    # Limpiar el gráfico anterior si existe
    if grafico_canvas:
        grafico_canvas.get_tk_widget().pack_forget()
        grafico_canvas = None

    df = pd.DataFrame(data)
    
    if tipo == "Barras":
        # Agrupar por Sexo para mostrar el consumo de bebidas semanal
        if "Sexo" in df.columns:
            df_barras = df.groupby("Sexo")["BebidasSemana"].sum()
            fig, ax = plt.subplots()
            df_barras.plot(kind='bar', ax=ax)
            ax.set_title("Consumo de Bebidas Semanal por Sexo")
            ax.set_xlabel("Sexo")
            ax.set_ylabel("Bebidas por Semana")
        else:
            messagebox.showerror("Error", "No hay datos para mostrar en el gráfico de barras.")
            return
        
    elif tipo == "Circular":
        df_pie = df.groupby("Sexo")["BebidasSemana"].sum()
        fig, ax = plt.subplots()
        df_pie.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title("Distribución del Consumo de Bebidas por Sexo")
        ax.set_ylabel("")

    grafico_canvas = FigureCanvasTkAgg(fig, master=root)
    grafico_canvas.draw()
    grafico_canvas.get_tk_widget().pack()
    plt.close(fig)

# Configuración de la interfaz de Tkinter
root = tk.Tk()
root.title("Consulta de Encuestas")
root.geometry("1600x720")

if not iniciar_conexion():
    root.destroy()
else:
    configurar_estilo()

    # Título de la aplicación
    titulo_frame = tk.Frame(root, bg=BG_COLOR)
    titulo_frame.pack(pady=20)

    titulo_label = tk.Label(
        titulo_frame,
        text="Gestión de Inventario",
        font=("Helvetica", 24, "bold"),
        bg=BG_COLOR,
        fg="black"
    )
    titulo_label.pack()

    # Sección de filtros
    filter_frame = tk.Frame(root, bg=BG_COLOR)
    filter_frame.pack(pady=10)

    # Primera columna de filtros
    ttk.Label(filter_frame, text="Mínimo de Edad:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    edad_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    edad_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Sexo:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    sexo_combobox = ttk.Combobox(filter_frame, values=["", "Hombre", "Mujer"], style="TCombobox")
    sexo_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Mínimo Bebidas por Semana:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    bebidas_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    bebidas_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Mínimo Cervezas por Semana:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    cervezas_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    cervezas_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Mínimo Bebidas Fin de Semana:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    bebidas_fin_semana_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    bebidas_fin_semana_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Mínimo Bebidas Destiladas por Semana:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    bebidas_destiladas_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    bebidas_destiladas_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    # Segunda columna de filtros
    ttk.Label(filter_frame, text="Vinos por Semana (Mínimo):").grid(row=0, column=2, padx=10, pady=5, sticky="e")
    vinos_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    vinos_entry.grid(row=0, column=3, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Pérdidas de Control (Mínimo):").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    control_entry = tk.Entry(filter_frame, bg=ENTRY_BG_COLOR, highlightbackground=HIGHLIGHT_COLOR)
    control_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Diversión Dependencia de Alcohol:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
    diversion_combobox = ttk.Combobox(filter_frame, values=["", "Sí", "No"], style="TCombobox")
    diversion_combobox.grid(row=2, column=3, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Problemas Digestivos:").grid(row=3, column=2, padx=10, pady=5, sticky="e")
    digestivos_combobox = ttk.Combobox(filter_frame, values=["", "Sí", "No"], style="TCombobox")
    digestivos_combobox.grid(row=3, column=3, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Tensión Alta:").grid(row=4, column=2, padx=10, pady=5, sticky="e")
    tension_combobox = ttk.Combobox(filter_frame, values=["", "Sí", "No", "No lo sé"], style="TCombobox")
    tension_combobox.grid(row=4, column=3, padx=10, pady=5, sticky="w")

    ttk.Label(filter_frame, text="Dolor de Cabeza:").grid(row=5, column=2, padx=10, pady=5, sticky="e")
    cabeza_combobox = ttk.Combobox(filter_frame, values=["", "A menudo", "Alguna Vez", "Nunca", "Muy a menudo"], style="TCombobox")
    cabeza_combobox.grid(row=5, column=3, padx=10, pady=5, sticky="w")

    # Sección de botones de filtro
    button_and_export_frame = tk.Frame(root, bg=BG_COLOR)
    button_and_export_frame.pack(pady=10)

    # Centramos los botones en el frame
    consulta_button = tk.Button(button_and_export_frame, text="Filtrar", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=realizar_consulta)
    consulta_button.grid(row=0, column=0, padx=5, pady=5)

    actualizar_button = tk.Button(button_and_export_frame, text="Actualizar", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=actualizar_registro)
    actualizar_button.grid(row=0, column=1, padx=5, pady=5)

    eliminar_button = tk.Button(button_and_export_frame, text="Eliminar", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=eliminar_registro)
    eliminar_button.grid(row=0, column=2, padx=5, pady=5)

    limpiar_button = tk.Button(button_and_export_frame, text="Limpiar Campos", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=limpiar_campos)
    limpiar_button.grid(row=0, column=3, padx=5, pady=5)

    export_excel_button = tk.Button(button_and_export_frame, text="Exportar a Excel", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=lambda: export_to_excel(consulta_data))
    export_excel_button.grid(row=0, column=4, padx=10, pady=5)

    export_pdf_button = tk.Button(button_and_export_frame, text="Exportar a PDF", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=lambda: export_to_pdf(consulta_data))
    export_pdf_button.grid(row=0, column=5, padx=10, pady=5)

    agregar_button = tk.Button(button_and_export_frame, text="Agregar Registro", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=abrir_ventana_agregar)
    agregar_button.grid(row=0, column=6, padx=5, pady=5)

    # Configuración del Combobox de orden y el botón
    order_button = tk.Button(button_and_export_frame, text="Ordenar Campos", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=ordenar_datos)
    order_button.grid(row=0, column=7, padx=10, pady=5)

    order_combobox = ttk.Combobox(button_and_export_frame, values=[
        "edad", "Sexo", "BebidasSemana", "CervezasSemana", "BebidasFinSemana", 
        "BebidasDestiladasSemana", "VinosSemana", "PerdidasControl", 
        "DiversionDependenciaAlcohol", "ProblemasDigestivos", 
        "TensionAlta", "DolorCabeza"
    ], style="TCombobox")
    order_combobox.grid(row=0, column=8, padx=10, pady=5, sticky="w")

    # Tabla Treeview
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, pady=10, padx=20)

    tree = ttk.Treeview(tree_frame, columns=("ID", "Edad", "Sexo", "Bebidas/Semana", "Cervezas/Semana", "Bebidas Fin Semana", "Bebidas Destiladas / Semana", "Vino/Semana", "Pérdidas de Control", "Diversión/Dependencia", "Problemas Digestivos", "Tensión Alta", "Dolor de Cabeza"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Barra de desplazamiento
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Sección de gráficos y exportación
    export_frame = tk.Frame(root, bg=BG_COLOR)
    export_frame.pack(pady=10)

    grafico_tipo = tk.StringVar(value="Barras")
    tk.Radiobutton(export_frame, text="Barras", variable=grafico_tipo, value="Barras", bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=HIGHLIGHT_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Radiobutton(export_frame, text="Circular", variable=grafico_tipo, value="Circular", bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=HIGHLIGHT_COLOR).grid(row=0, column=1, padx=10, pady=5, sticky="w")

    grafico_button = tk.Button(export_frame, text="Mostrar Gráfico", bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"), command=lambda: mostrar_grafico(consulta_data, grafico_tipo.get()))
    grafico_button.grid(row=0, column=2, padx=10, pady=5)

    

    # Llamar a realizar_consulta al iniciar la aplicación para mostrar todos los datos
    realizar_consulta()

root.mainloop()
