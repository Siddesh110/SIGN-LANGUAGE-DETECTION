import customtkinter as ctk
from PIL import Image
import os
import threading
from tkinter import filedialog
from webcam_detection import (
    run_webcam_detection, stop_webcam, practice_word,
    session_stats, reset_session_stats
)
BASE_DIR = r"C:\SignEase\SignEase"
ASSETS = os.path.join(BASE_DIR, "assets")
SIDEBAR_ICON  = os.path.join(ASSETS, "logo.png")
DISPLAY_IMAGE = os.path.join(ASSETS, "hand.png")
THEMES = {
    "Blue": {
        "bg": "#0B1B33", "sidebar": "#071427", "panel": "#0E223F",
        "box": "#1A2E4A", "button": "#1F4E79", "hover": "#256192", "text": "white"
    },
    "White": {
        "bg": "#F8F9FA", "sidebar": "#E9ECEF", "panel": "#FFFFFF",
        "box": "#DEE2E6", "button": "#6C757D", "hover": "#5A6268", "text": "black"
    },
    "Grey": {
        "bg": "#2E2E2E", "sidebar": "#1E1E1E", "panel": "#3A3A3A",
        "box": "#4A4A4A", "button": "#757575", "hover": "#9E9E9E", "text": "white"
    }
}
current_theme_name = "Blue"
current_theme = THEMES[current_theme_name]
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Indian Sign Language Detection")
app.resizable(True, True)
app.update_idletasks()
w, h = app.winfo_screenwidth(), app.winfo_screenheight()
app.geometry(f"{w}x{h}+0+0")
app.after(50, lambda: app.state("zoomed"))
current_username    = ctk.StringVar(value="Siddesh")
current_profile_path = None
bg_frame = ctk.CTkFrame(app, fg_color=current_theme["bg"])
bg_frame.pack(fill="both", expand=True)
sidebar = ctk.CTkFrame(bg_frame, width=220,
                       fg_color=current_theme["sidebar"], corner_radius=15)
sidebar.place(x=40, y=40, relheight=0.90)
if os.path.exists(SIDEBAR_ICON):
    try:
        logo = ctk.CTkImage(Image.open(SIDEBAR_ICON), size=(90, 90))
        ctk.CTkLabel(sidebar, image=logo, text="").pack(pady=(50, 10))
    except Exception:
        pass
app_name_label = ctk.CTkLabel(
    sidebar,
    text="Indian\nSign Language\nDetection",
    font=("Segoe UI", 18, "bold"),
    text_color=current_theme["text"],
    justify="center"
)
app_name_label.pack(pady=10)
profile_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
profile_frame.pack(pady=20)
profile_image_label = ctk.CTkLabel(profile_frame, text="")
profile_image_label.pack(pady=5)
username_label = ctk.CTkLabel(
    profile_frame,
    textvariable=current_username,
    font=("Segoe UI", 16, "bold"),
    text_color=current_theme["text"]
)
username_label.pack()
title_label = ctk.CTkLabel(
    bg_frame,
    text="Indian Sign Language\nDetection and Learning System",
    font=("Segoe UI", 26, "bold"),
    text_color=current_theme["text"]
)
title_label.place(relx=0.55, rely=0.08, anchor="center")
main_panel = ctk.CTkFrame(bg_frame, fg_color=current_theme["panel"], corner_radius=20)
main_panel.place(relx=0.55, rely=0.48, anchor="center", relwidth=0.65, relheight=0.55)
display_box = ctk.CTkFrame(main_panel, fg_color=current_theme["box"], corner_radius=15)
display_box.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.90, relheight=0.70)
image_label = ctk.CTkLabel(display_box, text="")
image_label.place(relx=0.5, rely=0.5, anchor="center")
def load_image():
    try:
        img = Image.open(DISPLAY_IMAGE)
        bw, bh = display_box.winfo_width(), display_box.winfo_height()
        if bw < 10 or bh < 10:
            app.after(100, load_image)
            return
        img.thumbnail((bw, bh), Image.LANCZOS)
        img_ctk = ctk.CTkImage(img, size=(img.width, img.height))
        image_label.configure(image=img_ctk)
        image_label.image = img_ctk
    except Exception:
        pass
