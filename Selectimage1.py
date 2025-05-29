import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
from PIL import Image, ImageTk


class Imageapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("800x600")

        self.image_path = None
        self.cv_image = None
        self.tk_image = None

        self.setup_ui()

    def setup_ui(self):
        # Button to load image
        load_button = ttk.Button(self.root, text="Load Image", command=self.load_image)
        load_button.pack(pady=10)

        # Label to display image
        self.image_label = ttk.Label(self.root)
        self.image_label.pack()

    def load_image(self):
        # Open file dialog
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
        if not file_path:
            return

        self.image_path = file_path

        # Load with OpenCV
        self.cv_image = cv2.imread(file_path)

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)

        # Convert to PIL and then ImageTk format
        pil_image = Image.fromarray(image_rgb)
        self.tk_image = ImageTk.PhotoImage(pil_image)

        # Show in label
        self.image_label.config(image=self.tk_image)
        self.image_label.image = self.tk_image


if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()

# Reference https://www.youtube.com/watch?v=Aim_7fC-inw
