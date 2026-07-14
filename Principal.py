import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import random

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Parciales - V4 (Corregido)")
        self.root.geometry("850x750")
        self.root.minsize(800, 700)
        
        # --- MEJORA: Sistema de Temas (Dark/Light Mode) ---
        self.is_dark_mode = False
        self.temas = {
            "claro": {"fondo": "#F3F4F6", "primario": "#2563EB", "secundario": "#ffffff", "texto": "#1F2937"},
            "oscuro": {"fondo": "#111827", "primario": "#3B82F6", "secundario": "#1F2937", "texto": "#F9FAFB"}
        }
        
        # Contenedores principales declarados antes de aplicar_colores
        self.top_bar = tk.Frame(self.root)
        self.main_frame = tk.Frame(self.root)
        
        self.aplicar_colores()
        
        # Variables de estado del juego
        self.preguntas = []
        self.indice_actual = 0
        self.respuestas_usuario = []
        self.materia_actual = ""
        self.estado_app = {"pantalla": "menu", "arg": None}
        
        # Obtener el directorio base
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        if not self.base_dir:
            self.base_dir = os.getcwd()
            
        # Barra superior permanente (para el botón de tema)
        self.top_bar.pack(fill="x", padx=20, pady=(10, 0))
        
        self.btn_theme = tk.Button(self.top_bar, text="🌙 Modo Oscuro", font=("Segoe UI", 9, "bold"),
                                   bg=self.color_secundario, fg=self.color_texto, relief="flat", cursor="hand2",
                                   command=self.toggle_theme, padx=10, pady=5)
        self.btn_theme.pack(side="right")
        
        # Contenedor principal
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=(10, 40))
        
        self.verificar_estructura_directorios()
        self.mostrar_menu()

    # --- LÓGICA DE TEMAS Y COMPONENTES NUEVOS ---
    def aplicar_colores(self):
        tema = self.temas["oscuro"] if self.is_dark_mode else self.temas["claro"]
        self.color_fondo = tema["fondo"]
        self.color_primario = tema["primario"]
        self.color_secundario = tema["secundario"]
        self.color_texto = tema["texto"]
        self.fuente_titulo = ("Segoe UI", 18, "bold")
        self.fuente_texto = ("Segoe UI", 12)
        
        # ➔ FIX MODO OSCURO: Se actualizan TODOS los contenedores en cascada
        self.root.configure(bg=self.color_fondo)
        self.main_frame.configure(bg=self.color_fondo)
        self.top_bar.configure(bg=self.color_fondo)
        
        # Configurar el estilo de la barra de progreso
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=8, background=self.color_primario, 
                        troughcolor=self.color_secundario, borderwidth=0)

    def crear_lista_scrollable(self, parent):
        """➔ FIX OVERFLOW: Crea un contenedor con scrollbar para listas largas de botones."""
        contenedor_exterior = tk.Frame(parent, bg=self.color_fondo)

        canvas = tk.Canvas(contenedor_exterior, bg=self.color_fondo, highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor_exterior, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.color_fondo)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def configure_canvas_width(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)

        canvas.bind("<Configure>", configure_canvas_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Habilitar scroll con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        return contenedor_exterior, scrollable_frame

    def toggle_theme(self):
        """Alterna el modo oscuro/claro de forma dinámica sin perder el progreso."""
        if self.estado_app["pantalla"] == "pregunta":
            self.guardar_respuesta_actual()
            
        self.is_dark_mode = not self.is_dark_mode
        self.aplicar_colores()
        
        texto_btn = "☀️ Modo Claro" if self.is_dark_mode else "🌙 Modo Oscuro"
        self.btn_theme.configure(text=texto_btn, bg=self.color_secundario, fg=self.color_texto)
        
        # Recargar la pantalla exacta donde estaba el usuario
        pantalla = self.estado_app["pantalla"]
        if pantalla == "menu": self.mostrar_menu()
        elif pantalla == "archivos": self.mostrar_archivos_materia(self.estado_app["arg"])
        elif pantalla == "pregunta": self.mostrar_pregunta()
        elif pantalla == "resultados": self.mostrar_resultados()
        elif pantalla == "repaso": self.mostrar_repaso(self.estado_app["arg"])

    def verificar_estructura_directorios(self):
        items = os.listdir(self.base_dir)
        materias = [d for d in items if os.path.isdir(os.path.join(self.base_dir, d)) 
                    and not d.startswith('.') and d != '__pycache__']
        
        if not materias:
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
                    "correctas": [1]
                }
            ]
            with open(ejemplo_json, 'w', encoding='utf-8') as f:
                json.dump(preguntas_ejemplo, f, indent=4, ensure_ascii=False)

    def limpiar_pantalla(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def crear_boton(self, master, texto, comando, bg_color=None):
        bg = bg_color if bg_color else self.color_primario
        btn = tk.Button(master, text=texto, font=("Segoe UI", 10, "bold"), 
                        bg=bg, fg="white", activebackground="#1D4ED8", activeforeground="white",
                        relief="flat", cursor="hand2", padx=15, pady=8, command=comando)
        return btn

    def obtener_correctas(self, pregunta):
        if 'correctas' in pregunta:
            correctas = pregunta['correctas']
            return [int(x) for x in correctas] if isinstance(correctas, list) else [int(correctas)]
        elif 'correcta_index' in pregunta:
            idx = pregunta['correcta_index']
            return [int(x) for x in idx] if isinstance(idx, list) else [int(idx)]
        return []

    # --- PANTALLA 1: MENÚ ---
    def mostrar_menu(self):
        self.estado_app = {"pantalla": "menu", "arg": None}
        self.limpiar_pantalla()
        
        titulo = tk.Label(self.main_frame, text="📚 Selecciona una Asignatura", 
                          font=self.fuente_titulo, bg=self.color_fondo, fg=self.color_texto)
        titulo.pack(pady=(0, 20))

        items = os.listdir(self.base_dir)
        materias = [d for d in items if os.path.isdir(os.path.join(self.base_dir, d)) 
                    and not d.startswith('.') and d != '__pycache__']

        # ➔ FIX OVERFLOW: Reemplazamos el Frame normal por el Scrollable
        frame_exterior, frame_botones = self.crear_lista_scrollable(self.main_frame)
        frame_exterior.pack(fill="both", expand=True)

        for materia in materias:
            nombre_materia = materia.replace("_", " ").title()
            btn = self.crear_boton(frame_botones, f"📁 {nombre_materia}", 
                                   lambda m=materia: self.mostrar_archivos_materia(m))
            btn.pack(pady=6, fill="x")

    # --- PANTALLA 2: ARCHIVOS ---
    def mostrar_archivos_materia(self, materia):
        self.estado_app = {"pantalla": "archivos", "arg": materia}
        self.materia_actual = materia
        self.limpiar_pantalla()
        
        materia_titulo = materia.replace("_", " ").title()
        titulo = tk.Label(self.main_frame, text=f"📖 Parciales de: {materia_titulo}", 
                          font=self.fuente_titulo, bg=self.color_fondo, fg=self.color_texto)
        titulo.pack(pady=(0, 20))

        ruta_materia = os.path.join(self.base_dir, materia)
        archivos = [f for f in os.listdir(ruta_materia) if f.endswith('.json')]

        # ➔ FIX OVERFLOW: Reemplazamos el Frame normal por el Scrollable
        frame_exterior, frame_botones = self.crear_lista_scrollable(self.main_frame)
        frame_exterior.pack(fill="both", expand=True, pady=(0, 20))

        if not archivos:
            tk.Label(frame_botones, text="No se encontraron cuestionarios en esta carpeta.", 
                     bg=self.color_fondo, fg=self.color_texto, font=self.fuente_texto).pack(pady=10)
        else:
            for archivo in archivos:
                nombre_parcial = archivo.replace(".json", "").replace("_", " ").title()
                ruta_completa = os.path.join(ruta_materia, archivo)
                btn = self.crear_boton(frame_botones, f"📄 {nombre_parcial}", 
                                       lambda r=ruta_completa: self.iniciar_juego(r))
                btn.pack(pady=6, fill="x")

        btn_volver = self.crear_boton(self.main_frame, "⬅ Volver a Asignaturas", self.mostrar_menu, bg_color="#6B7280")
        btn_volver.pack()

    # --- LÓGICA DE INICIO Y RANDOMIZER ---
    def iniciar_juego(self, ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)
            
        self.preguntas = []
        for p in datos_json:
            correctas_orig = self.obtener_correctas(p)
            opciones_enumeradas = list(enumerate(p['opciones']))
            
            if len(opciones_enumeradas) > 2:
                random.shuffle(opciones_enumeradas)
            
            nuevas_opciones = []
            nuevas_correctas = []
            
            for nuevo_idx, (viejo_idx, texto) in enumerate(opciones_enumeradas):
                nuevas_opciones.append(texto)
                if viejo_idx in correctas_orig:
                    nuevas_correctas.append(nuevo_idx)
            
            self.preguntas.append({
                "pregunta": p['pregunta'],
                "opciones": nuevas_opciones,
                "correctas": nuevas_correctas
            })
            
        random.shuffle(self.preguntas)

        self.indice_actual = 0
        self.respuestas_usuario = [None] * len(self.preguntas)
        self.mostrar_pregunta()

    # --- PANTALLA 3: CUESTIONARIO ---
    def mostrar_pregunta(self):
        self.estado_app = {"pantalla": "pregunta", "arg": None}
        self.limpiar_pantalla()
        
        pregunta_actual = self.preguntas[self.indice_actual]
        correctas_indices = self.obtener_correctas(pregunta_actual)
        self.es_multiple = len(correctas_indices) > 1

        porcentaje_progreso = ((self.indice_actual) / len(self.preguntas)) * 100
        progreso_bar = ttk.Progressbar(self.main_frame, style="TProgressbar", orient="horizontal", mode="determinate")
        progreso_bar.pack(fill="x", pady=(0, 5))
        progreso_bar["value"] = porcentaje_progreso

        tipo_texto = "¡Selecciona todas las correctas!" if self.es_multiple else "Selecciona una única opción."
        progreso = tk.Label(self.main_frame, text=f"Pregunta {self.indice_actual + 1} de {len(self.preguntas)}  |  ({tipo_texto})", 
                            font=("Segoe UI", 10, "bold"), bg=self.color_fondo, fg="#6B7280")
        progreso.pack(anchor="w", pady=(0, 10))

        card_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=25, pady=25, relief="flat")
        card_frame.pack(fill="both", expand=True)

        lbl_pregunta = tk.Label(card_frame, text=pregunta_actual['pregunta'], 
                                font=("Segoe UI", 13, "bold"), bg=self.color_secundario, fg=self.color_texto, 
                                wraplength=700, justify="left")
        lbl_pregunta.pack(pady=(0, 20), anchor="w")

        saved_respuestas = self.respuestas_usuario[self.indice_actual]

        if self.es_multiple:
            self.variables_opciones = []
            for i, opcion in enumerate(pregunta_actual['opciones']):
                is_selected = False
                if saved_respuestas is not None and i in saved_respuestas:
                    is_selected = True
                
                var = tk.BooleanVar(value=is_selected)
                self.variables_opciones.append(var)
                
                cb = tk.Checkbutton(card_frame, text=opcion, variable=var, 
                                    font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto,
                                    activebackground=self.color_secundario, selectcolor=self.color_fondo, cursor="hand2",
                                    wraplength=700, justify="left")
                cb.pack(anchor="w", pady=5)
        else:
            initial_val = -1
            if saved_respuestas is not None and len(saved_respuestas) > 0:
                initial_val = saved_respuestas[0]
                
            self.opcion_seleccionada = tk.IntVar(value=initial_val)
            for i, opcion in enumerate(pregunta_actual['opciones']):
                rb = tk.Radiobutton(card_frame, text=opcion, variable=self.opcion_seleccionada, value=i, 
                                    font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto,
                                    activebackground=self.color_secundario, selectcolor=self.color_fondo, cursor="hand2",
                                    wraplength=700, justify="left")
                rb.pack(anchor="w", pady=5)

        navigation_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        navigation_frame.pack(fill="x", pady=(20, 0))

        if self.indice_actual > 0:
            btn_anterior = self.crear_boton(navigation_frame, "⬅ Anterior", self.anterior_pregunta, bg_color="#4B5563")
            btn_anterior.pack(side="left")

        texto_sig = "Finalizar 🏁" if self.indice_actual == len(self.preguntas) - 1 else "Siguiente ➔"
        btn_siguiente = self.crear_boton(navigation_frame, texto_sig, self.siguiente_pregunta)
        btn_siguiente.pack(side="right")
        
        btn_abandonar = tk.Button(navigation_frame, text="Abandonar", font=("Segoe UI", 9, "bold"),
                                  bg="#EF4444", fg="white", activebackground="#DC2626", activeforeground="white",
                                  relief="flat", cursor="hand2", padx=10, pady=5,
                                  command=lambda: self.mostrar_archivos_materia(self.materia_actual))
        btn_abandonar.pack(side="left", padx=15)

    def guardar_respuesta_actual(self):
        if self.es_multiple:
            seleccionados = [i for i, var in enumerate(self.variables_opciones) if var.get()]
            self.respuestas_usuario[self.indice_actual] = seleccionados
        else:
            val = self.opcion_seleccionada.get()
            if val != -1:
                self.respuestas_usuario[self.indice_actual] = [val]
            else:
                self.respuestas_usuario[self.indice_actual] = [] 

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

    # --- PANTALLA 4: RESULTADOS ---
    def mostrar_resultados(self):
        self.estado_app = {"pantalla": "resultados", "arg": None}
        self.limpiar_pantalla()
        
        correctas_cnt = 0
        sin_responder_cnt = 0
        detalles_errores = []
        detalles_sin_responder = []

        for i, p in enumerate(self.preguntas):
            user_ans = self.respuestas_usuario[i]
            correctas_indices = self.obtener_correctas(p)

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

        stats_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        stats_frame.pack(fill="x", pady=(0, 15))

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        def crear_tarjeta_stat(col, titulo, valor, cantidad, color):
            frame = tk.Frame(stats_frame, bg=self.color_secundario, padx=10, pady=10)
            frame.grid(row=0, column=col, padx=5, sticky="nsew")
            tk.Label(frame, text=titulo, font=("Segoe UI", 9, "bold"), bg=self.color_secundario, fg="#6B7280").pack()
            tk.Label(frame, text=f"{valor:.1f}%", font=("Segoe UI", 18, "bold"), bg=self.color_secundario, fg=color).pack()
            tk.Label(frame, text=f"({cantidad} de {total})", font=("Segoe UI", 9), bg=self.color_secundario, fg=self.color_texto).pack()

        crear_tarjeta_stat(0, "CORRECTAS", pct_correctas, correctas_cnt, "#10B981")
        crear_tarjeta_stat(1, "INCORRECTAS", pct_incorrectas, incorrectas_cnt, "#EF4444")
        crear_tarjeta_stat(2, "SIN RESPONDER", pct_sin_responder, sin_responder_cnt, "#6B7280")

        review_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=10, pady=10)
        review_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(review_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(review_frame, wrap="word", yscrollcommand=scrollbar.set,
                              font=("Segoe UI", 10), bg=self.color_secundario, fg=self.color_texto,
                              relief="flat", height=8)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
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

        text_widget.config(state="disabled")

        botones_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        botones_frame.pack(pady=10)

        btn_repaso = self.crear_boton(botones_frame, "🔍 Ver Solucionario", lambda: self.mostrar_repaso(0), bg_color="#10B981")
        btn_repaso.pack(side="left", padx=10)

        btn_volver = self.crear_boton(botones_frame, "Volver al Menú", self.mostrar_menu, bg_color="#4B5563")
        btn_volver.pack(side="left", padx=10)
        
    # --- PANTALLA 5: SOLUCIONARIO ---
    def mostrar_repaso(self, index):
        self.estado_app = {"pantalla": "repaso", "arg": index}
        self.limpiar_pantalla()
        
        pregunta_actual = self.preguntas[index]
        correctas_indices = self.obtener_correctas(pregunta_actual)
        user_ans = self.respuestas_usuario[index] or []

        porcentaje_progreso = ((index + 1) / len(self.preguntas)) * 100
        progreso_bar = ttk.Progressbar(self.main_frame, style="TProgressbar", orient="horizontal", mode="determinate")
        progreso_bar.pack(fill="x", pady=(0, 5))
        progreso_bar["value"] = porcentaje_progreso

        progreso = tk.Label(self.main_frame, text=f"Solucionario - Pregunta {index + 1} de {len(self.preguntas)}", 
                            font=("Segoe UI", 10, "bold"), bg=self.color_fondo, fg="#6B7280")
        progreso.pack(anchor="w", pady=(0, 10))

        card_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=25, pady=25, relief="flat")
        card_frame.pack(fill="both", expand=True)

        lbl_pregunta = tk.Label(card_frame, text=pregunta_actual['pregunta'], 
                                font=("Segoe UI", 13, "bold"), bg=self.color_secundario, fg=self.color_texto, 
                                wraplength=700, justify="left")
        lbl_pregunta.pack(pady=(0, 20), anchor="w")

        for i, opcion in enumerate(pregunta_actual['opciones']):
            color_texto = self.color_texto
            fuente = self.fuente_texto
            
            if i in correctas_indices:
                color_texto = "#10B981" 
                opcion_texto = f"✅ {opcion}"
                fuente = ("Segoe UI", 12, "bold")
            elif i in user_ans and i not in correctas_indices:
                color_texto = "#EF4444"
                opcion_texto = f"❌ {opcion} (Tu respuesta)"
            else:
                opcion_texto = f"⚪ {opcion}"

            tk.Label(card_frame, text=opcion_texto, font=fuente, bg=self.color_secundario, fg=color_texto, 
                     wraplength=700, justify="left").pack(anchor="w", pady=6)

        nav_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
        nav_frame.pack(fill="x", pady=(20, 0))

        if index > 0:
            btn_anterior = self.crear_boton(nav_frame, "⬅ Anterior", lambda: self.mostrar_repaso(index - 1), bg_color="#4B5563")
            btn_anterior.pack(side="left")

        if index < len(self.preguntas) - 1:
            btn_siguiente = self.crear_boton(nav_frame, "Siguiente ➔", lambda: self.mostrar_repaso(index + 1))
            btn_siguiente.pack(side="right")
        else:
            btn_fin = self.crear_boton(nav_frame, "Volver a Resultados", self.mostrar_resultados, bg_color="#2563EB")
            btn_fin.pack(side="right")    

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()