app.after(300, load_image)
button_frame = ctk.CTkFrame(bg_frame, fg_color=current_theme["bg"])
button_frame.place(relx=0.55, rely=0.90, anchor="center", relwidth=0.75, relheight=0.15)
main_buttons    = []
settings_buttons = []
settings_labels  = []
settings_dropdown = None
settings_window   = None
def create_button(text, command, relx, rely):
    btn = ctk.CTkButton(
        button_frame, text=text, command=command,
        width=160, height=45, corner_radius=18,
        font=("Segoe UI", 14, "bold"),
        fg_color=current_theme["button"],
        hover_color=current_theme["hover"]
    )
    btn.place(relx=relx, rely=rely, anchor="center")
    main_buttons.append(btn)
    return btn
def start_detection():
    threading.Thread(target=run_webcam_detection, daemon=True).start()
ISL_DESCRIPTIONS = {
    "A": "Fist with thumb resting on the side",
    "B": "Four fingers straight up, thumb folded in",
    "C": "Curved hand like holding a ball",
    "D": "Index finger up, other fingers curved touching thumb",
    "E": "All fingers bent, touching the thumb",
    "F": "Index and thumb circle, other fingers up",
    "G": "Index and thumb pointing sideways (like a gun)",
    "H": "Index and middle fingers pointing sideways",
    "I": "Pinky finger raised, fist",
    "J": "Pinky raised, trace a J in the air",
    "K": "Index up, middle angled, thumb between them",
    "L": "L-shape: index up, thumb out",
    "M": "Three fingers folded over the thumb",
    "N": "Two fingers folded over the thumb",
    "O": "All fingers and thumb form an O",
    "P": "Like K but pointing downward",
    "Q": "Like G but pointing downward",
    "R": "Index and middle fingers crossed",
    "S": "Fist with thumb over fingers",
    "T": "Thumb between index and middle finger in a fist",
    "U": "Index and middle fingers together, pointing up",
    "V": "Index and middle fingers spread (peace sign)",
    "W": "Index, middle, ring spread out",
    "X": "Index finger hooked/crooked",
    "Y": "Thumb and pinky extended (hang loose)",
    "Z": "Index finger traces a Z in the air",
}
def learn_isl():
    win = ctk.CTkToplevel(app)
    win.title("Learn ISL Alphabet")
    win.geometry("700x560")
    win.transient(app)
    win.grab_set()
    win.focus()
    win.configure(fg_color=current_theme["bg"])
    ctk.CTkLabel(win, text="ISL Fingerspelling Guide",
                 font=("Segoe UI", 22, "bold"),
                 text_color=current_theme["text"]).pack(pady=18)
    scroll = ctk.CTkScrollableFrame(win, fg_color=current_theme["panel"], corner_radius=12)
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    letters = sorted(ISL_DESCRIPTIONS.keys())
    for i, letter in enumerate(letters):
        row = ctk.CTkFrame(scroll, fg_color=current_theme["box"], corner_radius=10)
        row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row, text=letter,
                     font=("Segoe UI", 26, "bold"),
                     text_color=current_theme["hover"],
                     width=50).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(row, text=ISL_DESCRIPTIONS[letter],
                     font=("Segoe UI", 14),
                     text_color=current_theme["text"],
                     anchor="w",
                     justify="left").pack(side="left", padx=8, pady=12)
