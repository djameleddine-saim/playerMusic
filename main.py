
from pygame import mixer
import tkinter
from tkinter import ttk
from tkinter.filedialog import askdirectory
import os
import random
import eyed3

# Définissez le niveau de journalisation de la bibliothèque EyeD3 sur ERROR
eyed3.log.setLevel("ERROR")

# Initialize variables
p = False
current_pos = 0

repeat_status = False
random_status = False

# Espace réservé pour name_scrolling_task
name_scrolling_task = str()
current_max = int()

# Espace réservé pour les longueurs de chanson
song_lengths = {}

# Créer une fenêtre pour le "Player_music"
window = tkinter.Tk()
window.resizable(False, False)
window.title("Player_music")
window.config(bg="#2E8B57")

# Créer une variable qui contenir le nom de la chanson actuelle
var = tkinter.StringVar()
var.set("Select the song to play")

# Créer une variable qui contenir l'heure actuelle et max dans la chanson
current_time_max_ui = tkinter.StringVar()
current_time_ui = tkinter.StringVar()

# Remplacer le répertoire courant par le répertoire sélectionné par l'utilisateur
os.chdir(askdirectory())
# Obtenir la liste des chansons du répertoire
songlist = os.listdir()

# Créer une zone de liste pour afficher les chansons
playing = tkinter.Listbox(window, font="BOLD", width=50, bg="#006400", fg="white", selectmode=tkinter.SINGLE)

# Initialisation de mixer pour la lecture de la musique
mixer.init()


for song in songlist:
    playing.insert(tkinter.END, song)
    if song.endswith(".mp3"):
        song_lengths[song] = eyed3.load(song).info.time_secs

# Définition de la fonction de lecture de la musique
def play():
    global p, name_scrolling_task, current_max
    current_time_max_ui.set("00:00")
    current_time_ui.set("00:00")
    # Chargement de la chanson sélectionnée dans la liste
    current_song = playing.get(tkinter.ACTIVE)
    current_max = song_lengths[current_song]
    reset_progressbar()
    mixer.music.load(current_song)
    name = current_song.rstrip(".mp3 ") + " " * 4
    if name_scrolling_task:
        window.after_cancel(name_scrolling_task)
    name_scrolling_task = window.after(0, name_scrolling, name)
    # Lecture de la chanson
    mixer.music.play()
    p = False
    # Mise à jour du bouton pause
    pause_button.config(text="Pause", bg="#2E8B57",)
    current_time_max_ui.set(str(convert(current_max)))
    progressbar.config(maximum=current_max)


def on_song_end():
    if repeat_status:
        play()
    elif random_status:
        choose_random_song()
    else:
        next_song()

# Définition de la fonction pour arrêter la lecture de la musique
def stop():
    global p, name_scrolling_task
    # Arrêt de la lecture de la musique
    mixer.music.stop()
    p = False
    # Mise à jour du bouton pause
    pause_button.config(text="Pause", bg="#2E8B57",)
    if name_scrolling_task:
        window.after_cancel(name_scrolling_task)
    var.set("Select the song to play")
    current_time_max_ui.set("")
    current_time_ui.set("")
    reset_progressbar()


def name_scrolling(name):
    global name_scrolling_task
    var.set(name[:20])
    name_scrolling_task = window.after(250, name_scrolling, name[1:]+name[0])

# Définition de la fonction pour mettre en pause la lecture de la musique
def pause():
    global p, current_pos
    if not p:
        # Mise en pause de la lecture de la musique
        mixer.music.pause()
        p = True
        # Mise à jour du bouton pause
        pause_button.config(text="Resume")
    else:
        mixer.music.unpause()
        p = False
        pause_button.config(text="Pause")

# Définition de la fonction pour changer le volume de la lecture de la musique
def change_volume(v):
    # Changement du volume de la lecture de la musique
    mixer.music.set_volume(int(v)/100)

# Définition de la fonction pour passer à la chanson précédente
def previous_song():
    # Récupération de la chanson actuellement sélectionnée
    current_song = playing.curselection()
    # Si aucune chanson n'est sélectionnée, définir la chanson précédente comme étant la première chanson de la liste
    if not current_song:
        previous_song = 0
    else:
        previous_song = current_song[0] - 1
    # Si la chanson précédente est la première chanson de la liste, définir la dernière chanson comme étant la chanson précédente
    if previous_song < 0:
        previous_song = len(songlist) - 1
    # Sélection de la chanson précédente dans la liste
    playing.activate(previous_song)
    playing.selection_clear(0, len(songlist) - 1)
    playing.activate(previous_song)
    playing.selection_set(previous_song, last=previous_song)
    # Lecture de la chanson précédente
    play()

# Définition de la fonction pour passer à la chanson suivante
def next_song():
    # Récupération de la chanson actuellement sélectionnée
    current_song = playing.curselection()
    # Si aucune chanson n'est sélectionnée, la prochaine chanson sera la première de la liste
    if not current_song:
        next_song = 0
    else:
        next_song = current_song[0] + 1
    # Si la prochaine chanson dépasse la longueur de la liste, recommencer à la première chanson
    if next_song >= len(songlist):
        next_song = 0
    # Sélectionne la prochaine chanson dans la liste
    playing.activate(next_song)
    playing.selection_clear(0, len(songlist) - 1)
    playing.activate(next_song)
    playing.selection_set(next_song, last=next_song)
    play()


