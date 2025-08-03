import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import os
import json
import datetime
import psutil
import platform
import shutil
import time
import webbrowser
# import webview # Removed webview for better executable compatibility
from random import randint  # Added missing import


def mail():
    messagebox.showinfo("Information", "Voici une fenêtre d'information.")


# ==== CONFIGURATION ==== #
CONFIG_FILE = "config.json"
DATA_DIR = "data/notes"
AVAILABLE_APPS = ["Notes", "Fichiers", "Navigateur", "Analyse du PC", "Snake"]

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ==== CHARGER CONFIG ==== #
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted config file
                messagebox.showerror("Erreur", "Fichier de configuration corrompu. Réinitialisation...")
                os.remove(CONFIG_FILE)  # Delete corrupted file
    # Default configuration
    return {"password": "", "bg_color": "#ffffff", "installed_apps": []}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)  # Use indent for readability in config.json


# Initialize config immediately after load_config and save_config are defined
config = load_config()


def reset_system():
    global config  # Declare global to modify the variable

    # Demande mot de passe
    pwd = simpledialog.askstring("Mot de passe", "Entrez votre mot de passe pour réinitialiser:", show='*')
    if pwd != config.get("password"):
        messagebox.showerror("Erreur", "Mot de passe incorrect")
        return

    # Confirmation
    if not messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir tout réinitialiser ?\n"
                                            "Cela supprimera toutes vos données. Le nouveau mot de passe sera vide."):
        return

    # Attente 10 secondes (Consider making this non-blocking with root.after or a separate thread)
    # For a simple OS, a blocking messagebox might be acceptable for a short duration
    for i in range(5, 0, -1):  # Reduced to 5 seconds for quicker testing
        temp_win = tk.Toplevel(root)
        temp_win.title("Attention")
        tk.Label(temp_win, text=f"Réinitialisation dans {i} secondes...", font=("Arial", 12)).pack(padx=20, pady=20)
        temp_win.update_idletasks()  # Update the window to show the text
        time.sleep(1)
        temp_win.destroy()

    # Suppression des données
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR)

    # Supprime config (réinitialise config)
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    config = {"password": "", "bg_color": "#ffffff", "installed_apps": []}  # Reinitialize config
    save_config(config)

    messagebox.showinfo("Réinitialisé",
                        "Le système a été réinitialisé.\nVous allez être déconnecté. Le nouveau mot de passe est vide.")

    # Retour à l'écran login
    login_screen()


# ==== ANALYSE RÉELLE ==== #
def analyze_system():
    memory = psutil.virtual_memory()
    cpu_cores = psutil.cpu_count(logical=True)
    disk = shutil.disk_usage("/")
    system = platform.system()
    release = platform.release()
    temp = "Non disponible"  # Default to "Non disponible"

    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current is not None:  # Check if temperature is available
                        temp = f"{entry.current:.1f}°C"
                        break
                if temp != "Non disponible":
                    break

    return {
        "Système": f"{system} {release}",
        "Mémoire RAM": f"{memory.total // (1024 ** 3)} GB",
        "CPU": f"{cpu_cores} cœurs",
        "Stockage libre": f"{disk.free // (1024 ** 3)} GB",
        "Température": temp
    }


# ==== ÉCRAN DE DÉMARRAGE ==== #
def login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#ffffff")  # Set default background for login screen

    tk.Label(root, text="Bienvenue dans Nexa OS", font=("Arial", 20)).pack(pady=20)
    now = datetime.datetime.now()
    tk.Label(root, text=now.strftime("%Y-%m-%d %H:%M:%S"), font=("Arial", 14)).pack(pady=5)

    tk.Label(root, text="Mot de passe:").pack(pady=5)
    pwd_entry = tk.Entry(root, show="*")
    pwd_entry.pack(pady=5)

    def check_password():
        # If no password is set, any input is considered correct or proceed if empty
        if not config.get("password"):
            main_os()
        elif pwd_entry.get() == config.get("password"):
            main_os()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")

    button_text = "Définir et se connecter" if not config.get("password") else "Se connecter"
    login_button = tk.Button(root, text=button_text, command=check_password)
    login_button.pack(pady=10)

    # Allow pressing Enter to log in
    root.bind('<Return>', lambda event=None: check_password())
    pwd_entry.focus_set()  # Focus the password entry for immediate typing


