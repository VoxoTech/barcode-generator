import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

# --- Constantes ---
DPI = 300
MM_TO_PX = DPI / 25.4
WIDTH_MM = 65
HEIGHT_MM = 20

# Fonction utilitaire pour trouver le chemin de la police même dans le .exe/.app
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
    code128 = barcode.get('code128', data, writer=ImageWriter())
    barcode_path = output_path.replace(".png", "_barcode.png")
    code128.save(barcode_path)

    barcode_img = Image.open(barcode_path).convert("RGB")

    # Ajustement de la taille à 65x20 mm (300 dpi)
    img_width = int(WIDTH_MM * MM_TO_PX)
    img_height = int(HEIGHT_MM * MM_TO_PX)
    barcode_img = barcode_img.resize((img_width, img_height), Image.LANCZOS)

    # Crée une nouvelle image avec un espace pour le prénom en dessous
    total_height = img_height + int(8 * MM_TO_PX)
    final_img = Image.new("RGB", (img_width, total_height), "white")
    final_img.paste(barcode_img, (0, 0))

    draw = ImageDraw.Draw(final_img)

    # Police TrueType (10 mm de haut environ)
    try:
        font = ImageFont.truetype(FONT_PATH, size=int(10 * MM_TO_PX))
    except OSError:
        font = ImageFont.load_default()

    # Centrage du texte
    text_bbox = draw.textbbox((0, 0), prenom, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (img_width - text_width) // 2
    text_y = img_height + int(2 * MM_TO_PX)
    draw.text((text_x, text_y), prenom, fill="black", font=font)

    # Sauvegarde finale
    final_img.save(output_path, dpi=(DPI, DPI))
    os.remove(barcode_path)

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
        generate_barcode(username, password, prenom, output_path)
        messagebox.showinfo("Succès", f"Code-barres généré :\n{output_path}")
        show_preview(output_path)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def show_preview(image_path):
    preview = tk.Toplevel(root)
    preview.title("Aperçu du code-barres")
    img = tk.PhotoImage(file=image_path)
    label = tk.Label(preview, image=img)
    label.image = img
    label.pack(padx=10, pady=10)

# --- Fenêtre principale ---
root = tk.Tk()
root.title("Générateur de codes-barres 128")

tk.Label(root, text="Nom d’utilisateur :").grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(root, width=30)
entry_username.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Mot de passe :").grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(root, width=30)
entry_password.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Prénom (affiché sous le code-barres) :").grid(row=2, column=0, padx=5, pady=5)
entry_prenom = tk.Entry(root, width=30)
entry_prenom.grid(row=2, column=1, padx=5, pady=5)

btn_generate = tk.Button(root, text="Générer et Prévisualiser", command=generate_and_preview)
btn_generate.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
