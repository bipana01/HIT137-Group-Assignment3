import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2

class Imageapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        self.root.geometry("800x600")

        self.cv_image = None
        self.tk_image = None
        self.displayed_image = None

        self.start_x = self.start_y = None
        self.rect = None
        self.rect_coords = None

        self.load_button = ttk.Button(self.root, text="Select and Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.canvas = tk.Canvas(self.root, bg='gray', cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        self.root.update()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.cv_image = cv2.imread(file_path)
            if self.cv_image is not None:
                self.display_image(self.cv_image)

    def display_image(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        pil_image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)

        self.tk_image = pil_image
        self.displayed_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

    def on_mouse_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2
        )

    def on_mouse_release(self, event):
        end_x, end_y = event.x, event.y
        self.rect_coords = (self.start_x, self.start_y, end_x, end_y)
        print(f"Selected rectangle: {self.rect_coords}")  # Optional debug print

if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()


# Reference https://www.youtube.com/watch?v=Aim_7fC-inw
