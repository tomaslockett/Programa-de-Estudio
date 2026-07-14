import tkinter as tk
from tkinter import messagebox
import json
import os

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Parciales - V2")
        self.root.geometry("700x550")
        
        # 1. Definición de Estilos (Tu paleta de diseño)
        self.color_fondo = "#F3F4F6"      # Gris claro moderno
        self.color_primario = "#2563EB"   # Azul vibrante para botones
        self.color_secundario = "#ffffff" # Blanco para las tarjetas
        self.color_texto = "#1F2937"      # Gris oscuro (mejor contraste que el negro puro)
        self.fuente_titulo = ("Segoe UI", 18, "bold")
        self.fuente_texto = ("Segoe UI", 12)
        
        self.root.configure(bg=self.color_fondo)
        
        # Variables de estado del juego
        self.preguntas = []
        self.indice_actual = 0
        self.respuestas_usuario = []
        
        # Contenedor principal
        self.main_frame = tk.Frame(self.root, bg=self.color_fondo)
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        self.mostrar_menu()

    def limpiar_pantalla(self):
        """Destruye los widgets actuales para cargar la nueva pantalla."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def crear_boton(self, master, texto, comando):
        """Generador de botones estilizados para no repetir código."""
        btn = tk.Button(master, text=texto, font=("Segoe UI", 11, "bold"), 
                        bg=self.color_primario, fg="white", 
                        activebackground="#1D4ED8", activeforeground="white",
                        relief="flat", cursor="hand2", padx=20, pady=10,
                        command=comando)
        return btn

    # --- PANTALLA 1: MENÚ PRINCIPAL ---
    def mostrar_menu(self):
        self.limpiar_pantalla()
        
        titulo = tk.Label(self.main_frame, text="📚 Selecciona un Parcial", 
                          font=self.fuente_titulo, bg=self.color_fondo, fg=self.color_texto)
        titulo.pack(pady=(0, 30))

        archivos = [f for f in os.listdir() if f.endswith('.json')]
        
        if not archivos:
            tk.Label(self.main_frame, text="No se encontraron archivos JSON.", 
                     bg=self.color_fondo, font=self.fuente_texto).pack()
            return

        # Contenedor para alinear los botones
        frame_botones = tk.Frame(self.main_frame, bg=self.color_fondo)
        frame_botones.pack(fill="x")

        for archivo in archivos:
            # Formatear el nombre del archivo para que se vea mejor (ej: "parcial_sistemas.json" -> "Parcial Sistemas")
            nombre_limpio = archivo.replace(".json", "").replace("_", " ").title()
            btn = self.crear_boton(frame_botones, nombre_limpio, lambda a=archivo: self.iniciar_juego(a))
            btn.pack(pady=8, fill="x") # fill="x" hace que el botón ocupe todo el ancho disponible

    # --- PANTALLA 2: EL JUEGO ---
    def iniciar_juego(self, archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            self.preguntas = json.load(f)
            
        self.indice_actual = 0
        self.respuestas_usuario = []
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        self.limpiar_pantalla()
        
        pregunta_actual = self.preguntas[self.indice_actual]
        
        # Indicador de progreso (Ej: Pregunta 1 de 10)
        progreso = tk.Label(self.main_frame, text=f"Pregunta {self.indice_actual + 1} de {len(self.preguntas)}", 
                            font=("Segoe UI", 10, "bold"), bg=self.color_fondo, fg="#6B7280")
        progreso.pack(anchor="w", pady=(0, 10))

        # Tarjeta blanca para la pregunta (Simulando un contenedor flotante)
        card_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=25, pady=25, relief="flat")
        card_frame.pack(fill="both", expand=True)

        lbl_pregunta = tk.Label(card_frame, text=pregunta_actual['pregunta'], 
                                font=("Segoe UI", 14, "bold"), bg=self.color_secundario, fg=self.color_texto, 
                                wraplength=550, justify="left")
        lbl_pregunta.pack(pady=(0, 20), anchor="w")

        self.opcion_seleccionada = tk.IntVar(value=-1)

        # Opciones estilizadas
        for i, opcion in enumerate(pregunta_actual['opciones']):
            rb = tk.Radiobutton(card_frame, text=opcion, variable=self.opcion_seleccionada, value=i, 
                                font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto,
                                activebackground=self.color_secundario, selectcolor="#E5E7EB", cursor="hand2")
            rb.pack(anchor="w", pady=5)

        # Botón Siguiente alineado a la derecha
        btn_siguiente = self.crear_boton(self.main_frame, "Siguiente ➔", self.siguiente_pregunta)
        btn_siguiente.pack(pady=(20, 0), side="right")

    def siguiente_pregunta(self):
        if self.opcion_seleccionada.get() == -1:
            messagebox.showwarning("Atención", "Por favor, selecciona una opción.")
            return
            
        self.respuestas_usuario.append(self.opcion_seleccionada.get())
        self.indice_actual += 1
        
        if self.indice_actual < len(self.preguntas):
            self.mostrar_pregunta()
        else:
            self.mostrar_resultados()

    # --- PANTALLA 3: RESULTADOS ---
    def mostrar_resultados(self):
        self.limpiar_pantalla()
        
        correctas = 0
        detalles = []

        for i, p in enumerate(self.preguntas):
            respuesta_user = self.respuestas_usuario[i]
            respuesta_ok = p['correcta_index']
            
            if respuesta_user == respuesta_ok:
                correctas += 1
            else:
                texto_error = f"❌ Pregunta {i+1}: Contestaste '{p['opciones'][respuesta_user]}' ➔ Era '{p['opciones'][respuesta_ok]}'."
                detalles.append(texto_error)

        total = len(self.preguntas)
        porcentaje = (correctas / total) * 100

        # Tarjeta de resumen de nota
        resumen_frame = tk.Frame(self.main_frame, bg=self.color_secundario, padx=20, pady=20, relief="flat")
        resumen_frame.pack(fill="x")

        # Color dinámico: Verde si es >= 60%, Rojo si no
        color_resultado = "#10B981" if porcentaje >= 60 else "#EF4444"
        
        tk.Label(resumen_frame, text="Tu Calificación", font=self.fuente_texto, bg=self.color_secundario, fg="#6B7280").pack()
        tk.Label(resumen_frame, text=f"{porcentaje:.0f}%", font=("Segoe UI", 32, "bold"), bg=self.color_secundario, fg=color_resultado).pack()
        tk.Label(resumen_frame, text=f"Acertaste {correctas} de {total} preguntas", font=self.fuente_texto, bg=self.color_secundario, fg=self.color_texto).pack(pady=(5,0))

        # Lista de errores
        if detalles:
            errores_frame = tk.Frame(self.main_frame, bg=self.color_fondo)
            errores_frame.pack(fill="both", expand=True, pady=20)
            
            tk.Label(errores_frame, text="Revisión de errores:", font=("Segoe UI", 12, "bold"), 
                     bg=self.color_fondo, fg=self.color_texto).pack(anchor="w", pady=(0, 10))
            
            for error in detalles:
                tk.Label(errores_frame, text=error, fg="#991B1B", bg=self.color_fondo, font=("Segoe UI", 10), 
                         wraplength=600, justify="left").pack(anchor="w", pady=2)

        btn_volver = self.crear_boton(self.main_frame, "Volver al Menú", self.mostrar_menu)
        btn_volver.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()