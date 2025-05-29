import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2

class Imageapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        self.root.geometry("1200x600")

        self.cv_image = None
        self.tk_image = None
        self.displayed_image = None
        self.cropped_image = None

        self.start_x = self.start_y = None
        self.rect = None
        self.rect_coords = None

        self.load_button = ttk.Button(self.root, text="Select and Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg='gray', cursor="cross", width=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cropped_canvas = tk.Canvas(self.canvas_frame, bg='lightgray', width=600)
        self.cropped_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
        self.original_pil_image = Image.fromarray(rgb_image)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.scaled_pil_image = self.original_pil_image.copy()
        self.scaled_pil_image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)

        self.tk_image = self.scaled_pil_image
        self.displayed_image = ImageTk.PhotoImage(self.tk_image)

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
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2, dash=(4, 2)
        )

    def on_mouse_release(self, event):
        end_x, end_y = event.x, event.y
        self.rect_coords = (self.start_x, self.start_y, end_x, end_y)

        # Crop based on scaled image and map to original
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        if x2 - x1 > 1 and y2 - y1 > 1:
            scale_x = self.original_pil_image.width / self.tk_image.width
            scale_y = self.original_pil_image.height / self.tk_image.height

            orig_x1 = int(x1 * scale_x)
            orig_y1 = int(y1 * scale_y)
            orig_x2 = int(x2 * scale_x)
            orig_y2 = int(y2 * scale_y)

            cropped = self.original_pil_image.crop((orig_x1, orig_y1, orig_x2, orig_y2))
            self.display_cropped_image(cropped)

    def display_cropped_image(self, cropped_pil_image):
        cropped_pil_image.thumbnail((self.cropped_canvas.winfo_width(), self.cropped_canvas.winfo_height()))
        self.cropped_image = ImageTk.PhotoImage(cropped_pil_image)

        self.cropped_canvas.delete("all")
        self.cropped_canvas.create_image(0, 0, anchor=tk.NW, image=self.cropped_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()


