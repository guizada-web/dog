import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import json

# Endpoint da API
DOG_API_URL = "https://api.thedogapi.com/v1"
HEADERS = {"x-api-key": "DEMO-API-KEY"}  # Substitua por sua chave de API

# Função para carregar os estilos do arquivo JSON
def load_styles():
    try:
        with open("styles.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo de estilos não encontrado!")
        return None

class DogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Navegador de Raças de Cães")
        self.root.geometry("600x600")

        self.breeds = []
        self.selected_breed_id = None
        self.current_theme = "light"

        # Carrega os estilos do arquivo
        self.styles = load_styles()

        self.create_widgets()
        self.load_breeds()
        self.apply_theme()

    def create_widgets(self):
        # Label de título
        self.title_label = tk.Label(self.root, text="Raças de Cães", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Campo de busca
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_breeds)

        # Combobox para raças
        self.breed_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.breed_combo.pack(pady=5)
        self.breed_combo.bind("<<ComboboxSelected>>", self.on_breed_selected)

        # Botão para buscar imagem
        self.fetch_btn = tk.Button(self.root, text="Ver Imagem", command=self.fetch_image)
        self.fetch_btn.pack(pady=10)

        # Botão para alternar tema
        self.toggle_btn = tk.Button(self.root, text="Alternar Tema", command=self.toggle_theme)
        self.toggle_btn.pack(pady=5)

        # Área de imagem
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

    def load_breeds(self):
        try:
            response = requests.get(f"{DOG_API_URL}/breeds", headers=HEADERS)
            response.raise_for_status()
            self.breeds = response.json()
            breed_names = [breed['name'] for breed in self.breeds]
            self.breed_combo['values'] = breed_names
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível carregar as raças:\n{e}")

    def filter_breeds(self, event):
        search_term = self.search_var.get().lower()
        filtered = [breed['name'] for breed in self.breeds if search_term in breed['name'].lower()]
        self.breed_combo['values'] = filtered

    def on_breed_selected(self, event):
        breed_name = self.breed_combo.get()
        for breed in self.breeds:
            if breed['name'] == breed_name:
                self.selected_breed_id = breed['id']
                break

    def fetch_image(self):
        if not self.selected_breed_id:
            messagebox.showwarning("Selecione uma raça", "Por favor, selecione uma raça primeiro.")
            return
        try:
            params = {"breed_id": self.selected_breed_id, "limit": 1}
            response = requests.get(f"{DOG_API_URL}/images/search", params=params, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if data:
                image_url = data[0]['url']
                self.display_image(image_url)
            else:
                messagebox.showinfo("Sem imagem", "Nenhuma imagem encontrada para essa raça.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao buscar imagem:\n{e}")

    def display_image(self, url):
        try:
            image_response = requests.get(url)
            image_response.raise_for_status()
            image_data = image_response.content
            image = Image.open(BytesIO(image_data))
            image = image.resize((400, 400))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Erro na imagem", f"Não foi possível carregar a imagem:\n{e}")

    def apply_theme(self):
        if not self.styles:
            return

        theme = self.styles[self.current_theme]
        self.root.configure(bg=theme["bg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.search_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
        self.breed_combo.configure(background=theme["bg"], foreground=theme["fg"])
        self.toggle_btn.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.fetch_btn.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.image_label.configure(bg=theme["bg"])

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

if __name__ == "__main__":
    root = tk.Tk()
    app = DogApp(root)
    root.mainloop()