# ==== APPLICATIONS ==== #
def open_mp3_playeur():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import pygame
    import os
    import threading
    import time

    FICHIER_MUSIQUES = "musiques.txt"

    class LecteurMP3:
        def __init__(self):
            pygame.init()

            self.fenetre = tk.Tk()
            self.fenetre.title("Lecteur MP3")

            # --- Définir la couleur de fond ici ---
            # Vous pouvez essayer différentes nuances de bleu saphir:
            # Par exemple: '#306998' (un bleu légèrement plus clair)
            # Ou un bleu saphir plus profond: '#2C3E50' (bleu nuit/anthracite)
            # Ou encore un bleu saphir éclatant: '#007FFF' (bleu Capri)
            self.couleur_fond = '#306998'  # Bleu saphir légèrement foncé
            self.fenetre.configure(bg=self.couleur_fond)
            # --- Fin de la définition de la couleur de fond ---

            self.chanson_actuelle = None
            self.en_lecture = False
            self.musiques = []
            self.longueur_chanson = 0
            self.current_audio_device = None

            # Widgets (nous devrons peut-être ajuster le fond des widgets si nécessaire)
            # Par défaut, les widgets ttk s'adaptent au thème du système.
            # Si vous voulez un fond coloré pour les labels, il faudra spécifier bg=...
            self.label_chanson = ttk.Label(self.fenetre, text="Aucune chanson sélectionnée",
                                           background=self.couleur_fond,
                                           foreground="white")  # Texte blanc pour contraste
            self.label_chanson.pack(pady=10)

            self.bouton_ajouter = ttk.Button(self.fenetre, text="Enregistrer une nouvelle musique",
                                             command=self.ajouter_musique)
            self.bouton_ajouter.pack(pady=5)

            self.liste_musiques = tk.Listbox(self.fenetre, width=50, bg='#306998', fg='white',
                                             selectbackground='#007FFF',
                                             selectforeground='white')  # Fond bleu, texte blanc
            self.liste_musiques.pack(pady=5)
            self.liste_musiques.bind("<<ListboxSelect>>", self.selectionner_musique)

            # Cadre pour les boutons de contrôle (définir le fond pour le cadre aussi)
            control_frame = ttk.Frame(self.fenetre, style='ControlFrame.TFrame')
            control_frame.pack(pady=5)

            # Style pour le cadre des contrôles
            style = ttk.Style()
            style.configure('ControlFrame.TFrame', background=self.couleur_fond)

            self.bouton_lecture = ttk.Button(control_frame, text="▶", command=self.lecture_pause)
            self.bouton_lecture.grid(row=0, column=0, padx=5)

            self.bouton_stop = ttk.Button(control_frame, text="⏹", command=self.stop)
            self.bouton_stop.grid(row=0, column=1, padx=5)

            self.bouton_supprimer = ttk.Button(control_frame, text="Supprimer de la liste",
                                               command=self.supprimer_musique_de_liste)
            self.bouton_supprimer.grid(row=0, column=2, padx=5)
            self.bouton_supprimer.config(state=tk.DISABLED)

            self.scale_volume = ttk.Scale(self.fenetre, from_=0, to=100, orient='horizontal',
                                          command=self.changer_volume)
            self.scale_volume.pack(pady=10)
            self.scale_volume.set(70)

            self.barre_progression = ttk.Scale(self.fenetre, from_=0, to=100, orient='horizontal',
                                               command=self.regler_position_musique)
            self.barre_progression.pack(pady=10, fill='x', padx=20)
            self.barre_progression.bind("<ButtonRelease-1>", self.on_barre_progression_release)

            self.label_temps_actuel = ttk.Label(self.fenetre, text="00:00", background=self.couleur_fond,
                                                foreground="white")
            self.label_temps_actuel.pack(side=tk.LEFT, padx=20)
            self.label_temps_total = ttk.Label(self.fenetre, text="00:00", background=self.couleur_fond,
                                               foreground="white")
            self.label_temps_total.pack(side=tk.RIGHT, padx=20)

            self.charger_musiques_enregistrees()
            self.mettre_a_jour_barre_progression()

            self.initialiser_mixer()

        def initialiser_mixer(self, device_name=None):
            if pygame.mixer.get_init():
                pygame.mixer.quit()

            pygame.mixer.pre_init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=2048,
                devicename=device_name if device_name else None
            )
            pygame.mixer.init()
            print(
                f"Mixer Pygame initialisé avec le périphérique : {device_name if device_name else 'par défaut du système'}")
            self.changer_volume(self.scale_volume.get())

        def ajouter_musique(self):
            fichiers = filedialog.askopenfilenames(filetypes=[("Fichiers MP3", "*.mp3")])
            for fichier in fichiers:
                if fichier not in self.musiques:
                    self.musiques.append(fichier)
                    self.liste_musiques.insert(tk.END, os.path.basename(fichier))
            self.sauvegarder_musiques()

        def selectionner_musique(self, event):
            selection = self.liste_musiques.curselection()
            if selection:
                index = selection[0]
                self.chanson_actuelle = self.musiques[index]
                self.label_chanson.config(text=os.path.basename(self.chanson_actuelle))
                self.charger_et_jouer()
                self.bouton_supprimer.config(state=tk.NORMAL)
            else:
                self.bouton_supprimer.config(state=tk.DISABLED)

        def charger_et_jouer(self):
            if not pygame.mixer.get_init():
                self.initialiser_mixer(self.current_audio_device)

            pygame.mixer.music.load(self.chanson_actuelle)
            pygame.mixer.music.play()
            self.en_lecture = True
            self.bouton_lecture.config(text="⏸")
            self.longueur_chanson = pygame.mixer.Sound(self.chanson_actuelle).get_length()
            self.barre_progression.config(to=self.longueur_chanson)
            self.label_temps_total.config(text=self.formater_temps(self.longueur_chanson))
            self.mettre_a_jour_barre_progression()

        def lecture_pause(self):
            if self.chanson_actuelle:
                if self.en_lecture:
                    pygame.mixer.music.pause()
                    self.bouton_lecture.config(text="▶")
                else:
                    pygame.mixer.music.unpause()
                    self.bouton_lecture.config(text="⏸")
                self.en_lecture = not self.en_lecture

        def stop(self):
            if self.chanson_actuelle:
                pygame.mixer.music.stop()
                self.en_lecture = False
                self.bouton_lecture.config(text="▶")
                self.barre_progression.set(0)
                self.label_temps_actuel.config(text="00:00")

        def changer_volume(self, val):
            volume = float(val) / 100
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(volume)

        def regler_position_musique(self, val):
            pass

        def on_barre_progression_release(self, event):
            if self.chanson_actuelle:
                position_desiree = float(self.barre_progression.get())
                pygame.mixer.music.set_pos(position_desiree)
                if not self.en_lecture:
                    pygame.mixer.music.play(start=position_desiree)
                    pygame.mixer.music.pause()

        def mettre_a_jour_barre_progression(self):
            if self.chanson_actuelle and self.en_lecture:
                temps_actuel = pygame.mixer.music.get_pos() / 1000
                self.barre_progression.set(temps_actuel)
                self.label_temps_actuel.config(text=self.formater_temps(temps_actuel))
                if temps_actuel >= self.longueur_chanson - 1:
                    if not pygame.mixer.music.get_busy():
                        self.stop()
                        self.chanson_actuelle = None

            elif not self.en_lecture and self.chanson_actuelle and pygame.mixer.music.get_busy():
                temps_actuel = pygame.mixer.music.get_pos() / 1000
                self.label_temps_actuel.config(text=self.formater_temps(temps_actuel))

            self.fenetre.after(1000, self.mettre_a_jour_barre_progression)

        def formater_temps(self, secondes):
            minutes = int(secondes // 60)
            secondes_restantes = int(secondes % 60)
            return f"{minutes:02d}:{secondes_restantes:02d}"

        def supprimer_musique_de_liste(self):
            selection_index = self.liste_musiques.curselection()
            if not selection_index:
                messagebox.showinfo("Supprimer", "Veuillez sélectionner une musique à supprimer de la liste.")
                return

            index_a_supprimer = selection_index[0]
            chemin_musique = self.musiques[index_a_supprimer]
            nom_musique = os.path.basename(chemin_musique)

            confirmation = messagebox.askyesno(
                "Confirmation de suppression",
                f"Êtes-vous sûr de vouloir supprimer '{nom_musique}' de la liste ? La musique ne sera pas supprimée de votre ordinateur."
            )

            if confirmation:
                if self.chanson_actuelle == chemin_musique:
                    self.stop()
                    self.chanson_actuelle = None
                    self.label_chanson.config(text="Aucune chanson sélectionnée")
                    self.bouton_supprimer.config(state=tk.DISABLED)

                self.liste_musiques.delete(index_a_supprimer)
                self.musiques.pop(index_a_supprimer)
                self.sauvegarder_musiques()
                messagebox.showinfo("Supprimé", f"'{nom_musique}' a été supprimé de la liste.")
            else:
                messagebox.showinfo("Annulé", "Suppression annulée.")

        def sauvegarder_musiques(self):
            with open(FICHIER_MUSIQUES, "w", encoding="utf-8") as f:
                for chemin in self.musiques:
                    f.write(chemin + "\n")

        def charger_musiques_enregistrees(self):
            if os.path.exists(FICHIER_MUSIQUES):
                with open(FICHIER_MUSIQUES, "r", encoding="utf-8") as f:
                    for ligne in f:
                        chemin = ligne.strip()
                        if os.path.exists(chemin):
                            self.musiques.append(chemin)
                            self.liste_musiques.insert(tk.END, os.path.basename(chemin))

        def demarrer(self):
            self.fenetre.mainloop()

    if __name__ == "__main__":
        lecteur = LecteurMP3()
        lecteur.demarrer()

def open_notes():
    note_win = tk.Toplevel(root)
    note_win.title("Notes")
    note_win.geometry("600x400")  # Set a default size
    txt = tk.Text(note_win)
    txt.pack(expand=True, fill="both")

    def save_note():
        name = simpledialog.askstring("Nom", "Nom de la note:")
        if name:
            # Ensure filename is safe (no slashes, etc.)
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).strip()
            if not safe_name:
                messagebox.showerror("Erreur", "Nom de fichier invalide.")
                return

            file_path = os.path.join(DATA_DIR, f"{safe_name}.txt")
            with open(file_path, "w") as f:
                f.write(txt.get("1.0", "end-1c"))  # -1c to remove the extra newline
            messagebox.showinfo("Sauvegarde", "Note sauvegardée")
            note_win.destroy()  # Close note window after saving

    tk.Button(note_win, text="Sauvegarder", command=save_note).pack(pady=5)