import random
QUIZ_WORDS = [
    "Hello", "Thank You", "Please", "Mother", "Father",
    "Brother", "Book", "", "", "Happy",
    "Sad", "Angry", "Cat", "Dog", "Water"
]
def practice_quiz():
    win = ctk.CTkToplevel(app)
    win.title("Practice / Quiz")
    win.geometry("500x420")
    win.transient(app)
    win.grab_set()
    win.focus()
    win.configure(fg_color=current_theme["bg"])
    ctk.CTkLabel(win, text="Quiz Mode",
                 font=("Segoe UI", 22, "bold"),
                 text_color=current_theme["text"]).pack(pady=20)
    info = ctk.CTkLabel(win,
        text="A random word will appear.\nSign each letter and press SPACE to submit it.\nPress Q in the camera window to stop.",
        font=("Segoe UI", 14),
        text_color=current_theme["text"],
        justify="center")
    info.pack(pady=10)
    result_var = ctk.StringVar(value="")
    result_label = ctk.CTkLabel(win, textvariable=result_var,
                                font=("Segoe UI", 16, "bold"),
                                text_color="#00CC66")
    result_label.pack(pady=6)
    word_var = ctk.StringVar(value="")
    word_label = ctk.CTkLabel(win, textvariable=word_var,
                              font=("Segoe UI", 20, "bold"),
                              text_color=current_theme["hover"])
    word_label.pack(pady=6)
    score_var = ctk.StringVar(value="Score: 0 correct / 0 wrong")
    ctk.CTkLabel(win, textvariable=score_var,
                 font=("Segoe UI", 13),
                 text_color=current_theme["text"]).pack(pady=4)
    def refresh_score():
        score_var.set(
            f"Score: {session_stats['correct']} correct / {session_stats['wrong']} wrong"
        )
    def on_result(word, res):
        emoji = "✔ Correct!" if res == "correct" else "✖ Wrong"
        result_var.set(f"{word}: {emoji}")
        app.after(0, refresh_score)
    def start_quiz():
        word = random.choice(QUIZ_WORDS)
        word_var.set(f"Sign: {word}")
        result_var.set("")
        threading.Thread(
            target=practice_word,
            args=(word, on_result),
            daemon=True
        ).start()
    ctk.CTkButton(win, text="Start Random Quiz",
                  width=260, height=45, corner_radius=18,
                  font=("Segoe UI", 14, "bold"),
                  fg_color=current_theme["button"],
                  hover_color=current_theme["hover"],
                  command=start_quiz).pack(pady=20)
    ctk.CTkButton(win, text="Reset Score",
                  width=160, height=36, corner_radius=14,
                  font=("Segoe UI", 12),
                  fg_color="#5A3030", hover_color="#7A3030",
                  command=lambda: [reset_session_stats(), refresh_score()]
                  ).pack()
def storytelling():
    vocab_win = ctk.CTkToplevel(app)
    vocab_win.title("Vocabulary")
    vocab_win.geometry("600x600")
    vocab_win.transient(app)
    vocab_win.grab_set()
    vocab_win.focus()
    vocab_win.configure(fg_color=current_theme["bg"])
    ctk.CTkLabel(vocab_win, text="Vocabulary",
                 font=("Segoe UI", 24, "bold"),
                 text_color=current_theme["text"]).pack(pady=25)
    words_frame = ctk.CTkFrame(vocab_win, fg_color=current_theme["panel"], corner_radius=15)
    words_frame.pack(pady=20, padx=40, fill="both", expand=True)
    words = [
        "Hello", "Thank You", "Please",
        "Mother", "Father", "Brother",
        "Book", "Teacher", "Student",
        "Happy", "Sad", "Angry"
    ]
    selected_word = ctk.StringVar(value="")
    def start_practice(word=None):
        if word is None:
            word = selected_word.get()
        if word:
            threading.Thread(target=practice_word, args=(word,), daemon=True).start()
    def create_word_button(word):
        btn = ctk.CTkButton(
            words_frame, text=word, height=45, corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color=current_theme["button"],
            hover_color=current_theme["hover"],
            command=lambda: selected_word.set(word)
        )
        btn.bind("<Double-Button-1>", lambda e: start_practice(word))
        return btn
    row = col = 0
    for word in words:
        btn = create_word_button(word)
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        col += 1
        if col > 2:
            col = 0
            row += 1
    for i in range(3):
        words_frame.grid_columnconfigure(i, weight=1)
    ctk.CTkButton(vocab_win, text="Practice Selected Word",
                  width=260, height=45, corner_radius=18,
                  font=("Segoe UI", 14, "bold"),
                  fg_color=current_theme["button"],
                  hover_color=current_theme["hover"],
                  command=start_practice).pack(pady=20)
