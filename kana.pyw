import os
import sys
import tkinter as tk
import random

def resource_path(relative_path):
    """Obtenir le chemin absolu du fichier de ressources (dict.txt)"""
    try:
        # Pour les exécutables générés par PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # Pour le développement local
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# Fonction pour charger le dictionnaire à partir d'un fichier externe
def load_kana_dict(file_path):
    kana_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignorer les lignes vides et les commentaires
                romaji, hiragana, katakana = line.split(':')
                kana_dict[hiragana] = (katakana, romaji)
    # Ajouter les correspondances inversées
    kana_dict.update({v[0]: (k, v[1]) for k, v in kana_dict.items()})
    romaji_dict = {v[1]: (k, v[0]) for k, v in kana_dict.items()}
    return kana_dict, romaji_dict

class KanaApp:
    def __init__(self, root, kana_dict, romaji_dict):
        self.root = root
        self.root.title("Kana Trainer")
        self.root.attributes("-fullscreen", True)  # Mode plein écran

        self.display_label = tk.Label(root, font=("Arial", 100))
        self.display_label.pack(expand=True)
        self.answer_label = tk.Label(root, font=("Arial", 20))
        self.answer_label.pack()
        self.counter_label = tk.Label(root, font=("Arial", 20))
        self.counter_label.pack()
        self.score_label = tk.Label(root, font=("Arial", 20), fg="green")  # Affichage du score en vert
        self.score_label.pack()

        # Associer les touches aux fonctions
        self.root.bind('<space>', self.mark_correct_default)
        self.root.bind('<Up>', self.mark_correct)
        self.root.bind('<Down>', self.mark_incorrect)
        self.root.bind('<Escape>', self.exit_fullscreen)

        # Variables pour suivre l'état
        self.kana_dict = kana_dict
        self.romaji_dict = romaji_dict
        self.current_display = None
        self.current_answer = None
        self.answer_shown = False
        self.total_attempts = 0
        self.correct_answers = 0
        self.incorrect_kana = {}  # Suivi des kana ou romaji incorrects pour révision

        # Initialiser l'application avec un caractère
        self.next_kana()

    def next_kana(self):
        # Choisir un caractère aléatoire
        self.current_display, self.current_answer = self.get_random_character()
        self.display_label['text'] = self.current_display
        self.answer_label['text'] = ''
        self.answer_shown = False

    def get_random_character(self):
        # Si des caractères incorrects existent, donner la priorité pour la révision
        if self.incorrect_kana and random.random() < 0.5:
            choice = random.choice(list(self.incorrect_kana.keys()))
            return choice, self.incorrect_kana[choice]
        
        # Sinon, choisir aléatoirement un caractère
        choice_type = random.choice(['kana', 'romaji'])
        if choice_type == 'kana':
            kana, (other_kana, romaji) = random.choice(list(self.kana_dict.items()))
            if kana in self.kana_dict:
                return kana, f"{other_kana} / {romaji}"
            else:
                return other_kana, f"{kana} / {romaji}"
        else:
            romaji, (hiragana, katakana) = random.choice(list(self.romaji_dict.items()))
            return romaji, f"{hiragana} / {katakana}"

    def mark_correct_default(self, event=None):
        # Marque comme correct par défaut (espace)
        if not self.answer_shown:
            self.toggle_display()
            # Mise à jour du compteur d'essais
            self.total_attempts += 1
            self.update_counter()
        else:
            self.mark_correct()

    def mark_correct(self, event=None):
        # Marquer la réponse comme correcte
        self.correct_answers += 1
        if self.current_display in self.incorrect_kana:
            del self.incorrect_kana[self.current_display]
        self.next_kana()
        self.update_score()

    def mark_incorrect(self, event=None):
        # Marquer la réponse comme incorrecte
        self.incorrect_kana[self.current_display] = self.current_answer
        self.next_kana()
        self.update_score()

    def toggle_display(self, event=None):
        if self.answer_shown:
            self.next_kana()
        else:
            self.answer_label['text'] = self.current_answer
            self.answer_shown = True

    def update_counter(self):
        self.counter_label['text'] = f"Total attempts : {self.total_attempts}"

    def update_score(self):
        self.score_label['text'] = f"Score : {self.correct_answers} / {self.total_attempts}"

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

if __name__ == "__main__":
    root = tk.Tk()
    dict_file = resource_path("dict.txt")  # Charger le dictionnaire externe depuis le package
    kana_dict, romaji_dict = load_kana_dict(dict_file)
    app = KanaApp(root, kana_dict, romaji_dict)
    root.mainloop()