def open_file_explorer():
    explorer = tk.Toplevel(root)
    explorer.title("Fichiers")
    explorer.geometry("600x400")

    # Frame for listing files
    file_list_frame = tk.Frame(explorer)
    file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(file_list_frame)
    scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def refresh_file_list():
        # Clear existing widgets in scrollable_frame
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
        if not files:
            tk.Label(scrollable_frame, text="Aucun fichier .txt trouvé.").pack(pady=10)
            return

        for file in files:
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill="x", pady=2, padx=5)
            tk.Label(frame, text=file, width=30, anchor="w").pack(side="left")

            tk.Button(frame, text="Lire", command=lambda f=file: open_file(f)).pack(side="left", padx=2)
            tk.Button(frame, text="Modifier", command=lambda f=file: modify_file(f, refresh_file_list)).pack(
                side="left", padx=2)
            tk.Button(frame, text="Renommer", command=lambda f=file: rename_file(f, refresh_file_list)).pack(
                side="left", padx=2)
            tk.Button(frame, text="Supprimer", command=lambda f=file: delete_file(f, refresh_file_list)).pack(
                side="left", padx=2)

    refresh_file_list()  # Initial load


def open_file(fname):
    file_path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(file_path):
        messagebox.showerror("Erreur", f"Le fichier '{fname}' n'existe pas.")
        return

    with open(file_path, "r") as f:
        content = f.read()
    read_win = tk.Toplevel(root)
    read_win.title(fname)
    text_display = tk.Text(read_win, wrap="word", height=15, width=60)
    text_display.insert("1.0", content)
    text_display.config(state="disabled")  # Make text read-only
    text_display.pack(padx=10, pady=10)
    tk.Button(read_win, text="Fermer", command=read_win.destroy).pack(pady=5)