def text_to_isl():
    win = ctk.CTkToplevel(app)
    win.title("Text / Speech to ISL Guide")
    win.geometry("640x520")
    win.transient(app)
    win.grab_set()
    win.focus()
    win.configure(fg_color=current_theme["bg"])
    ctk.CTkLabel(win, text="Text → ISL Fingerspelling",
                 font=("Segoe UI", 22, "bold"),
                 text_color=current_theme["text"]).pack(pady=18)
    ctk.CTkLabel(win, text="Type a word or phrase and see the handshape guide for each letter.",
                 font=("Segoe UI", 13),
                 text_color=current_theme["text"]).pack(pady=(0, 10))
    entry = ctk.CTkEntry(win, width=400, height=42, corner_radius=12,
                         font=("Segoe UI", 15),
                         placeholder_text="e.g. Hello")
    entry.pack(pady=6)
    result_frame = ctk.CTkScrollableFrame(win, fg_color=current_theme["panel"],
                                          corner_radius=12, height=280)
    result_frame.pack(fill="both", expand=True, padx=30, pady=14)
    def show_guide():
        for widget in result_frame.winfo_children():
            widget.destroy()
        text = entry.get().upper().strip()
        if not text:
            return
        for ch in text:
            if ch == " ":
                ctk.CTkLabel(result_frame, text="  [ SPACE ]  ",
                             font=("Segoe UI", 13, "italic"),
                             text_color=current_theme["hover"]).pack(anchor="w", pady=2, padx=10)
                continue
            if ch not in ISL_DESCRIPTIONS:
                ctk.CTkLabel(result_frame, text=f"  {ch}  — (no ISL reference available)",
                             font=("Segoe UI", 13),
                             text_color=current_theme["text"]).pack(anchor="w", pady=2, padx=10)
                continue
            row = ctk.CTkFrame(result_frame, fg_color=current_theme["box"], corner_radius=8)
            row.pack(fill="x", padx=6, pady=4)
            ctk.CTkLabel(row, text=ch,
                         font=("Segoe UI", 22, "bold"),
                         text_color=current_theme["hover"],
                         width=44).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=ISL_DESCRIPTIONS[ch],
                         font=("Segoe UI", 13),
                         text_color=current_theme["text"],
                         anchor="w", justify="left").pack(side="left", padx=6, pady=8)
    ctk.CTkButton(win, text="Show Guide",
                  width=200, height=42, corner_radius=18,
                  font=("Segoe UI", 14, "bold"),
                  fg_color=current_theme["button"],
                  hover_color=current_theme["hover"],
                  command=show_guide).pack(pady=4)
