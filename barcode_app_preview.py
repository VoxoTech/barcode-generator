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

# --- Génération du code-barres ---
def generate_barcode(username, password, prenom, output_path):
    data = f"\t\t{username}\t{password}\n"
    code128 = barcode.get("code128", data, writer=ImageWriter())
    temp_path = output_path.replace(".png", "_temp.png")
    code128.save(temp_path)

    barcode_img = Image.open(temp_path).convert("RGB")

    # Ajustement de la taille à 65x20 mm (300 dpi)
    img_width = int(WIDTH_MM * MM_TO_PX)
    img_height = int(HEIGHT_MM * MM_TO_PX)
    barcode_img = barcode_img.resize((img_width, img_height), Image.LANCZOS)

    # Nouvelle image avec un espace sous le code-barres pour le prénom
    total_height = img_height + int(8 * MM_TO_PX)
    final_img = Image.new("RGB", (img_width, total_height), "white")
    final_img.paste(barcode_img, (0, 0))
    draw = ImageDraw.Draw(final_img)

    # Police lisible
    try:
        font = ImageFont.truetype(FONT_PATH, size=int(10 * MM_TO_PX))
    except OSError:
        font = ImageFont.load_default()

    # Centrage du prénom
    text_bbox = draw.textbbox((0, 0), prenom, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (img_width - text_width) // 2
    text_y = img_height + int(2 * MM_TO_PX)
    draw.text((text_x, text_y), prenom, fill="black", font=font)

    final_img.save(output_path, dpi=(DPI, DPI))
    os.remove(temp_path)

    return final_img

# --- Interface graphique ---
def generate_and_preview():
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
        pil_image = generate_barcode(username, password, prenom, output_path)
        show_preview(pil_image)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def show_preview(pil_image):
    # Création de l’image adaptée à la fenêtre (mise à l’échelle)
    preview_width = 600
    ratio = preview_width / pil_image.width
    preview_height = int(pil_image.height * ratio)
    img_resized = pil_image.resize((preview_width, preview_height), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_resized)

    preview_label.config(image=img_tk)
    preview_label.image = img_tk

# --- Fenêtre principale ---
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

btn_generate = tk.Button(root, text="Générer et Prévisualiser", command=generate_and_preview)
btn_generate.grid(row=3, column=0, columnspan=2, pady=10)

preview_label = tk.Label(root)
preview_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