def modify_file(fname, refresh_callback):
    file_path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(file_path):
        messagebox.showerror("Erreur", f"Le fichier '{fname}' n'existe pas.")
        return

    with open(file_path, "r") as f:
        content = f.read()
    mod_win = tk.Toplevel(root)
    mod_win.title(f"Modifier {fname}")
    txt = tk.Text(mod_win, wrap="word", height=15, width=60)
    txt.insert("1.0", content)
    txt.pack(padx=10, pady=10)

    def save_changes():
        with open(file_path, "w") as f:
            f.write(txt.get("1.0", "end-1c"))  # -1c to remove the extra newline
        messagebox.showinfo("Succès", "Modifications enregistrées.")
        mod_win.destroy()
        if refresh_callback:
            refresh_callback()

    tk.Button(mod_win, text="Enregistrer", command=save_changes).pack(pady=5)


def rename_file(fname, refresh_callback):
    old_path = os.path.join(DATA_DIR, fname)
    new_name = simpledialog.askstring("Renommer", "Nouveau nom (sans .txt):")
    if new_name:
        safe_new_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '.', '_')).strip()
        if not safe_new_name:
            messagebox.showerror("Erreur", "Nom de fichier invalide.")
            return

        new_path = os.path.join(DATA_DIR, f"{safe_new_name}.txt")
        if os.path.exists(new_path):
            messagebox.showerror("Erreur", "Un fichier avec ce nom existe déjà.")
            return

        try:
            os.rename(old_path, new_path)
            messagebox.showinfo("Renommé", "Fichier renommé avec succès.")
            if refresh_callback:
                refresh_callback()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de renommer le fichier: {e}")


def delete_file(fname, refresh_callback):
    file_path = os.path.join(DATA_DIR, fname)
    if messagebox.askyesno("Confirmer la suppression", f"Êtes-vous sûr de vouloir supprimer '{fname}' ?"):
        try:
            os.remove(file_path)
            messagebox.showinfo("Supprimé", "Fichier supprimé avec succès.")
            if refresh_callback:
                refresh_callback()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer le fichier: {e}")