def progress_profile():
    win = ctk.CTkToplevel(app)
    win.title("Progress & Profile")
    win.geometry("560x560")
    win.transient(app)
    win.grab_set()
    win.focus()
    win.configure(fg_color=current_theme["bg"])
    ctk.CTkLabel(win, text="Progress & Profile",
                 font=("Segoe UI", 22, "bold"),
                 text_color=current_theme["text"]).pack(pady=18)
    profile_card = ctk.CTkFrame(win, fg_color=current_theme["panel"], corner_radius=12)
    profile_card.pack(fill="x", padx=30, pady=(0, 12))
    ctk.CTkLabel(profile_card, text="User",
                 font=("Segoe UI", 13),
                 text_color=current_theme["text"]).pack(anchor="w", padx=20, pady=(14, 0))
    ctk.CTkLabel(profile_card, textvariable=current_username,
                 font=("Segoe UI", 18, "bold"),
                 text_color=current_theme["hover"]).pack(anchor="w", padx=20, pady=(0, 14))
    stats_card = ctk.CTkFrame(win, fg_color=current_theme["panel"], corner_radius=12)
    stats_card.pack(fill="x", padx=30, pady=(0, 12))
    ctk.CTkLabel(stats_card, text="Session Stats",
                 font=("Segoe UI", 15, "bold"),
                 text_color=current_theme["text"]).pack(anchor="w", padx=20, pady=(14, 4))
    total = session_stats["correct"] + session_stats["wrong"]
    pct   = round(100 * session_stats["correct"] / total) if total else 0
    ctk.CTkLabel(stats_card,
                 text=f"Correct: {session_stats['correct']}   Wrong: {session_stats['wrong']}   "
                      f"Accuracy: {pct}%",
                 font=("Segoe UI", 14),
                 text_color=current_theme["text"]).pack(anchor="w", padx=20, pady=(0, 14))
    ctk.CTkLabel(win, text="Practice History",
                 font=("Segoe UI", 15, "bold"),
                 text_color=current_theme["text"]).pack(anchor="w", padx=30, pady=(4, 4))
    history_frame = ctk.CTkScrollableFrame(win, fg_color=current_theme["panel"],
                                           corner_radius=12, height=220)
    history_frame.pack(fill="both", expand=True, padx=30, pady=(0, 16))
    if not session_stats["history"]:
        ctk.CTkLabel(history_frame, text="No practice sessions yet.",
                     font=("Segoe UI", 13, "italic"),
                     text_color=current_theme["text"]).pack(pady=20)
    else:
        for entry in reversed(session_stats["history"]):
            color = "#00CC66" if entry["result"] == "correct" else "#CC3333"
            icon  = "✔" if entry["result"] == "correct" else "✖"
            row = ctk.CTkFrame(history_frame, fg_color=current_theme["box"], corner_radius=8)
            row.pack(fill="x", padx=6, pady=4)
            ctk.CTkLabel(row, text=icon,
                         font=("Segoe UI", 16, "bold"),
                         text_color=color, width=32).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=entry["word"],
                         font=("Segoe UI", 14),
                         text_color=current_theme["text"]).pack(side="left", pady=8)
def apply_theme(theme_name):
    global current_theme_name, current_theme
    current_theme_name = theme_name
    current_theme = THEMES[theme_name]
    bg_frame.configure(fg_color=current_theme["bg"])
    sidebar.configure(fg_color=current_theme["sidebar"])
    main_panel.configure(fg_color=current_theme["panel"])
    display_box.configure(fg_color=current_theme["box"])
    button_frame.configure(fg_color=current_theme["bg"])
    title_label.configure(text_color=current_theme["text"])
    app_name_label.configure(text_color=current_theme["text"])
    username_label.configure(text_color=current_theme["text"])
    for btn in main_buttons:
        btn.configure(fg_color=current_theme["button"], hover_color=current_theme["hover"])
    if settings_window and settings_window.winfo_exists():
        settings_window.configure(fg_color=current_theme["bg"])
        for lbl in settings_labels:
            lbl.configure(text_color=current_theme["text"])
        for btn in settings_buttons:
            btn.configure(fg_color=current_theme["button"], hover_color=current_theme["hover"])
        if settings_dropdown:
            settings_dropdown.configure(
                fg_color=current_theme["button"],
                button_color=current_theme["button"],
                button_hover_color=current_theme["hover"],
                text_color=current_theme["text"]
            )
