import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import barcode
from barcode.writer import ImageWriter

# --- Constantes ---
DPI = 300
MM_TO_PX = DPI / 25.4
WIDTH_MM = 65
HEIGHT_MM = 20

def resource_path(relative_path):
    """Trouve le chemin du fichier, même dans le binaire PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

FONT_PATH = resource_path("DejaVuSans.ttf")

# --- Génération du code-barres (retourne image PIL) ---
def generate_barcode_image(username, password, prenom):
    data = f"\t\t{username}\t{password}\n"
    code128 = barcode.get("code128", data, writer=ImageWriter())
    temp_path = "temp_barcode.png"
    code128.save(temp_path)

    barcode_img = Image.open(temp_path).convert("RGB")
    os.remove(temp_path)

    img_width = int(WIDTH_MM * MM_TO_PX)
    img_height = int(HEIGHT_MM * MM_TO_PX)
    barcode_img = barcode_img.resize((img_width, img_height), Image.LANCZOS)

    total_height = img_height + int(8 * MM_TO_PX)
    final_img = Image.new("RGB", (img_width, total_height), "white")
    final_img.paste(barcode_img, (0, 0))
    draw = ImageDraw.Draw(final_img)

    try:
        font = ImageFont.truetype(FONT_PATH, size=int(10 * MM_TO_PX))
    except OSError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), prenom, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (img_width - text_width) // 2
    text_y = img_height + int(2 * MM_TO_PX)
    draw.text((text_x, text_y), prenom, fill="black", font=font)

    return final_img

# --- Actions interface ---
def preview_barcode():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    prenom = entry_prenom.get().strip()

    if not username or not password or not prenom:
        messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
        return

    try:
        pil_image = generate_barcode_image(username, password, prenom)
        show_preview(pil_image)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def save_barcode():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    prenom = entry_prenom.get().strip()

    if not username or not password or not prenom:
        messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
        return

    output_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Image PNG", "*.png")],
        title="Enregistrer le code-barres"
    )
    if not output_path:
        return

    try:
        pil_image = generate_barcode_image(username, password, prenom)
        pil_image.save(output_path, dpi=(DPI, DPI))
        messagebox.showinfo("Succès", f"Fichier enregistré :\n{output_path}")
        show_preview(pil_image)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def show_preview(pil_image):
    preview_width = 600
    ratio = preview_width / pil_image.width
    preview_height = int(pil_image.height * ratio)
    img_resized = pil_image.resize((preview_width, preview_height), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_resized)
    preview_label.config(image=img_tk)
    preview_label.image = img_tk

# --- Interface principale ---
root = tk.Tk()
root.title("Générateur de codes-barres 128")

tk.Label(root, text="Nom d’utilisateur :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_username = tk.Entry(root, width=30)
entry_username.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Mot de passe :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_password = tk.Entry(root, width=30)
entry_password.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Prénom (affiché sous le code-barres) :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_prenom = tk.Entry(root, width=30)
entry_prenom.grid(row=2, column=1, padx=5, pady=5)

# Deux boutons côte à côte
frame_buttons = tk.Frame(root)
frame_buttons.grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(frame_buttons, text="Aperçu", width=15, command=preview_barcode).pack(side="left", padx=5)
tk.Button(frame_buttons, text="Enregistrer", width=15, command=save_barcode).pack(side="left", padx=5)

# Label d’aperçu
preview_label = tk.Label(root)
preview_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