def open_snake():
    snake_win = tk.Toplevel(root)
    snake_win.title("Snake")
    snake_win.resizable(False, False)

    canvas = tk.Canvas(snake_win, width=400, height=400, bg="black")
    canvas.pack()

    score = 0
    score_label = tk.Label(snake_win, text=f"Score : {score}", font=("Arial", 12), fg="white", bg="black")
    score_label.place(x=320, y=0)  # En haut à droite

    cell_size = 20
    direction = "Right"
    snake = [(5, 5)]
    food = (randint(0, 19), randint(0, 19))  # Initialize food

    # Ensure food doesn't spawn on snake initially
    while food in snake:
        food = (randint(0, 19), randint(0, 19))

    def draw():
        canvas.delete("all")
        for x, y in snake:
            canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size,
                                    fill="green")
        fx, fy = food
        canvas.create_oval(fx * cell_size, fy * cell_size, (fx + 1) * cell_size, (fy + 1) * cell_size, fill="red")

    def move():
        nonlocal food, score, direction
        head_x, head_y = snake[0]

        if direction == "Up":
            head_y -= 1
        elif direction == "Down":
            head_y += 1
        elif direction == "Left":
            head_x -= 1
        elif direction == "Right":
            head_x += 1

        new_head = (head_x, head_y)

        # Check for collision with self or walls
        if new_head in snake or not (0 <= head_x < 20 and 0 <= head_y < 20):
            messagebox.showinfo("Fin de partie", f"Score : {score}")
            snake_win.destroy()
            return

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            score_label.config(text=f"Score : {score}")
            while True:
                food = (randint(0, 19), randint(0, 19))
                if food not in snake:  # Ensure food doesn't spawn on snake
                    break
        else:
            snake.pop()  # Remove tail only if food not eaten

        draw()
        snake_win.after(150, move)

    def on_key(event):
        nonlocal direction
        current_direction = direction
        if event.keysym == "Up" and current_direction != "Down":
            direction = "Up"
        elif event.keysym == "Down" and current_direction != "Up":
            direction = "Down"
        elif event.keysym == "Left" and current_direction != "Right":
            direction = "Left"
        elif event.keysym == "Right" and current_direction != "Left":
            direction = "Right"

    snake_win.bind("<KeyPress>", on_key)
    snake_win.focus_set()
    draw()
    move()


def open_browser():
    url = simpledialog.askstring("URL",
                                 "Écrivez google.com pour visiter Google\nÉcrivez youtube.com pour visiter Youtube\nEntrez l'URL à charger :")
    if url:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url  # Prepend http:// if missing
        try:
            webbrowser.open(url)  # Use webbrowser for external opening
            messagebox.showinfo("Navigateur", f"Ouverture de {url} dans votre navigateur par défaut.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'URL: {e}")


def open_analyzer():
    info = tk.Toplevel(root)
    info.title("Analyse du PC")
    data = analyze_system()
    text = "\n".join(f"{k} : {v}" for k, v in data.items())
    tk.Label(info, text=text, justify="left").pack(padx=10, pady=10)


# ==== STORE ==== #
def open_store():
    store = tk.Toplevel(root)
    store.title("Nexa Store")
    store.geometry("400x300")

    # Use a frame to hold buttons, easier to refresh
    store_frame = tk.Frame(store)
    store_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_store_display():
        for widget in store_frame.winfo_children():
            widget.destroy()  # Clear previous buttons

        for app in AVAILABLE_APPS:
            frame = tk.Frame(store_frame)
            frame.pack(fill="x", pady=2)

            tk.Label(frame, text=app, width=20, anchor="w").pack(side="left")

            if app in config["installed_apps"]:
                tk.Button(frame, text="Désinstaller",
                          command=lambda a=app: uninstall_app(a, refresh_store_display)).pack(side="right")
            else:
                tk.Button(frame, text="Installer", command=lambda a=app: install_app(a, refresh_store_display)).pack(
                    side="right")

    refresh_store_display()  # Initial display


def install_app(app, refresh_callback=None):
    if app not in config["installed_apps"]:
        config["installed_apps"].append(app)
        save_config(config)
        messagebox.showinfo("Succès", f"{app} installé.")
        if refresh_callback:
            refresh_callback()
        main_os()  # Refresh main OS menu
    else:
        messagebox.showwarning("Info", f"{app} est déjà installé.")


def uninstall_app(app, refresh_callback=None):
    if app in config["installed_apps"]:
        config["installed_apps"].remove(app)
        save_config(config)
        messagebox.showinfo("Désinstallé", f"{app} désinstallé.")
        if refresh_callback:
            refresh_callback()
        main_os()  # Refresh main OS menu
    else:
        messagebox.showwarning("Erreur", f"{app} n'est pas installé.")


