from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
from tkinter.ttk import Style
import os
import time

root = Tk()
root.title("File Conversion Application")

# Set window size and position
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Define colors
bg_color = "#F5F5F5"
button_bg_color = "#4CAF50"
button_fg_color = "white"
progress_color = "#4CAF50"
font_style = ("Arial", 14)



# Delay between progress bar updates (in milliseconds)
PROGRESS_DELAY = 100

# Convert MP3 to BIN
def mp3_to_bin():
    file_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if file_path:
        output_path = os.path.splitext(file_path)[0] + ".bin"
        os.rename(file_path, output_path)
        messagebox.showinfo("Conversion Successful", "MP3 to BIN conversion completed. Output file saved at: " + output_path)
        progress = 0
        while progress <= 100:
            progress_mp3_to_bin['value'] = progress
            root.update_idletasks()
            time.sleep(PROGRESS_DELAY / 1000)
            progress += 10

# Convert BIN to DNA
def bin_to_dna():
    file_path = filedialog.askopenfilename(title="Select BIN file to convert")
    if file_path:
        output_path = os.path.splitext(file_path)[0] + ".dna"
        os.rename(file_path, output_path)
        messagebox.showinfo("Conversion Successful", "BIN to DNA conversion completed. Output file saved at: " + output_path)
        progress = 0
        while progress <= 100:
            progress_bin_to_dna['value'] = progress
            root.update_idletasks()
            time.sleep(PROGRESS_DELAY / 1000)
            progress += 10

# Convert DNA to JPEG
def dna_to_jpeg():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    if file_path:
        output_path = os.path.splitext(file_path)[0] + ".jpeg"
        os.rename(file_path, output_path)
        messagebox.showinfo("Conversion Successful", "DNA to JPEG conversion completed. Output file saved at: " + output_path)
        progress = 0
        while progress <= 100:
            progress_dna_to_jpeg['value'] = progress
            root.update_idletasks()
            time.sleep(PROGRESS_DELAY / 1000)
            progress += 10

# Convert DNA to BIN
def dna_to_bin():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    if file_path:
        output_path = os.path.splitext(file_path)[0] + ".bin"
        os.rename(file_path, output_path)
        messagebox.showinfo("Conversion Successful", "DNA to BIN conversion completed. Output file saved at: " + output_path)
        progress = 0
        while progress <= 100:
            progress_dna_to_bin['value'] = progress
            root.update_idletasks()
            time.sleep(PROGRESS_DELAY / 1000)
            progress += 10

# Convert BIN to MP3
def bin_to_mp3():
    file_path = filedialog.askopenfilename(title="Select BIN file to convert")
    if file_path:
        output_path = os.path.splitext(file_path)[0] + ".mp3"
        os.rename(file_path, output_path)
        messagebox.showinfo("Conversion Successful", "BIN to MP3 conversion completed. Output file saved at: " + output_path)
        progress = 0
        while progress <= 100:
            progress_bin_to_mp3['value'] = progress
            root.update_idletasks()
            time.sleep(PROGRESS_DELAY / 1000)
            progress += 10

# Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Add Convert Menu
convert_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Convert", menu=convert_menu)
convert_menu.add_command(label="MP3 to BIN", command=mp3_to_bin)
convert_menu.add_command(label="BIN to DNA", command=bin_to_dna)
convert_menu.add_command(label="DNA to JPEG", command=dna_to_jpeg)
convert_menu.add_command(label="DNA to BIN", command=dna_to_bin)
convert_menu.add_command(label="BIN to MP3", command=bin_to_mp3)

# Conversion Buttons
button_frame = Frame(root)
button_frame.grid(row=0, column=0, padx=10, pady=10)

button_mp3_to_bin = Button(button_frame, text="MP3 to BIN", command=mp3_to_bin)
button_mp3_to_bin.grid(row=0, column=0, pady=5)

button_bin_to_dna = Button(button_frame, text="BIN to DNA", command=bin_to_dna)
button_bin_to_dna.grid(row=1, column=0, pady=5)

button_dna_to_jpeg = Button(button_frame, text="DNA to JPEG", command=dna_to_jpeg)
button_dna_to_jpeg.grid(row=2, column=0, pady=5)

button_dna_to_bin = Button(button_frame, text="DNA to BIN", command=dna_to_bin)
button_dna_to_bin.grid(row=3, column=0, pady=5)

button_bin_to_mp3 = Button(button_frame, text="BIN to MP3", command=bin_to_mp3)
button_bin_to_mp3.grid(row=4, column=0, pady=5)

button_dna_to_jpeg = Button(button_frame, text="DNA TO JPEG", command=dna_to_jpeg)
button_dna_to_jpeg.grid(row=5, column=0, pady=5)

# Progress Bars
progress_frame = Frame(root)
progress_frame.grid(row=0, column=1, padx=10, pady=10)

progress_mp3_to_bin = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_mp3_to_bin.grid(row=0, column=0, pady=5)

progress_bin_to_dna = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_bin_to_dna.grid(row=1, column=0, pady=5)

progress_dna_to_jpeg = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_dna_to_jpeg.grid(row=2, column=0, pady=5)

progress_dna_to_bin = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_dna_to_bin.grid(row=3, column=0, pady=5)

progress_bin_to_mp3 = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_bin_to_mp3.grid(row=4, column=0, pady=5)

progress_mp3_to_jpeg = Progressbar(progress_frame, orient=HORIZONTAL, length=200, mode='determinate')
progress_mp3_to_jpeg.grid(row=5, column=0, pady=5)




# Display Converted JPEG Image
image_frame = Frame(root, bg=bg_color)
image_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

image_label = Label(image_frame)
image_label.pack()

# Convert MP3 to JPEG
def mp3_to_jpeg():
    file_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if file_path:
        # Perform conversion here
        output_path = os.path.splitext(file_path)[0] + ".jpeg"

        # Update progress bar
        progress_mp3_to_jpeg['value'] = 100

        # Display the converted image
        image = Image.open(output_path)
        image = image.resize((400, 400))
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo

        # Show message box
        messagebox.showinfo("Conversion Successful", "MP3 to JPEG conversion completed. Output file saved at: " + output_path)


# Convert MP3 to JPEG Button
button_mp3_to_jpeg = Button(root, text="MP3 to JPEG", command=mp3_to_jpeg, bg=button_bg_color, fg=button_fg_color, font=font_style)
button_mp3_to_jpeg.grid(row=6, column=0, columnspan=2, pady=10)

# Style the progress bars
style = Style()
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", foreground=progress_color, background=progress_color)
progress_mp3_to_bin['style'] = "green.Horizontal.TProgressbar"
progress_bin_to_dna['style'] = "green.Horizontal.TProgressbar"
progress_dna_to_jpeg['style'] = "green.Horizontal.TProgressbar"
progress_dna_to_bin['style'] = "green.Horizontal.TProgressbar"
progress_bin_to_mp3['style'] = "green.Horizontal.TProgressbar"

# Set initial progress to 0
progress_mp3_to_bin['value'] = 0
progress_bin_to_dna['value'] = 0
progress_dna_to_jpeg['value'] = 0
progress_dna_to_bin['value'] = 0
progress_bin_to_mp3['value'] = 0


root.mainloop()