def settings():
    global settings_window, settings_buttons, settings_labels, settings_dropdown
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Settings")
    settings_window.geometry("500x650")
    settings_window.transient(app)
    settings_window.grab_set()
    settings_window.focus()
    settings_window.configure(fg_color=current_theme["bg"])
    settings_buttons = []
    settings_labels  = []
    title = ctk.CTkLabel(settings_window, text="Settings",
                         font=("Segoe UI", 26, "bold"),
                         text_color=current_theme["text"])
    title.pack(pady=30)
    settings_labels.append(title)
    label_theme = ctk.CTkLabel(settings_window, text="Select Theme",
                               font=("Segoe UI", 16),
                               text_color=current_theme["text"])
    label_theme.pack(pady=(10, 8))
    settings_labels.append(label_theme)
    selected_theme = ctk.StringVar(value=current_theme_name)
    settings_dropdown = ctk.CTkOptionMenu(
        settings_window, values=list(THEMES.keys()),
        variable=selected_theme, width=280, height=45,
        fg_color=current_theme["button"],
        button_color=current_theme["button"],
        button_hover_color=current_theme["hover"],
        text_color=current_theme["text"]
    )
    settings_dropdown.pack(pady=10)
    apply_btn = ctk.CTkButton(
        settings_window, text="Apply Theme",
        width=280, height=45, corner_radius=20,
        font=("Segoe UI", 14, "bold"),
        fg_color=current_theme["button"],
        hover_color=current_theme["hover"],
        command=lambda: apply_theme(selected_theme.get())
    )
    apply_btn.pack(pady=15)
    settings_buttons.append(apply_btn)
    label_user = ctk.CTkLabel(settings_window, text="Change Username",
                              font=("Segoe UI", 16),
                              text_color=current_theme["text"])
    label_user.pack(pady=(25, 8))
    settings_labels.append(label_user)
    username_entry = ctk.CTkEntry(settings_window, width=280, height=45, corner_radius=15)
    username_entry.pack(pady=10)
    def update_username():
        new_name = username_entry.get()
        if new_name.strip():
            current_username.set(new_name)
    update_btn = ctk.CTkButton(
        settings_window, text="Update Username",
        width=280, height=45, corner_radius=20,
        font=("Segoe UI", 14, "bold"),
        fg_color=current_theme["button"],
        hover_color=current_theme["hover"],
        command=update_username
    )
    update_btn.pack(pady=15)
    settings_buttons.append(update_btn)
    label_photo = ctk.CTkLabel(settings_window, text="Change Profile Photo",
                               font=("Segoe UI", 16),
                               text_color=current_theme["text"])
    label_photo.pack(pady=(25, 8))
    settings_labels.append(label_photo)
    def choose_photo():
        global current_profile_path
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            current_profile_path = file_path
            img = Image.open(file_path).resize((80, 80))
            img_ctk = ctk.CTkImage(img, size=(80, 80))
            profile_image_label.configure(image=img_ctk)
            profile_image_label.image = img_ctk
    photo_btn = ctk.CTkButton(
        settings_window, text="Choose Photo",
        width=280, height=45, corner_radius=20,
        font=("Segoe UI", 14, "bold"),
        fg_color=current_theme["button"],
        hover_color=current_theme["hover"],
        command=choose_photo
    )
    photo_btn.pack(pady=15)
    settings_buttons.append(photo_btn)
create_button("Start Detection",     start_detection,  0.15, 0.30)
create_button("Learn ISL",           learn_isl,        0.35, 0.30)
create_button("Practice / Quizzes",  practice_quiz,    0.55, 0.30)
create_button("Vocabulary",          storytelling,     0.75, 0.30)
create_button("Text / Speech to ISL", text_to_isl,    0.15, 0.70)
create_button("Progress / Profile",  progress_profile, 0.35, 0.70)
create_button("Settings",            settings,         0.55, 0.70)
ctk.CTkButton(
    button_frame, text="Exit / Logout",
    command=app.destroy,
    fg_color="#B22222", hover_color="#D12A2A",
    width=160, height=45, corner_radius=18,
    font=("Segoe UI", 14, "bold")
).place(relx=0.75, rely=0.70, anchor="center")
def on_closing():
    stop_webcam()
    app.after(200, app.destroy)
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()