def open_task_manager():
    task_win = tk.Toplevel(root)
    task_win.title("Gestionnaire des tâches")
    task_win.geometry("400x300")

    frame = tk.Frame(task_win)
    frame.pack(fill="both", expand=True)

    # Get a list of all Toplevel windows that are not the task manager itself
    managed_windows = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel) and w != task_win]

    if not managed_windows:
        tk.Label(frame, text="Aucune tâche en cours.").pack(pady=10)
    else:
        for win in managed_windows:
            try:
                title = win.title()
                state = win.state()  # e.g., 'normal', 'iconic' (minimized)
                row = tk.Frame(frame)
                row.pack(fill="x", pady=2)

                tk.Label(row, text=title, width=25, anchor="w").pack(side="left")
                tk.Label(row, text=f"État: {state}", width=10).pack(side="left")

                # Closure to pass the current window to the command
                def make_close_action(window_to_close):
                    def close_and_refresh():
                        try:
                            window_to_close.destroy()
                        except tk.TclError:  # Handle if window is already destroyed
                            pass
                        task_win.destroy()  # Close current task manager
                        open_task_manager()  # Reopen to refresh list

                    return close_and_refresh

                tk.Button(row, text="Fermer", command=make_close_action(win)).pack(side="right")
            except tk.TclError:
                # This can happen if a window was destroyed just before iteration
                continue


def main_os():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=config.get("bg_color", "#ffffff"))

    menu = tk.Menu(root)
    app_menu = tk.Menu(menu, tearoff=0)
    param_menu = tk.Menu(menu, tearoff=0)
    alim_menu = tk.Menu(menu, tearoff=0)

    # Dynamically add installed apps to the menu
    app_mapping = {
        "Notes": open_notes,
        "Fichiers": open_file_explorer,
        "Navigateur": open_browser,
        "Analyse du PC": open_analyzer,
        "Snake": open_snake,
        "Lecteur MP3": open_mp3_playeur
    }

    for app in config.get("installed_apps", []):
        if app in app_mapping:
            app_menu.add_command(label=app, command=app_mapping[app])

    app_menu.add_separator()
    app_menu.add_command(label="Gestionnaire des tâches", command=open_task_manager)

    # ==== PARAMÈTRES DIRECTEMENT DANS LE MENU ==== #
    def change_color():
        color_code = colorchooser.askcolor(title="Choisir une couleur de fond")[1]
        if color_code:
            config["bg_color"] = color_code
            save_config(config)
            root.configure(bg=color_code)

    def change_password():
        # If no password is set, allow setting a new one directly
        if not config.get("password"):
            new = simpledialog.askstring("Nouveau mot de passe",
                                         "Entrez le nouveau mot de passe (laissez vide pour aucun):", show='*')
            config["password"] = new if new else ""
            save_config(config)
            messagebox.showinfo("Succès", "Mot de passe défini.")
            return

        old = simpledialog.askstring("Ancien mot de passe", "Entrez l'ancien mot de passe:", show='*')
        if old == config.get("password"):
            new = simpledialog.askstring("Nouveau mot de passe",
                                         "Entrez le nouveau mot de passe (laissez vide pour aucun):", show='*')
            config["password"] = new if new else ""
            save_config(config)
            messagebox.showinfo("Succès", "Mot de passe changé")
        else:
            messagebox.showerror("Erreur", "Ancien mot de passe incorrect.")

    # Ajouter les paramètres dans le menu
    param_menu.add_command(label="Changer la couleur du fond", command=change_color)
    param_menu.add_command(label="Changer le mot de passe", command=change_password)
    param_menu.add_command(label="Réinitialiser tout", command=reset_system)
    param_menu.add_command(label="Nexa Store", command=open_store)
    param_menu.add_command(label="Wifi", command=wifi_settings)
    param_menu.add_command(label="Clé USB", command=open_usb)

    # Alimentation
    def shut_down():
        if messagebox.askyesno("Éteindre le PC", "Êtes-vous sûr de vouloir éteindre l'ordinateur ?"):
            # This command is for Windows. For Linux/macOS, use different commands.
            # E.g., os.system("sudo shutdown -h now") for Linux (requires elevated privileges)
            # os.system("osascript -e 'tell app \"System Events\" to shut down'") for macOS
            try:
                os.system("shutdown /s /f /t 1")  # /s for shutdown, /f for force, /t 1 for 1 second delay
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'éteindre le PC: {e}")

    def lock_workstation():
        # This will return to the login screen, effectively "locking" the Nexa OS
        login_screen()

    menu.add_cascade(label="Menu", menu=app_menu)
    menu.add_cascade(label="Paramètres", menu=param_menu)
    alim_menu.add_command(label="Éteindre le PC", command=shut_down)
    alim_menu.add_command(label="Verrouiller", command=lock_workstation)
    menu.add_cascade(label="Alimentation", menu=alim_menu)
    credits_menu = tk.Menu(menu, tearoff=0)
    credits_menu.add_command(label="À propos",
                             command=lambda: messagebox.showinfo("À propos",
                                                                 "Nom : Nexa OS\nVersion : 1.0\nCréé par : Lorenzo\nMerci d'utiliser notre OS !"))

    menu.add_cascade(label="Nexa OS", menu=credits_menu)

    root.config(menu=menu)


