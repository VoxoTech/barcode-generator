import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import barcode
from barcode.writer import ImageWriter
import io

# Conversion mm -> pixels à 300 dpi
def mm_to_px(mm, dpi=300):
    return int(mm / 25.4 * dpi)

IMG_WIDTH = mm_to_px(65)
IMG_HEIGHT = mm_to_px(20)
DPI = 300

def generate_barcode_image(username, password, first_name):
    """Génère une image PIL du code-barres avec prénom sous le code."""
    data = f"\t\t{username}\t{password}\n"

    CODE128 = barcode.get_barcode_class('code128')
    code = CODE128(data, writer=ImageWriter())

    buffer = io.BytesIO()
    code.write(buffer, {
        'module_width': 0.25,
        'module_height': 12,
        'quiet_zone': 2,
        'font_size': 0,
        'dpi': DPI
    })
    buffer.seek(0)

    barcode_img = Image.open(buffer).convert("RGB")

    # Créer image finale blanche
    final_img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "white")
    draw = ImageDraw.Draw(final_img)

    barcode_h = int(IMG_HEIGHT * 0.8)
    resized_barcode = barcode_img.resize((IMG_WIDTH, barcode_h))
    final_img.paste(resized_barcode, (0, 0))

    # Dessiner prénom centré
    try:
        font = ImageFont.truetype("Arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # ✅ Compatible Pillow ≥10
    try:
        bbox = draw.textbbox((0, 0), first_name, font=font)
        text_w = bbox[2] - bbox[0]
        text_h_real = bbox[3] - bbox[1]
    except AttributeError:
        # Ancienne méthode Pillow <10
        text_w, text_h_real = draw.textsize(first_name, font=font)

    text_y = barcode_h + (IMG_HEIGHT - barcode_h - text_h_real) // 2
    draw.text(((IMG_WIDTH - text_w)//2, text_y), first_name, fill="black", font=font)

    return final_img

class BarcodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de code-barres (Code128)")
        self.geometry("500x500")
        self.resizable(False, False)

        tk.Label(self, text="Prénom :").pack(anchor="w", padx=10, pady=(10,0))
        self.entry_first = tk.Entry(self, width=50)
        self.entry_first.pack(padx=10, pady=5)

        tk.Label(self, text="Nom d'utilisateur :").pack(anchor="w", padx=10)
        self.entry_user = tk.Entry(self, width=50)
        self.entry_user.pack(padx=10, pady=5)

        tk.Label(self, text="Mot de passe :").pack(anchor="w", padx=10)
        self.entry_pass = tk.Entry(self, show="*", width=50)
        self.entry_pass.pack(padx=10, pady=5)

        frame_btn = tk.Frame(self)
        frame_btn.pack(pady=10)
        tk.Button(frame_btn, text="Aperçu", command=self.preview).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Enregistrer PNG", command=self.save).pack(side="left", padx=5)

        self.preview_label = tk.Label(self, text="(Aucun aperçu pour l’instant)")
        self.preview_label.pack(pady=10)

        self.tk_preview_image = None

    def preview(self):
        first = self.entry_first.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not (first and user and pwd):
            messagebox.showwarning("Champs vides", "Tous les champs doivent être remplis.")
            return

        try:
            img = generate_barcode_image(user, pwd, first)
            preview_w = 400
            ratio = preview_w / IMG_WIDTH
            preview_h = int(IMG_HEIGHT * ratio)
            img_preview = img.resize((preview_w, preview_h))

            self.tk_preview_image = ImageTk.PhotoImage(img_preview)
            self.preview_label.configure(image=self.tk_preview_image, text="")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer l'aperçu : {e}")

    def save(self):
        first = self.entry_first.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not (first and user and pwd):
            messagebox.showwarning("Champs vides", "Tous les champs doivent être remplis.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Enregistrer sous",
            defaultextension=".png",
            filetypes=[("Image PNG", "*.png")]
        )
        if not output_path:
            return

        try:
            img = generate_barcode_image(user, pwd, first)
            img.save(output_path, dpi=(DPI, DPI))
            messagebox.showinfo("Succès", f"Code-barres enregistré :\n{output_path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
    app = BarcodeApp()
    app.mainloop()
