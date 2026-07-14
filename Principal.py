import tkinter as tk
from tkinter import messagebox
import json
import os

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Parciales - V3")
        self.root.geometry("750x600")
        
        # 1. Paleta de Estilos (Diseño Limpio y Moderno)
        self.color_fondo = "#F3F4F6"       # Gris claro moderno
        self.color_primario = "#2563EB"    # Azul vibrante para botones
        self.color_secundario = "#ffffff"  # Blanco para las tarjetas
        self.color_texto = "#1F2937"       # Gris oscuro para contraste
        self.fuente_titulo = ("Segoe UI", 18, "bold")
        self.fuente_texto = ("Segoe UI", 12)
        
        self.root.configure(bg=self.color_fondo)
        
        # Obtener el directorio donde está guardado este script de Python
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        if not self.base_dir:
            self.base_dir = os.getcwd()
            
        # Variables de estado del juego
        self.preguntas = []
        self.indice_actual = 0
        self.respuestas_usuario = []  # Lista de listas: guardará los índices seleccionados
        self.materia_actual = ""
        
        # Contenedor principal
        self.main_frame = tk.Frame(self.root, bg=self.color_fondo)
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Generar estructura por defecto si la carpeta está vacía
        self.verificar_estructura_directorios()
        self.mostrar_menu()

    def verificar_estructura_directorios(self):
        """Verifica si existen carpetas de asignaturas. Si no, crea una de ejemplo."""
        items = os.listdir(self.base_dir)
        materias = [d for d in items if os.path.isdir(os.path.join(self.base_dir, d)) 
                    and not d.startswith('.') and d != '__pycache__']
        
        if not materias:
            # Crear una carpeta de ejemplo para que el programa funcione de inmediato
            ejemplo_dir = os.path.join(self.base_dir, "Materia_De_Ejemplo")
            os.makedirs(ejemplo_dir, exist_ok=True)
            
            ejemplo_json = os.path.join(ejemplo_dir, "parcial_modelo_v3.json")
            preguntas_ejemplo = [
                {
                    "pregunta": "¿Qué patrones pertenecen al grupo de diseño Creacionales? (Selección Múltiple)",
                    "opciones": ["Singleton", "Decorator", "Abstract Factory", "Adapter"],
                    "correctas": [0, 2]
                },
                {
                    "pregunta": "En SQL Server, las subconsultas siempre se ejecutan de manera más lenta que los JOIN.",
                    "opciones": ["Verdadero", "Falso"],
                    "correcta_index": 1
                }
            ]
            with open(ejemplo_json, 'w', encoding='utf-8') as f:
                json.dump(preguntas_ejemplo, f, indent=4, ensure_ascii=False)

    def limpiar_pantalla(self):
        """Destruye los widgets actuales para cargar la nueva pantalla."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def crear_boton(self, master, texto, comando, bg_color=None):
        """Generador de botones estilizados."""
        bg = bg_color if bg_color else self.color_primario
        btn = tk.Button(master, text=texto, font=("Segoe UI", 10, "bold"), 
                        bg=bg, fg="white", 
                        activebackground="#1D4ED8", activeforeground="white",
                        relief="flat", cursor="hand2", padx=15, pady=8,
                        command=comando)
        return btn

    def obtener_correctas(self, pregunta):
        """Normaliza los índices correctos del JSON a una lista de enteros."""
        if 'correctas' in pregunta:
            correctas = pregunta['correctas']
            return [int(x) for x in correctas] if isinstance(correctas, list) else [int(correctas)]
        elif 'correcta_index' in pregunta:
            idx = pregunta['correcta_index']
            return [int(x) for x in idx] if isinstance(idx, list) else [int(idx)]
        return []

    # --- PANTALLA 1: MENÚ DE MATERIAS (Carpetas) ---
    def mostrar_menu(self):
        self.limpiar_pantalla()
        
        titulo = tk.Label(self.main_frame, text="📚 Selecciona una Asignatura", 
                          font=self.fuente_titulo, bg=self.color_fondo, fg=self.color_texto)
        titulo.pack(pady=(0, 20))

        # Escanear carpetas (materias)
        items = os.listdir(self.base_dir)
        materias = [d for d in items if os.path.isdir(os.path.join(self.base_dir, d)) 
                    and not d.startswith('.') and d != '__pycache__']

        frame_botones = tk.Frame(self.main_frame, bg=self.color_fondo)
        frame_botones.pack(fill="x")

        for materia in materias:
            nombre_materia = materia.replace("_", " ").title()
            btn = self.crear_boton(frame_botones, f"📁 {nombre_materia}", 
                                   lambda m=materia: self.mostrar_archivos_materia(m))
            btn.pack(pady=6, fill="x")

    # --- PANTALLA 2: SELECCIÓN DE PARCIAL (Archivos JSON de la carpeta) ---
    def mostrar_archivos_materia(self, materia):
        self.materia_actual = materia
        self.limpiar_pantalla()
        
        materia_titulo = materia.replace("_", " ").title()
        titulo = tk.Label(self.main_frame, text=f"📖 Parciales de: {materia_titulo}", 
                          font=self.fuente_titulo, bg=self.color_fondo, fg=self.color_texto)
        titulo.pack(pady=(0, 20))

        ruta_materia = os.path.join(self.base_dir, materia)
        archivos = [f for f in os.listdir(ruta_materia) if f.endswith('.json')]

        frame_botones = tk.Frame(self.main_frame, bg=self.color_fondo)
        frame_botones.pack(fill="x")

        if not archivos:
            tk.Label(frame_botones, text="No se encontraron cuestionarios en esta carpeta.", 
                     bg=self.color_fondo, font=self.fuente_texto).pack(pady=10)
        else:
            for archivo in archivos:
                nombre_parcial = archivo.replace(".json", "").replace("_", " ").title()
                ruta_completa = os.path.join(ruta_materia, archivo)
                btn = self.crear_boton(frame_botones, f"📄 {nombre_parcial}", 
                                       lambda r=ruta_completa: self.iniciar_juego(r))
                btn.pack(pady=6, fill="x")

        # Botón para volver atrás
        btn_volver = self.crear_boton(self.main_frame, "⬅ Volver a Asignaturas", self.mostrar_menu, bg_color="#6B7280")
        btn_volver.pack(pady=(20, 0))

    # --- INICIAR EL JUEGO ---
    def iniciar_juego(self, ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            self.preguntas = json.load(f)
            
        self.indice_actual = 0
        # Inicializamos las respuestas como listas vacías para cada pregunta
        self.respuestas_usuario = [None] * len(self.preguntas)
        self.mostrar_pregunta()

    # --- PANTALLA 3: EL CUESTIONARIO ---
    def mostrar_pregunta(self):
        self.limpiar_pantalla()
        
        pregunta_actual = self.preguntas[self.indice_actual]
        correctas_indices = self.obtener_correctas(pregunta_actual)
        
        # Determinar si la pregunta acepta múltiples respuestas correctas
        self.es_multiple = len(correctas_indices) > 1

        # Barra de progreso y tipo de pregunta
        tipo_texto = "¡Selecciona todas las correctas!" if self.es_multiple else "Selecciona una única opción."
        progreso = tk.Label(self.main_frame, 
                            text=f"Pregunta {self.indice_actual + 1} de {len(self.preguntas)}  |  ({tipo_texto})", 
                            font=("Segoe UI", 10, "bold"), bg=self.color_fondo, fg="#6B7280")
        progreso.pack(anchor="w", pady=(0, 10))

        # Tarjeta blanca para el contenido
        card_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=25, pady=25, relief="flat")
        card_frame.pack(fill="both", expand=True)

        lbl_pregunta = tk.Label(card_frame, text=pregunta_actual['pregunta'], 
                                font=("Segoe UI", 13, "bold"), bg=self.color_secundario, fg=self.color_texto, 
                                wraplength=600, justify="left")
        lbl_pregunta.pack(pady=(0, 20), anchor="w")

        # Recuperar respuesta guardada (si existe)
        saved_respuestas = self.respuestas_usuario[self.indice_actual]

        # Generar las opciones dinámicamente según el tipo de pregunta
        if self.es_multiple:
            self.variables_opciones = []
            for i, opcion in enumerate(pregunta_actual['opciones']):
                # Si ya existía una selección previa, la recuperamos
                is_selected = False
                if saved_respuestas is not None and i in saved_respuestas:
                    is_selected = True
                
                var = tk.BooleanVar(value=is_selected)
                self.variables_opciones.append(var)
                
                cb = tk.Checkbutton(card_frame, text=opcion, variable=var, 
                                    font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto,
                                    activebackground=self.color_secundario, selectcolor="#E5E7EB", cursor="hand2")
                cb.pack(anchor="w", pady=5)
        else:
            initial_val = -1
            if saved_respuestas is not None and len(saved_respuestas) > 0:
                initial_val = saved_respuestas[0]
                
            self.opcion_seleccionada = tk.IntVar(value=initial_val)
            for i, opcion in enumerate(pregunta_actual['opciones']):
                rb = tk.Radiobutton(card_frame, text=opcion, variable=self.opcion_seleccionada, value=i, 
                                    font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto,
                                    activebackground=self.color_secundario, selectcolor="#E5E7EB", cursor="hand2")
                rb.pack(anchor="w", pady=5)

        # Contenedor inferior de control de flujo
        navigation_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        navigation_frame.pack(fill="x", pady=(20, 0))

        # Botón Anterior (solo si no es la primera)
        if self.indice_actual > 0:
            btn_anterior = self.crear_boton(navigation_frame, "⬅ Anterior", self.anterior_pregunta, bg_color="#4B5563")
            btn_anterior.pack(side="left")

        # Botón Siguiente / Finalizar
        texto_sig = "Finalizar 🏁" if self.indice_actual == len(self.preguntas) - 1 else "Siguiente ➔"
        btn_siguiente = self.crear_boton(navigation_frame, texto_sig, self.siguiente_pregunta)
        btn_siguiente.pack(side="right")
        
        # Botón para abandonar el juego actual
        btn_abandonar = tk.Button(navigation_frame, text="Abandonar", font=("Segoe UI", 9, "bold"),
                                  bg="#EF4444", fg="white", activebackground="#DC2626", activeforeground="white",
                                  relief="flat", cursor="hand2", padx=10, pady=5,
                                  command=lambda: self.mostrar_archivos_materia(self.materia_actual))
        btn_abandonar.pack(side="left", padx=15)

    def guardar_respuesta_actual(self):
        """Lee el estado actual de los controles visuales y lo guarda en memoria."""
        if self.es_multiple:
            # Guarda los índices de todas las casillas marcadas
            seleccionados = [i for i, var in enumerate(self.variables_opciones) if var.get()]
            self.respuestas_usuario[self.indice_actual] = seleccionados
        else:
            val = self.opcion_seleccionada.get()
            if val != -1:
                self.respuestas_usuario[self.indice_actual] = [val]
            else:
                self.respuestas_usuario[self.indice_actual] = [] # Lista vacía significa omitida/sin responder

    def anterior_pregunta(self):
        self.guardar_respuesta_actual()
        self.indice_actual -= 1
        self.mostrar_pregunta()

    def siguiente_pregunta(self):
        self.guardar_respuesta_actual()
        self.indice_actual += 1
        
        if self.indice_actual < len(self.preguntas):
            self.mostrar_pregunta()
        else:
            self.mostrar_resultados()

    # --- PANTALLA 4: RESULTADOS DETALLADOS ---
    def mostrar_resultados(self):
        self.limpiar_pantalla()
        
        correctas_cnt = 0
        sin_responder_cnt = 0
        detalles_errores = []
        detalles_sin_responder = []

        # Evaluar detalladamente las respuestas
        for i, p in enumerate(self.preguntas):
            user_ans = self.respuestas_usuario[i]
            correctas_indices = self.obtener_correctas(p)

            # Si la lista de respuestas está vacía o es None, la contamos como omitida
            if user_ans is None or len(user_ans) == 0:
                sin_responder_cnt += 1
                correctas_str = ", ".join([p['opciones'][idx] for idx in correctas_indices])
                detalles_sin_responder.append(f"⚪ Pregunta {i+1}: No la contestaste. ➔ Correcta(s): '{correctas_str}'")
            elif set(user_ans) == set(correctas_indices):
                correctas_cnt += 1
            else:
                user_str = ", ".join([p['opciones'][idx] for idx in user_ans])
                correctas_str = ", ".join([p['opciones'][idx] for idx in correctas_indices])
                detalles_errores.append(f"❌ Pregunta {i+1}: Contestaste '{user_str}' ➔ Era '{correctas_str}'")

        total = len(self.preguntas)
        incorrectas_cnt = total - correctas_cnt - sin_responder_cnt

        pct_correctas = (correctas_cnt / total) * 100
        pct_incorrectas = (incorrectas_cnt / total) * 100
        pct_sin_responder = (sin_responder_cnt / total) * 100

        # Bloque de estadísticas de Rendimiento
        stats_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        stats_frame.pack(fill="x", pady=(0, 15))

        # Configuramos una cuadrícula de 3 columnas para mostrar cada porcentaje
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        # Tarjetas de datos
        def crear_tarjeta_stat(col, titulo, valor, cantidad, color):
            frame = tk.Frame(stats_frame, bg=self.color_secundario, padx=10, pady=10)
            frame.grid(row=0, column=col, padx=5, sticky="nsew")
            tk.Label(frame, text=titulo, font=("Segoe UI", 9, "bold"), bg=self.color_secundario, fg="#6B7280").pack()
            tk.Label(frame, text=f"{valor:.1f}%", font=("Segoe UI", 18, "bold"), bg=self.color_secundario, fg=color).pack()
            tk.Label(frame, text=f"({cantidad} de {total})", font=("Segoe UI", 9), bg=self.color_secundario, fg=self.color_texto).pack()

        crear_tarjeta_stat(0, "CORRECTAS", pct_correctas, correctas_cnt, "#10B981")
        crear_tarjeta_stat(1, "INCORRECTAS", pct_incorrectas, incorrectas_cnt, "#EF4444")
        crear_tarjeta_stat(2, "SIN RESPONDER", pct_sin_responder, sin_responder_cnt, "#6B7280")

        # Caja de Texto Desplazable (Scrollable) para el feedback de errores
        review_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=10, pady=10)
        review_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(review_frame)
        scrollbar.pack(side="right", fill="y")
        
        # El widget Text nos asegura que el programa no se rompa si hay decenas de preguntas erróneas
        text_widget = tk.Text(review_frame, wrap="word", yscrollcommand=scrollbar.set,
                              font=("Segoe UI", 10), bg=self.color_secundario, fg=self.color_texto,
                              relief="flat", height=8)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Estilos aplicados al texto
        text_widget.tag_config("rojo", foreground="#EF4444")
        text_widget.tag_config("gris", foreground="#4B5563")
        text_widget.tag_config("negro_bold", foreground=self.color_texto, font=("Segoe UI", 11, "bold"))
        
        text_widget.insert("end", "📋 REPASO DE TU EVALUACIÓN\n\n", "negro_bold")
        
        if detalles_errores:
            text_widget.insert("end", "Preguntas Incorrectas:\n", "negro_bold")
            for err in detalles_errores:
                text_widget.insert("end", err + "\n", "rojo")
            text_widget.insert("end", "\n")
            
        if detalles_sin_responder:
            text_widget.insert("end", "Preguntas Omitidas:\n", "negro_bold")
            for sr in detalles_sin_responder:
                text_widget.insert("end", sr + "\n", "gris")
                
        if not detalles_errores and not detalles_sin_responder:
            text_widget.insert("end", "🎉 ¡Excelente trabajo! Respondiste todo de forma perfecta.", "negro_bold")

        text_widget.config(state="disabled") # Hacer el control de solo lectura

        btn_volver = self.crear_boton(self.main_frame, "Volver al Menú de Materias", self.mostrar_menu)
        btn_volver.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()