# ==== DÉMARRER ==== #
# ==== CLÉ USB ==== #
def open_usb():
    usb_win = tk.Toplevel(root)
    usb_win.title("Clé USB")
    usb_win.geometry("500x400")

    usb_drives = [p.device for p in psutil.disk_partitions() if 'removable' in p.opts.lower()]
    if not usb_drives:
        tk.Label(usb_win, text="Aucune clé USB détectée.").pack(padx=10, pady=10)
        return

    # Use a scrollable frame for USB content if there are many files
    usb_content_frame = tk.Frame(usb_win)
    usb_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(usb_content_frame)
    scrollbar = ttk.Scrollbar(usb_content_frame, orient="vertical", command=canvas.yview)
    scrollable_usb_frame = ttk.Frame(canvas)

    scrollable_usb_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_usb_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    found_usb_content = False
    for drive in usb_drives:
        try:
            files = os.listdir(drive)

            tk.Label(scrollable_usb_frame, text=f"Contenu de {drive}:", font=("Arial", 10, "bold")).pack(pady=(10, 0),
                                                                                                         anchor="w")

            if not files:
                tk.Label(scrollable_usb_frame, text=f"{drive} est vide.").pack(padx=10, anchor="w")
                found_usb_content = True
                continue

            for file in files:
                full_path = os.path.join(drive, file)
                if os.path.isfile(full_path):
                    found_usb_content = True
                    frame = tk.Frame(scrollable_usb_frame)
                    frame.pack(fill="x", padx=10, pady=2)
                    tk.Label(frame, text=file, width=30, anchor="w").pack(side="left")

                    if file.endswith(".txt"):
                        tk.Button(frame, text="Importer", command=lambda src=full_path: import_txt_file(src)).pack(
                            side="right")

                    # Add a move button for files already on the USB drive
                    tk.Button(frame, text="Copier vers Nexa OS",
                              command=lambda src=full_path: copy_file_to_mini_os(src)).pack(side="right")
        except Exception as e:
            tk.Label(scrollable_usb_frame, text=f"Erreur avec {drive} : {e}", fg="red").pack(padx=10, anchor="w")

    if not found_usb_content and not usb_drives:
        tk.Label(scrollable_usb_frame, text="Aucun contenu détecté sur les clés USB.").pack(padx=10, pady=10)

    # Button to move files from Nexa OS to USB
    tk.Button(usb_win, text="Copier un fichier de Nexa OS vers USB",
              command=lambda: select_file_to_move(usb_drives)).pack(pady=10)


def import_txt_file(src_path):
    if not os.path.exists(src_path):
        messagebox.showerror("Erreur", "Le fichier source n'existe pas.")
        return

    file_name = os.path.basename(src_path)
    dest_path = os.path.join(DATA_DIR, file_name)

    if os.path.exists(dest_path):
        if not messagebox.askyesno("Fichier existant",
                                   f"Le fichier '{file_name}' existe déjà dans Nexa OS. Voulez-vous le remplacer ?"):
            return

    try:
        shutil.copy(src_path, dest_path)
        messagebox.showinfo("Succès", f"'{file_name}' importé dans Nexa OS.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'importer le fichier: {e}")


def copy_file_to_mini_os(src_path):
    import_txt_file(src_path)  # Reuse the import function


def wifi_settings():
    def scan_wifi():
        networks_listbox.delete(0, tk.END)
        try:
            # For Windows systems
            if platform.system() == "Windows":
                result = os.popen("netsh wlan show networks").read()
                lines = result.splitlines()
                ssids = set()
                for line in lines:
                    if "SSID" in line and ":" in line:
                        ssid = line.split(":", 1)[1].strip()
                        if ssid and ssid != 'N/A':
                            ssids.add(ssid)
                if ssids:
                    for ssid in sorted(list(ssids)):
                        networks_listbox.insert(tk.END, ssid)
                else:
                    networks_listbox.insert(tk.END, "Aucun réseau Wi-Fi trouvé.")
            else:
                # Placeholder for non-Windows (Linux/macOS)
                networks_listbox.insert(tk.END, "La numérisation Wi-Fi n'est pas prise en charge sur ce système.")
                messagebox.showwarning("Non pris en charge",
                                       "La numérisation Wi-Fi via 'netsh' est uniquement prise en charge sur Windows.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de scanner le Wi-Fi:\n{e}")

    def connect_wifi():
        ssid = networks_listbox.get(tk.ACTIVE)
        if not ssid or ssid == "Aucun réseau Wi-Fi trouvé." or "La numérisation Wi-Fi n'est pas prise en charge" in ssid:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un réseau valide.")
            return

        password = simpledialog.askstring("Connexion Wi-Fi", f"Mot de passe pour '{ssid}' (laisser vide si aucun) :",
                                          show='*')

        # Only proceed if password dialog wasn't cancelled
        if password is not None:
            profile_name = ssid
            # XML configuration for WPA2PSK
            config_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{profile_name}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            {"<sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>" + password + "</keyMaterial></sharedKey>" if password else "<openAuth><openAuthentication>None</openAuthentication></openAuth>"}
        </security>
    </MSM>