def update():
    # Vérifie si la lecture de la musique est en cours
    if not p and mixer.music.get_busy():
        global current_pos, current_max
        # Met à jour la barre de progression
        progressbar.config(value=current_pos)
        current_pos += 1
        # Met à jour l'affichage du temps de lecture
        current_time_ui.set(str(convert(current_pos)))
        # Répète la mise à jour toutes les secondes
        window.after(1000, update)
        # Si la lecture est terminée
        if current_pos >= int(current_max) - 1:
            # Si la lecture est terminée
            on_song_end()
    else:
        # Si la lecture est terminée
        window.after(1000, update)

# Mise à jour de la position de la chanson en cours de lecture lors du clic sur la barre de progression
def on_progressbar_click(event):
    global current_pos, p
    # Définition de la nouvelle position en fonction de l'emplacement du clic
    new_pos = int(event.x * progressbar['maximum'] / progressbar.winfo_width())
    current_pos = new_pos
    # Réinitialisation de la chanson et mise à jour de la position
    mixer.music.rewind()
    mixer.music.set_pos(new_pos)
    progressbar.config(value=new_pos)
    # Si la chanson était en pause, la lecture reprend
    if p:
        mixer.music.unpause()
        p = False
        pause_button.config(text="Pause")
# Fonction pour réinitialiser la barre de progression de la musique
def reset_progressbar():
    # Mettre la variable globale current_pos à0
    global current_pos
    current_pos = 0
    # Mettre la valeur de la barre de progression à current_pos
    progressbar.config(value=current_pos)


# Fonction pour choisir une chanson au hasard dans la liste de chansons
def choose_random_song():
    # Choisir une chanson au hasard dans la liste
    random_song = random.choice(songlist)
    # Activer la chanson choisie dans la liste de lecture
    playing.activate(songlist.index(random_song))
    # Désélectionner toutes les chansons dans la liste de lecture
    playing.selection_clear(0, len(songlist) - 1)
    # Activer la chanson choisie dans la liste de lecture
    playing.activate(songlist.index(random_song))
    # Sélectionner la chanson choisie dans la liste de lecture
    playing.selection_set(songlist.index(random_song), last=songlist.index(random_song))
    # Jouer la chanson choisie
    play()


def convert(seconds):
    # Convertissez le nombre total de secondes en quelques secondes en une minute
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    # Obtenez la valeur des minutes à partir des secondes
    minutes = seconds // 60
    # Obtenez les secondes restantes
    seconds %= 60

    # Return the time in the format "mm:ss"
    return "%02d:%02d" % (minutes, seconds)

# affiche la liste des musiques
playing.grid(columnspan=4, row=0, padx=5,pady=5)

# Créer une étiquette pour afficher l'heure actuelle de la chanson
current_t = tkinter.Label(window, font="BOLD", bg="#2E8B57", textvariable=current_time_ui)
current_t.grid(row=2, column=0)

# Créer une étiquette pour afficher la durée maximale de la chanson
max_t = tkinter.Label(window, font="BOLD", bg="#2E8B57", textvariable=current_time_max_ui)
max_t.grid(row=2, column=2)

# Créer une étiquette pour afficher le titre de la chanson
text = tkinter.Label(window, font="BOLD", textvariable=var, pady=10, bg="#2E8B57",)
text.grid(row=4, columnspan=3)

# Créez le bouton "Play" et configurez-le pour appeler la fonction "play" lorsque vous cliquez dessus
play_button = tkinter.Button(window, width=7, height=1, font="BOLD", text="Play", bg="#2E8B57", command=play, relief="groove")
play_button.grid(row=1, column=0)

# Créez le bouton "Stop" et configurez-le pour appeler la fonction "stop" lorsqu'il est cliqué
stop_button = tkinter.Button(window,width=7, height=1, font="BOLD", text="Stop", bg="#2E8B57", command=stop, relief="groove")
stop_button.grid(row=1, column=2)

# Créez le bouton "Pause" et configurez-le pour appeler la fonction "pause" lorsqu'il est cliqué
pause_button = tkinter.Button(window, width=7, height=1, font="BOLD", text="Pause", bg="#2E8B57", command=pause, fg="black", relief="groove")
pause_button.grid(row=5, column=1)

# Créer un curseur de contrôle du volume
volume = tkinter.Scale(window, from_=0, to=8, orient="horizontal", length=200, font="BOLD", bg="#2E8B57", command=change_volume)
volume.set(100)
volume.grid(row=7, column=1)

# Créez le bouton "Suivant" et configurez-le pour appeler la fonction "next_song" lorsqu'il est cliqué
next_button = tkinter.Button(window, width=7, height=1, font="BOLD", text="Next", bg="#2E8B57", command=next_song, relief="groove")
next_button.grid(row=3, column=2)

# Créez le bouton "Précédent" et configurez-le pour appeler la fonction "previous_song" lorsqu'il est cliqué
previous_button = tkinter.Button(window, width=7, height=1, font="BOLD", text="Previous", bg="#2E8B57", command=previous_song, relief="groove")
previous_button.grid(row=3, column=0)

# Créez une barre de progression et liez-la à la fonction "on_progressbar_click"
progressbar = ttk.Progressbar(window, length=250)
progressbar.grid(row=2, column=1, columnspan=1, pady=10,)
progressbar.bind("<Button-1>", on_progressbar_click)

# Démarrer la boucle principale de l'interface graphique
update()

# Afficher la fenêtre
window.mainloop()
