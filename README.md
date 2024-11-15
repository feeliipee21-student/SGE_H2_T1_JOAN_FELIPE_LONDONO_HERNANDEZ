# SGE_H2_T1_JOAN_FELIPE_LONDONO_HERNANDEZ
Hito segundo del primer trimeste de DAM

# Gestión de Encuestas Demográficas

Esta aplicación permite gestionar y analizar datos demográficos de encuestas, realizando operaciones CRUD (Crear, Leer, Actualizar, Eliminar) y generando gráficos estadísticos. Además, permite exportar resultados en formatos Excel y PDF.

---

## Requisitos Previos

### Instalar Tkinter
Tkinter viene incluido en la mayoría de las distribuciones de Python. Si no lo tienes, instálalo ejecutando:
sudo apt-get install python3-tk    # En Linux

### Instalar ttk, messagebox y filedialog
Estas sublibrerías están incluidas dentro del módulo tkinter y no requieren instalación adicional.

### Instalar Pandas
Pandas es una librería para el manejo y análisis de datos tabulares. Instálalo ejecutando:
pip install pandas

### Instalar ReportLab
ReportLab permite la generación de documentos PDF en Python. Instálalo ejecutando:
Copiar código
pip install reportlab

### Instalar MySQL Connector
Esta librería permite la conexión de aplicaciones Python con bases de datos MySQL. Instálalo ejecutando:
Copiar código
pip install mysql-connector-python

### Instalar Matplotlib
Matplotlib es una librería para crear gráficos. Instálalo ejecutando:
Copiar código
pip install matplotlib

### Instalar Backends de Matplotlib para Tkinter
El soporte para integrar Matplotlib con interfaces de Tkinter está incluido en Matplotlib, por lo que no requiere instalación adicional.

### Funcionalidades
Crear Encuestas: Agrega nuevos registros de encuestas.
Leer Encuestas: Consulta registros y filtra datos según criterios.
Actualizar Encuestas: Edita datos existentes en la base de datos.
Eliminar Encuestas: Borra registros seleccionados.
Visualización Gráfica: Genera gráficos de barras y circulares.
Exportar Resultados: Guarda datos en formato Excel o PDF.
Librerías Utilizadas
tkinter: Interfaz gráfica.
pandas: Manipulación de datos tabulares.
mysql.connector: Conexión a la base de datos MySQL.
matplotlib: Visualización gráfica.
reportlab: Generación de archivos PDF.

### Notas Adicionales
Asegúrate de que el servidor MySQL esté corriendo antes de iniciar la aplicación.
Los datos exportados se guardan en la misma carpeta del proyecto.
