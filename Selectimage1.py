# Desktop Application to demonstrate understanding of OOP principles, 
# GUI development using Tkinter &
# Image Processing using OpenCV

# Group  [CAS/DAN 05]
# Bipana Tripathee : [SID: s388875]
# Elijah Balanon Cantoria : [SID: s358778 ]
# Sakshi Sakshi :  [SID: s386993]
# Shreeya Regmi  :  [SID: s390356]



import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk

class Imageapp:
    def __init__(self, root):
        self.root = root
        # Title of image
        self.root.title("Image Processor")
        # size of canvas
        self.root.geometry("1200x700")

        # Initialize application state
        self.original_image = None
        self.current_cropped_image = None
        self.displayed_image = None
        self.scaling_factor_x = 1.0
        self.scaling_factor_y = 1.0
        self.undo_stack = []
        self.redo_stack = []
        self.rect = None
        self.crop_coords = None
        self.resize_scale = 100  
        self.is_resizing = False
        self.min_scale = 20  
        self.max_scale = 150  
        self.reference_scale = 100  

        self.create_toolbar()
        self.create_canvases()
        self.create_slider()
        self.bind_events()

    def create_toolbar(self):
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Upload Button
        self.upload_btn = ttk.Button(self.toolbar, text="Upload", command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Save Button
        self.save_btn = ttk.Button(self.toolbar, text="Save", command=self.save_image, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = ttk.Button(self.toolbar, text="Undo", command=self.undo, state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT, padx=5)
        
        # Redo Button
        self.redo_btn = ttk.Button(self.toolbar, text="Redo", command=self.redo, state=tk.DISABLED)
        self.redo_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset Button
        self.reset_btn = ttk.Button(self.toolbar, text="Reset", command=self.reset_application)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.config(state=tk.DISABLED)

        # Flip Horizontal Button
        self.flip_h_btn = ttk.Button(self.toolbar, text="Flip H", command=self.flip_horizontal)
        self.flip_h_btn.pack(side=tk.LEFT, padx=5)
        
        # Flip Vertical Button
        self.flip_v_btn = ttk.Button(self.toolbar, text="Flip V", command=self.flip_vertical)
        self.flip_v_btn.pack(side=tk.LEFT, padx=5)
        
        # Rotate Left Button
        self.rotate_left_btn = ttk.Button(self.toolbar, text="Rotate ⟲", command=self.rotate_left)
        self.rotate_left_btn.pack(side=tk.LEFT, padx=5)
        
        # Rotate Rignt Button
        self.rotate_right_btn = ttk.Button(self.toolbar, text="Rotate ⟳", command=self.rotate_right)
        self.rotate_right_btn.pack(side=tk.LEFT, padx=5)
        
        # Image Slider for resizing
    def create_slider(self):
        self.slider_frame = ttk.Frame(self.root)
        self.slider_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.scale_label = ttk.Label(self.slider_frame, text="Resize Scale (%):")
        self.scale_label.pack(side=tk.LEFT, padx=5)

        self.scale_slider = ttk.Scale(self.slider_frame, from_=self.min_scale, to=self.max_scale, command=self.on_slider_change)
        self.scale_slider.set(self.reference_scale)
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.scale_value = ttk.Label(self.slider_frame, text="100%")
        self.scale_value.pack(side=tk.LEFT, padx=5)
        self.scale_slider.config(state=tk.DISABLED)
        
        # Create The Canvas
    def create_canvases(self):
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window, width=600)
        self.left_canvas = tk.Canvas(self.left_frame, bg='gray')
        self.left_scroll_x = ttk.Scrollbar(self.left_frame, orient="horizontal", command=self.left_canvas.xview)
        self.left_scroll_y = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_canvas.configure(xscrollcommand=self.left_scroll_x.set, yscrollcommand=self.left_scroll_y.set)
        
        self.left_scroll_x.pack(side="bottom", fill="x")
        self.left_scroll_y.pack(side="right", fill="y")
        self.left_canvas.pack(side="left", fill="both", expand=True)
        self.paned_window.add(self.left_frame, width=600)

        self.right_frame = ttk.Frame(self.paned_window, width=600)
        self.right_canvas = tk.Canvas(self.right_frame, bg='gray')
        self.right_scroll_x = ttk.Scrollbar(self.right_frame, orient="horizontal", command=self.right_canvas.xview)
        self.right_scroll_y = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.right_canvas.yview)
        self.right_canvas.configure(xscrollcommand=self.right_scroll_x.set, yscrollcommand=self.right_scroll_y.set)
        
        self.right_scroll_x.pack(side="bottom", fill="x")
        self.right_scroll_y.pack(side="right", fill="y")
        self.right_canvas.pack(side="left", fill="both", expand=True)
        self.paned_window.add(self.right_frame, width=600)

    def bind_events(self):
        self.left_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.left_canvas.bind("<B1-Motion>", self.update_crop)
        self.left_canvas.bind("<ButtonRelease-1>", self.end_crop)

        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.root.bind_all("<Control-o>", lambda e: self.upload_image())
        self.root.bind_all("<Control-s>", lambda e: self.save_image())
        self.root.bind_all("<Control-z>", lambda e: self.undo())
        self.root.bind_all("<Control-y>", lambda e: self.redo())
        self.root.bind_all("<Control-r>", lambda e: self.reset_application())
        self.root.bind_all("<h>", lambda e: self.flip_horizontal())
        self.root.bind_all("<v>", lambda e: self.flip_vertical())
        self.root.bind_all("<l>", lambda e: self.rotate_left())
        self.root.bind_all("<r>", lambda e: self.rotate_right())
        
        # Upload the image
    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.reset_state()
                self.display_image_left()
                self.scale_slider.config(state=tk.NORMAL)
                self.update_button_states()
                
    # Display The image            
    def display_image_left(self):
        rgb_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        canvas_width = self.left_canvas.winfo_width()
        canvas_height = self.left_canvas.winfo_height()
        img_width, img_height = pil_image.size

        scale = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width*scale), int(img_height*scale))

        resized_image = pil_image.resize(new_size, Image.LANCZOS)
        self.displayed_image = ImageTk.PhotoImage(resized_image)

        self.scaling_factor_x = img_width / new_size[0]
        self.scaling_factor_y = img_height / new_size[1]

        self.left_canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

    def start_crop(self, event):
        if self.rect:
            self.left_canvas.delete(self.rect)

        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.left_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def update_crop(self, event):
        current_x = event.x
        current_y = event.y
        self.left_canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)
        self.update_preview(current_x, current_y)

    def update_preview(self, current_x, current_y):
        x1 = int(min(self.start_x, current_x) * self.scaling_factor_x)
        y1 = int(min(self.start_y, current_y) * self.scaling_factor_y)
        x2 = int(max(self.start_x, current_x) * self.scaling_factor_x)
        y2 = int(max(self.start_y, current_y) * self.scaling_factor_y)

        if x2 <= x1 or y2 <= y1:
            return

        self.current_cropped_image = self.original_image[y1:y2, x1:x2]
        self.display_cropped_image(self.current_cropped_image)

    def end_crop(self, event):
        current_x = event.x
        current_y = event.y
        self.update_preview(current_x, current_y)
        self.crop_coords = (
            int(min(self.start_x, current_x) * self.scaling_factor_x),
            int(min(self.start_y, current_y) * self.scaling_factor_y),
            int(max(self.start_x, current_x) * self.scaling_factor_x),
            int(max(self.start_y, current_y) * self.scaling_factor_y)
        )

        if self.current_cropped_image is not None and self.current_cropped_image.size > 0:
            self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.redo_stack.clear()
            self.update_button_states()

    def on_slider_change(self, event=None):
        if self.current_cropped_image is None:
            return
        self.resize_scale = int(float(self.scale_slider.get()))
        self.scale_value.config(text=f"{self.resize_scale}%")
        self.display_cropped_image(self.current_cropped_image)

    def display_cropped_image(self, image):
        if image is None or image.size == 0:
            return
        try:
            self.right_canvas.delete("all")
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)

            new_width = max(1, int(pil_image.width * self.resize_scale / 100))
            new_height = max(1, int(pil_image.height * self.resize_scale / 100))
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

            display_image = ImageTk.PhotoImage(resized_image)
            self.right_image = display_image
            self.right_canvas.create_image(0, 0, anchor=tk.NW, image=self.right_image)
        except Exception as e:
            print(f"Error displaying image: {e}")

    def reset_application(self):
        self.reset_state()
        self.scale_slider.config(state=tk.DISABLED)
        self.update_button_states()

    def reset_state(self):
        self.current_cropped_image = None
        self.crop_coords = None
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.resize_scale = 100
        self.scale_slider.set(100)
        self.scale_value.config(text="100%")
        self.left_canvas.delete("all")
        self.right_canvas.delete("all")
        self.rect = None

    def save_image(self):
        if self.current_cropped_image is None or self.current_cropped_image.size == 0:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            scale_factor = self.resize_scale / 100
            new_width = int(self.current_cropped_image.shape[1] * scale_factor)
            new_height = int(self.current_cropped_image.shape[0] * scale_factor)
            resized = cv2.resize(self.current_cropped_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            cv2.imwrite(file_path, resized)
            
    # Undo the changes
    def undo(self):
        if self.undo_stack:
            if self.current_cropped_image is not None:
                self.redo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.current_cropped_image, self.resize_scale = self.undo_stack.pop()
            self.scale_slider.set(self.resize_scale)
            self.scale_value.config(text=f"{self.resize_scale}%")
            self.display_cropped_image(self.current_cropped_image)
            self.update_button_states()
    
    # Redo Changes 
    def redo(self):
        if self.redo_stack:
            if self.current_cropped_image is not None:
                self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.current_cropped_image, self.resize_scale = self.redo_stack.pop()
            self.scale_slider.set(self.resize_scale)
            self.scale_value.config(text=f"{self.resize_scale}%")
            self.display_cropped_image(self.current_cropped_image)
            self.update_button_states()

    def update_button_states(self):
        has_crop = self.current_cropped_image is not None and self.current_cropped_image.size > 0
        self.save_btn.config(state=tk.NORMAL if has_crop else tk.DISABLED)
        self.undo_btn.config(state=tk.NORMAL if self.undo_stack else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if self.redo_stack else tk.DISABLED)
        self.reset_btn.config(state=tk.NORMAL if self.original_image is not None else tk.DISABLED)
        
    # Flip the cropped Image Horizontally
    def flip_horizontal(self):
        if self.current_cropped_image is not None:
            self.current_cropped_image = cv2.flip(self.current_cropped_image, 1)
            self.display_cropped_image(self.current_cropped_image)
            self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.redo_stack.clear()
            self.update_button_states()
            
    # Flip the cropped Image Vertically        
    def flip_vertical(self):
        if self.current_cropped_image is not None:
            self.current_cropped_image = cv2.flip(self.current_cropped_image, 0)
            self.display_cropped_image(self.current_cropped_image)
            self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.redo_stack.clear()
            self.update_button_states()
            
    # Rotate The cropped image to the Left        
    def rotate_left(self):
        if self.current_cropped_image is not None:
            self.current_cropped_image = cv2.rotate(self.current_cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.display_cropped_image(self.current_cropped_image)
            self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.redo_stack.clear()
            self.update_button_states()
            
    # Rotate the cropped image to the Right        
    def rotate_right(self):
        if self.current_cropped_image is not None:
            self.current_cropped_image = cv2.rotate(self.current_cropped_image, cv2.ROTATE_90_CLOCKWISE)
            self.display_cropped_image(self.current_cropped_image)
            self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            self.redo_stack.clear()
            self.update_button_states()

if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()
