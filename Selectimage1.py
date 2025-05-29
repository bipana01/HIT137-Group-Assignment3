import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2

class Imageapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Loader")
        self.root.geometry("800x600")

        self.image = None
        self.displayed_image = None

        # Button to load the image
        self.load_button = ttk.Button(self.root, text="Select and Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        # Canvas to display the image
        self.canvas = tk.Canvas(self.root, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            # Load the image and convert the image
            self.image = cv2.imread(file_path)
            if self.image is not None:
                self.display_image(self.image)

    def display_image(self, image):
        # Convert BGR (OpenCV) to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        # Resize the image to fit in canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        pil_image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)

        self.displayed_image = ImageTk.PhotoImage(pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()


# Reference https://www.youtube.com/watch?v=Aim_7fC-inw