import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk

class Imageapp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
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
        # Percentage scale (100% = original size)
        self.resize_scale = 100  
        self.is_resizing = False
        # Minimum scale percentage
        self.min_scale = 20  
        # Maximum scale percentage
        self.max_scale = 150  
        # Reference scale (100%)
        self.reference_scale = 100  

        # Initialize GUI components
        self.create_toolbar()
        self.create_canvases()
        self.create_slider()
        self.bind_events()

    def create_toolbar(self):
        """Create the toolbar with control buttons"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.upload_btn = ttk.Button(self.toolbar, text="Upload", command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(self.toolbar, text="Save", 
                                 command=self.save_image, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = ttk.Button(self.toolbar, text="Undo", 
                                  command=self.undo, state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        self.redo_btn = ttk.Button(self.toolbar, text="Redo", 
                                  command=self.redo, state=tk.DISABLED)
        self.redo_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(self.toolbar, text="Reset", 
                              command=self.reset_application)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.config(state=tk.DISABLED)
    
    def reset_application(self):
        """Reset the entire application to initial state"""
        self.reset_state()
        self.scale_slider.config(state=tk.DISABLED)
        self.update_button_states()

    def create_slider(self):
        """Create the resize slider with 20%-150% range"""
        self.slider_frame = ttk.Frame(self.root)
        self.slider_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.scale_label = ttk.Label(self.slider_frame, text="Resize Scale (%):")
        self.scale_label.pack(side=tk.LEFT, padx=5)

        self.scale_slider = ttk.Scale(self.slider_frame, from_=self.min_scale, to=self.max_scale, 
                                    command=self.on_slider_change)
        self.scale_slider.set(self.reference_scale)
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.scale_value = ttk.Label(self.slider_frame, text="100%")
        self.scale_value.pack(side=tk.LEFT, padx=5)
        self.scale_slider.config(state=tk.DISABLED)

    def create_canvases(self):
        """Create canvas areas with scrollbars for large images"""
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left canvas with scrollbars
        self.left_frame = ttk.Frame(self.paned_window, width=600)
        self.left_canvas = tk.Canvas(self.left_frame, bg='gray')
        self.left_scroll_x = ttk.Scrollbar(self.left_frame, orient="horizontal", command=self.left_canvas.xview)
        self.left_scroll_y = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_canvas.configure(xscrollcommand=self.left_scroll_x.set, yscrollcommand=self.left_scroll_y.set)
        
        self.left_scroll_x.pack(side="bottom", fill="x")
        self.left_scroll_y.pack(side="right", fill="y")
        self.left_canvas.pack(side="left", fill="both", expand=True)
        self.paned_window.add(self.left_frame, width=600)

        # Right canvas with scrollbars
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
        """Bind mouse events for cropping"""
        self.left_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.left_canvas.bind("<B1-Motion>", self.update_crop)
        self.left_canvas.bind("<ButtonRelease-1>", self.end_crop)

    def on_slider_change(self, event=None):
        """Handle slider value changes with proper scaling"""
        if self.original_image is None or self.current_cropped_image is None:
            return

        self.resize_scale = int(float(self.scale_slider.get()))
        self.scale_value.config(text=f"{self.resize_scale}%")
        
        # Calculate display size based on scale
        self.display_scaled_image()

    def display_scaled_image(self):
        """Display image with proper aspect ratio in right panel"""
        self.right_canvas.delete("all")
        
        if self.current_cropped_image is None:
            return

        try:
            # Get original image dimensions
            original_height, original_width = self.current_cropped_image.shape[:2]
            aspect_ratio = original_width / original_height
            
            # Calculate available canvas space
            canvas_width = self.right_canvas.winfo_width()
            canvas_height = self.right_canvas.winfo_height()
            
            # Calculate display dimensions based on scale (100% = half width)
            base_width = canvas_width // 2
            scaled_width = int(base_width * (self.resize_scale / 100))
            scaled_height = int(scaled_width / aspect_ratio)
            
            # Adjust if scaled height exceeds canvas
            if scaled_height > canvas_height:
                scaled_height = canvas_height
                scaled_width = int(scaled_height * aspect_ratio)
            
            # Resize the image while maintaining aspect ratio
            resized = cv2.resize(self.current_cropped_image, 
                            (scaled_width, scaled_height),
                            interpolation=cv2.INTER_AREA)
            
            # Convert to PhotoImage
            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            self.right_image = ImageTk.PhotoImage(pil_image)
            
            # Center the image in the canvas
            x_pos = (canvas_width - scaled_width) // 2
            y_pos = (canvas_height - scaled_height) // 2
            self.right_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.right_image)
            
        except Exception as e:
            print(f"Error displaying scaled image: {e}")


    def upload_image(self):
        """Handle image upload"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.reset_state()
                self.display_image_left()
                self.scale_slider.config(state=tk.NORMAL)
                self.update_button_states()

    def reset_state(self):
        """Reset application state for new image"""
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

    def display_image_left(self):
        """Display the uploaded image on left canvas"""
        rgb_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Calculate scaling to fit canvas
        canvas_width = self.left_canvas.winfo_width()
        canvas_height = self.left_canvas.winfo_height()
        img_width, img_height = pil_image.size
        
        scale = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width*scale), int(img_height*scale))
        
        resized_image = pil_image.resize(new_size, Image.LANCZOS)
        self.displayed_image = ImageTk.PhotoImage(resized_image)
        
        # Store scaling factors
        self.scaling_factor_x = img_width / new_size[0]
        self.scaling_factor_y = img_height / new_size[1]
        
        self.left_canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)

    def start_crop(self, event):
        """Start cropping operation"""
        if self.rect:
            self.left_canvas.delete(self.rect)
        
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.left_canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='red', width=2)

    def update_crop(self, event):
        """Update cropping rectangle and preview"""
        current_x = event.x
        current_y = event.y
        
        if not self.rect:
            self.rect = self.left_canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y, 
                outline='red', width=2)
        else:
            self.left_canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)
        
        self.update_preview(current_x, current_y)

    def update_preview(self, current_x, current_y):
        """Update the right canvas with current crop preview"""
        x1 = int(min(self.start_x, current_x) * self.scaling_factor_x)
        y1 = int(min(self.start_y, current_y) * self.scaling_factor_y)
        x2 = int(max(self.start_x, current_x) * self.scaling_factor_x)
        y2 = int(max(self.start_y, current_y) * self.scaling_factor_y)

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(self.original_image.shape[1], x2)
        y2 = min(self.original_image.shape[0], y2)

        if x2 <= x1 or y2 <= y1:
            return

        self.current_cropped_image = self.original_image[y1:y2, x1:x2]
        self.display_cropped_image(self.current_cropped_image)

    def display_cropped_image(self, image):
        """Display the given image on the right canvas with resizing"""
        self.right_canvas.delete("all")
        
        # Check for empty image
        if image is None or image.size == 0:
            return
            
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Apply resize scale to the actual image
            new_width = int(pil_image.width * self.resize_scale / 100)
            new_height = int(pil_image.height * self.resize_scale / 100)
            
            # Ensure minimum size of 1 pixel
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            
            # Scale to fit canvas while maintaining aspect ratio
            canvas_width = self.right_canvas.winfo_width()
            canvas_height = self.right_canvas.winfo_height()
            
            # Avoid division by zero
            if new_width == 0 or new_height == 0:
                return
                
            scale = min(canvas_width/new_width, canvas_height/new_height)
            display_size = (int(new_width*scale), int(new_height*scale))
            
            display_image = resized_image.resize(display_size, Image.LANCZOS)
            self.right_image = ImageTk.PhotoImage(display_image)
            self.right_canvas.create_image(0, 0, anchor=tk.NW, image=self.right_image)
        except Exception as e:
            print(f"Error displaying image: {e}")

    def end_crop(self, event):
        """Finalize cropping operation"""
        if self.rect:
            current_x = event.x
            current_y = event.y
            self.update_preview(current_x, current_y)
            
            # Store crop coordinates
            self.crop_coords = (
                int(min(self.start_x, current_x) * self.scaling_factor_x),
                int(min(self.start_y, current_y) * self.scaling_factor_y),
                int(max(self.start_x, current_x) * self.scaling_factor_x),
                int(max(self.start_y, current_y) * self.scaling_factor_y)
            )
            
            # Enable slider now that we have a crop
            self.scale_slider.config(state=tk.NORMAL)
            
            # Add to undo stack
            if (self.current_cropped_image is not None and 
                hasattr(self.current_cropped_image, 'size') and 
                self.current_cropped_image.size > 0):
                self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
                self.redo_stack.clear()
                self.update_button_states()

    def save_image(self):
        """Save the image with actual pixel dimensions based on scale"""
        if (self.current_cropped_image is None or 
            not hasattr(self.current_cropped_image, 'size') or 
            self.current_cropped_image.size == 0):
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Calculate actual output dimensions
                original_height, original_width = self.current_cropped_image.shape[:2]
                scale_factor = self.resize_scale / 100
                output_width = int(original_width * scale_factor)
                output_height = int(original_height * scale_factor)
                
                # Resize using high-quality interpolation
                resized = cv2.resize(self.current_cropped_image,
                                (output_width, output_height),
                                interpolation=cv2.INTER_LANCZOS4)
                
                # Save based on file type
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    cv2.imwrite(file_path, resized, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                else:
                    cv2.imwrite(file_path, resized)
            except Exception as e:
                print(f"Error saving image: {e}")

    def undo(self):
        """Undo last operation"""
        if self.undo_stack:
            # Save current state to redo stack
            if self.current_cropped_image is not None:
                self.redo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            
            # Restore previous state
            prev_image, prev_scale = self.undo_stack.pop()
            self.current_cropped_image = prev_image
            self.resize_scale = prev_scale
            self.scale_slider.set(prev_scale)
            self.scale_value.config(text=f"{prev_scale}%")
            self.display_cropped_image(self.current_cropped_image)
            self.update_button_states()

    def redo(self):
        """Redo last undone operation"""
        if self.redo_stack:
            # Save current state to undo stack
            if self.current_cropped_image is not None:
                self.undo_stack.append((self.current_cropped_image.copy(), self.resize_scale))
            
            # Restore next state
            next_image, next_scale = self.redo_stack.pop()
            self.current_cropped_image = next_image
            self.resize_scale = next_scale
            self.scale_slider.set(next_scale)
            self.scale_value.config(text=f"{next_scale}%")
            self.display_cropped_image(self.current_cropped_image)
            self.update_button_states()

    def update_button_states(self):
        """Update button states based on current state"""
        has_image = self.original_image is not None
        has_undo = len(self.undo_stack) > 0
        has_redo = len(self.redo_stack) > 0
        has_crop = self.current_cropped_image is not None and self.current_cropped_image.size > 0

        self.save_btn['state'] = tk.NORMAL if has_crop else tk.DISABLED
        self.undo_btn['state'] = tk.NORMAL if has_undo else tk.DISABLED
        self.redo_btn['state'] = tk.NORMAL if has_redo else tk.DISABLED
        self.reset_btn['state'] = tk.NORMAL if has_image else tk.DISABLED

if __name__ == "__main__":
    root = tk.Tk()
    app = Imageapp(root)
    root.mainloop()