</WLANProfile>"""
            # For open networks, the security part needs to be different.
            # Simplified for now assuming WPA2PSK or no password for simplicity.

            try:
                # Save profile to a temporary XML file
                temp_profile_file = "wifi_profile.xml"
                with open(temp_profile_file, "w") as f:
                    f.write(config_xml)

                # Add profile and connect using netsh (Windows specific)
                os.system(f'netsh wlan add profile filename="{temp_profile_file}" interface="Wi-Fi"')
                os.system(f'netsh wlan connect name="{profile_name}" ssid="{ssid}" interface="Wi-Fi"')

                messagebox.showinfo("Connexion", f"Tentative de connexion à '{ssid}'.")

                # Clean up temporary file
                if os.path.exists(temp_profile_file):
                    os.remove(temp_profile_file)

            except Exception as e:
                messagebox.showerror("Erreur de connexion", f"Impossible de se connecter au Wi-Fi:\n{e}")
                if os.path.exists(temp_profile_file):
                    os.remove(temp_profile_file)

    wifi_win = tk.Toplevel(root)
    wifi_win.title("Paramètres Wi-Fi")
    wifi_win.geometry("400x300")

    networks_listbox = tk.Listbox(wifi_win, width=50, height=10)
    networks_listbox.pack(padx=10, pady=10)

    tk.Button(wifi_win, text="Scanner les réseaux", command=scan_wifi).pack(pady=5)
    tk.Button(wifi_win, text="Se connecter", command=connect_wifi).pack(pady=5)

    scan_wifi()  # initial scan on opening


def select_file_to_move(usb_drives):
    if "Fichiers" not in config.get("installed_apps", []):
        messagebox.showerror("Erreur",
                             "L'application 'Fichiers' n'est pas installée.\nVeuillez l'installer depuis le Nexa Store.")
        return

    if not usb_drives:
        messagebox.showwarning("Avertissement", "Aucune clé USB détectée pour le déplacement de fichiers.")
        return

    files = os.listdir(DATA_DIR)
    txt_files = [f for f in files if f.endswith(".txt")]

    if not txt_files:
        messagebox.showinfo("Infos", "Aucun fichier .txt disponible dans les fichiers de Nexa OS à copier.")
        return

    move_win = tk.Toplevel(root)
    move_win.title("Sélectionnez un fichier à copier sur la clé USB")
    move_win.geometry("500x350")

    tk.Label(move_win, text="Fichiers de Nexa OS :").pack(pady=5)

    listbox = tk.Listbox(move_win, width=60, height=8)
    listbox.pack(padx=10, pady=5)

    for f in txt_files:
        listbox.insert(tk.END, f)

    tk.Label(move_win, text="Sélectionnez la clé USB de destination :").pack(pady=5)
    usb_drive_var = tk.StringVar(move_win)
    # Set default value if drives exist
    if usb_drives:
        usb_drive_var.set(usb_drives[0])
    usb_drive_menu = ttk.OptionMenu(move_win, usb_drive_var, usb_drive_var.get(), *usb_drives)
    usb_drive_menu.pack(pady=5)

    def move_file():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un fichier à copier.")
            return
        selected_file = txt_files[selection[0]]
        selected_drive = usb_drive_var.get()

        if not selected_drive:
            messagebox.showerror("Erreur", "Veuillez sélectionner une clé USB de destination.")
            return

        src_path = os.path.join(DATA_DIR, selected_file)
        dest_path = os.path.join(selected_drive, selected_file)

        try:
            shutil.copy(src_path, dest_path)
            messagebox.showinfo("Succès", f"'{selected_file}' a été copié sur la clé USB '{selected_drive}'.")
            move_win.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier le fichier : {e}")

    tk.Button(move_win, text="Copier vers USB", command=move_file).pack(pady=10)


root = tk.Tk()
root.title("Nexa OS")
root.attributes('-fullscreen', True)  # Start in fullscreen

# Initial call to login_screen to start the application flow
login_screen()

# Add a robust error handling for mainloop
try:
    root.mainloop()
except tk.TclError as e:
    if "main loop is already running" in str(e):
        print(f"Tkinter error: {e}. Application might have been closed unexpectedly.")
    else:
        print(f"A Tkinter error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    try:
        root.destroy()
    except:
        pass  # La fenêtre est déjà détruite
    print("Nexa OS closed.")