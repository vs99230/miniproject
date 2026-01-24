import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import hashlib

# Function to encode a message into an image
def encode_image(image_path, message, password, output_path):
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Error opening image: {e}") 

    encoded_image = image.copy()

    if not message:
        raise ValueError("Message cannot be empty.")
    
    message += '\0'  # Null character to indicate end
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    combined_message = password_hash + message
    binary_message = ''.join(format(ord(char), '08b') for char in combined_message)
    
    width, height = encoded_image.size
    if len(binary_message) > width * height:
        raise ValueError("Message is too long to encode in this image.")
    
    data_index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(encoded_image.getpixel((x, y)))
            if data_index < len(binary_message):
                pixel[0] = (pixel[0] & ~1) | int(binary_message[data_index])
                data_index += 1
            encoded_image.putpixel((x, y), tuple(pixel))
            if data_index >= len(binary_message):
                encoded_image.save(output_path, format=image.format)
                messagebox.showinfo("Success", f"Message encoded and saved as '{output_path}'.")
                return
    
    raise ValueError("Message is too long to encode in this image.")

# Function to decode the message
def decode_image(image_path, password):
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")
    
    binary_message = ''
    width, height = image.size
    for y in range(height):
        for x in range(width):
            pixel = image.getpixel((x, y))
            binary_message += str(pixel[0] & 1)
            if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
                decoded_message = ''.join(chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message) - 8, 8))
                password_hash = decoded_message[:64]
                original_message = decoded_message[64:]
                if password_hash == hashlib.sha256(password.encode()).hexdigest():
                    return original_message
                else:
                    raise ValueError("Incorrect password.")
    raise ValueError("No hidden message found.")

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Image Steganography Tool")
    root.geometry("500x400")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
    style.configure("TLabel", font=("Arial", 10))
    
    tab_control = ttk.Notebook(root)
    tab_encode = ttk.Frame(tab_control)
    tab_decode = ttk.Frame(tab_control)
    tab_control.add(tab_encode, text='Encode')
    tab_control.add(tab_decode, text='Decode')
    tab_control.pack(expand=1, fill="both")

    # Encoding Tab
    ttk.Label(tab_encode, text="Select Image to Encode:").pack(pady=5)
    image_path_entry = ttk.Entry(tab_encode, width=50)
    image_path_entry.pack(pady=5)
    ttk.Button(tab_encode, text="Browse", command=lambda: select_image(image_path_entry)).pack(pady=5)
    
    ttk.Label(tab_encode, text="Message:").pack(pady=5)
    message_entry = ttk.Entry(tab_encode, width=50)
    message_entry.pack(pady=5)
    
    ttk.Label(tab_encode, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(tab_encode, show='*', width=50)
    password_entry.pack(pady=5)
    
    ttk.Button(tab_encode, text="Encode Message", command=lambda: encode_message(image_path_entry, message_entry, password_entry)).pack(pady=10)

    # Decoding Tab
    ttk.Label(tab_decode, text="Select Image to Decode:").pack(pady=5)
    decode_image_path_entry = ttk.Entry(tab_decode, width=50)
    decode_image_path_entry.pack(pady=5)
    ttk.Button(tab_decode, text="Browse", command=lambda: select_image(decode_image_path_entry)).pack(pady=5)
    
    ttk.Label(tab_decode, text="Password:").pack(pady=5)
    password_entry_decode = ttk.Entry(tab_decode, show='*', width=50)
    password_entry_decode.pack(pady=5)
    
    ttk.Button(tab_decode, text="Decode Message", command=lambda: decode_message(decode_image_path_entry, password_entry_decode)).pack(pady=10)
    
    root.mainloop()

# Helper Functions
def select_image(entry_widget):
    file_path = filedialog.askopenfilename(title="Select Image")
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

def encode_message(image_entry, message_entry, password_entry):
    image_path = image_entry.get()
    message = message_entry.get()
    password = password_entry.get()
    output_path = filedialog.asksaveasfilename(title="Save Encoded Image", defaultextension=".png")
    
    if image_path and message and password and output_path:
        try:
            encode_image(image_path, message, password, output_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

def decode_message(image_entry, password_entry):
    image_path = image_entry.get()
    password = password_entry.get()
    
    if not password:
        messagebox.showerror("Error", "Please provide a password.")
        return
    
    if image_path and password:
        try:
            secret_message = decode_image(image_path, password)
            messagebox.showinfo("Decoded Message", secret_message)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "Please provide an image path.")

if __name__ == "__main__":
    create_gui()