from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar, Style
from PIL import ImageTk, Image
import os
import time
import wave
import rsa
from tkinter import ttk

root = Tk()
root.title("File Conversion Application")

# Set window size and position
window_width = 500
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
        #set output path
        output_path = os.path.basename(file_path).split('.')[0] + ".bin"

        # read the MP3 file in chunks
        chunk_size = 8192
        binary_data = bytearray()
        with open(file_path, 'rb') as fid:
            while True:
                chunk = fid.read(chunk_size)
                if not chunk:
                    break
                binary_data += chunk

        #write binary data in output file
        with open(output_path, 'wb') as file:
            file.write(binary_data)
            #print(f"Wrote {len(file_data)} bytes to {output_path}")

        
        update_progress(progress_mp3_to_bin)
        messagebox.showinfo("Conversion Successful", "MP3 to BIN conversion completed. Output file saved at: " + f"{output_path}")
        progress_mp3_to_bin['value'] = 0

        

# Convert BIN to DNA
def bin_to_dna():
    file_path = filedialog.askopenfilename(title="Select BIN file to convert")
    if file_path:

        #open bin file to read data
        with open(file_path, 'rb') as file:
            binary_data = file.read()

        # generate RSA key pair using import rsa  
        (public_key, private_key) = rsa.newkeys(2048)

        # encrypt binary Bytes using RSA public key
        key_size = 2048
        chunk_size = (key_size // 8) - 11  # Calculate chunk size based on key size
        encrypted_data =[]
        for i in range(0, len(binary_data), chunk_size):
            chunk = binary_data[i:i+chunk_size]
            encrypted_chunk = rsa.encrypt(chunk, public_key)
            encrypted_data.append(encrypted_chunk)   #Note - this encypted data is in Bytes(8 bit)
        #becease this function encrypt convert our binary Bytes to 8 bit and then Decimal then ecrypt using Keys

        #convert encrypted data to binary
        encrypted_binary = ''.join(format(byte, '08b') for encrypted_chunk in encrypted_data for byte in encrypted_chunk) 
        

        # mapping binary to AGCT
        dna_sequence = ""
        nucleotide_mapping = {
            "00": "A",
            "01": "T",
            "10": "G",
            "11": "C"
        }

        for i in range(0, len(encrypted_binary), 2):
            bits =encrypted_binary[i:i+2]
            dna_sequence += nucleotide_mapping[bits]

        #set output path
        output_path = os.path.basename(file_path).split('.')[0] + ".dnac"

        #save DNA sequence to .dnac file
        with open(output_path, 'w') as file:
            file.write(dna_sequence)   
            

        #attach public key in to our file
        public_key_path = os.path.join(os.getcwd(), 'public_key.pem')
        with open(public_key_path, 'wb') as file:
            file.write(public_key.save_pkcs1('PEM'))

        #attach private key in to our file
        private_key_path = os.path.join(os.getcwd(), 'private_key.pem')
        with open(private_key_path, 'wb') as file:
            file.write(private_key.save_pkcs1('PEM'))

        
        update_progress(progress_bin_to_dna)
        messagebox.showinfo("Conversion Successful", "BIN to DNA conversion completed. Output file saved at: " + output_path)
        progress_bin_to_dna['value'] = 0


# Convert DNA to JPEG
def dna_to_jpeg():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    if file_path:

        # open .dnac file to read data
        with open(file_path, 'r') as file:
            dna_sequence = file.read()
        
        # Convert the DNA sequence to an image
        image_width = 1800  # Adjust the width of the image based on your requirements
        image_height = len(dna_sequence) // image_width + 1
        image = Image.new('RGB', (image_width, image_height))
        pixels = image.load()

        # Map DNA bases to colors
        color_mapping = {'A': (255, 0, 0), 'C': (0, 0, 255), 'G': (0, 255, 0), 'T': (255, 255, 0)}

        # Assign colors to pixels
        for i, base in enumerate(dna_sequence):
            x = i % image_width
            y = i // image_width
            color = color_mapping.get(base, (0, 0, 0))
            pixels[x, y] = color

        # Save the image
        output_image_path = os.path.basename(file_path).split('.')[0] + "_Image.jpeg"
        image.save(output_image_path)

        update_progress(progress_dna_to_jpeg)
        messagebox.showinfo("Conversion Successful", "DNA to JPEG conversion completed. Output file saved at: " + output_image_path)
        progress_dna_to_jpeg['value'] = 0


# Convert DNA to BIN
def dna_to_bin():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    private_key_file_path = filedialog.askopenfilename(title="Select Private key file")
    if file_path and private_key_file_path:

        # get RSA private key from .pem file 
        with open(private_key_file_path, 'rb') as key_file:
            private_key = rsa.PrivateKey.load_pkcs1(key_file.read())


        # open .dnac file to read data
        with open(file_path, 'r') as file:
            dna_sequence = file.read()

        # mapping AGCT to binary 
        binary_data = ""
        nucleotide_mapping = {
            "A": "00",
            "T": "01",
            "G": "10",
            "C": "11"
        }

        chunk_size = 8192  # Adjust the chunk size based on your system's memory capacity
        total_length = len(dna_sequence)

        for i in range(0, total_length, chunk_size):
                chunk = dna_sequence[i:i+chunk_size]
                binary_chunk = ''.join(nucleotide_mapping.get(chunk[j:j+1]) for j in range(0, len(chunk)))
                binary_data += binary_chunk
                
        # decrypt the binary data using RSA private key
        decrypted_data =bytearray()
        chunk_size = (2048) 
        for i in range(0, len(binary_data), chunk_size):
            chunk = binary_data[i:i+chunk_size]
            decrypted_chunk = bytes(int(chunk[i:i+8], 2) for i in range(0, len(chunk), 8))
            decrypted_chunk = rsa.decrypt(decrypted_chunk, private_key)
            #decrypted_chunk = rsa.decrypt(chunk.encode(), private_key)
            decrypted_data.extend(decrypted_chunk)  # binary data result is in Bytes(8-bit combination)

        

        # set output path
        output_path = os.path.basename(file_path).split('.')[0] + "(1).bin"

        # save DNA sequence to .bin file
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)
        
        update_progress(progress_dna_to_bin)
        messagebox.showinfo("Conversion Successful", "DNA to BIN conversion completed. Output file saved at: " + output_path)
        progress_dna_to_bin['value'] = 0


# Convert BIN to MP3
def bin_to_mp3():
    file_path = filedialog.askopenfilename(title="Select BIN file to convert")
    if file_path:

        #open bin file to read data
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        
        # set output path
        output_path = os.path.basename(file_path).split('.')[0] + "_audio.mp3"

        # Write binary data to MP3 file
        with open(output_path, 'wb') as file:
            file.write(binary_data)

        update_progress(progress_bin_to_mp3)
        messagebox.showinfo("Conversion Successful", "BIN to MP3 conversion completed. Output file saved at: " + output_path)
        progress_bin_to_mp3['value'] = 0


# Update the progress bar
def update_progress(progress_bar):
    progress = 0
    while progress <= 100:
        progress_bar['value'] = progress
        root.update_idletasks()
        time.sleep(PROGRESS_DELAY / 1000)
        progress += 5
    
#creat statusbar
# status_bar=Label(root,text="ready        ",anchor=E)
# status_bar.pack(fill=X,side=BOTTOM,ipadx=5)   

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

#create frame for title
title_frame = Frame(root,bg="#F5F5FF")
title_frame.pack(expand=True,fill=X,padx=5,pady=2,side="top")

title_label=Label(title_frame,text="App Name",font=("Helvetica",14,"bold"))
title_label.grid(row=0,column=3,padx=5,pady=5, sticky="n",columnspan=3)

#create main frames for button ,lables and progress bar
main_frame = Frame(root,bg="#F5F5FF")
main_frame.pack(expand=True,fill=BOTH,padx=5,pady=4,side="top")

title_label=Label(main_frame,text="File Conversions",font=("Helvetica",14,"italic"))
title_label.grid(row=0,column=3,padx=5,pady=5, sticky="n",columnspan=3)

# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=1, column=3,sticky="ew", columnspan=3, padx=10, pady=10)
# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=2, column=3,sticky="ew", columnspan=3, padx=10, pady=10)

# Create Lable and buttons 
mp3_to_bin_label=Label(main_frame,text="Convert .mp3 file to .bin file:",font=("Helvetica",14))
mp3_to_bin_label.grid(row=3,column=3,padx=10,pady=10, sticky="n",columnspan=3)
button_mp3_to_bin = Button(main_frame, text="Select .mp3 file", command=mp3_to_bin,bg="#707080")
button_mp3_to_bin.grid(row=4, column=3, padx=5,pady=5, sticky="n")

# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=5, column=3,sticky="ew", columnspan=3, padx=10, pady=10)

bin_to_dna_label=Label(main_frame,text="Convert .bin file to .dnac file:",font=("Helvetica",14))
bin_to_dna_label.grid(row=6,column=3,padx=10,pady=10,sticky="n", columnspan=3)
button_bin_to_dna = Button(main_frame, text="Select .bin file", command=bin_to_dna,bg="#707080")
button_bin_to_dna.grid(row=7, column=3, padx=5,pady=5, sticky="n")

# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=8, column=3, sticky="ew", columnspan=3, padx=10, pady=10)

dna_to_jpeg_label=Label(main_frame,text="Convert .dnac file to .jpeg file:",font=("Helvetica",14))
dna_to_jpeg_label.grid(row=9,column=3,padx=10,pady=10, sticky="n", columnspan=3)
button_dna_to_jpeg = Button(main_frame, text="Select .dnac file", command=dna_to_jpeg,bg="#707080")
button_dna_to_jpeg.grid(row=10, column=3,padx=5, pady=5, sticky="n")

# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=11, column=3, sticky="ew", columnspan=3, padx=10, pady=10)

dna_to_bin_label=Label(main_frame,text="Convert .dnac file to .bin file:",font=("Helvetica",14))
dna_to_bin_label.grid(row=12,column=3,padx=10,pady=10, sticky="n", columnspan=3)
button_dna_to_bin = Button(main_frame, text="Select .dnac file", command=dna_to_bin,bg="#707080")
button_dna_to_bin.grid(row=13, column=3,padx=5, pady=5, sticky="n")

# Add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=14, column=3, sticky="ew", columnspan=3, padx=10, pady=10)

bin_to_mp3_label=Label(main_frame,text="Convert .bin file to .mp3 file :",font=("Helvetica",14))
bin_to_mp3_label.grid(row=15,column=3,padx=10,pady=10, sticky="n", columnspan=3)
button_bin_to_mp3 = Button(main_frame, text="Select .bin file", command=bin_to_mp3,bg="#707080")
button_bin_to_mp3.grid(row=16, column=3,padx=5, pady=5, sticky="n")


# Create Progress Bar For File Downloading status

progress_mp3_to_bin = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_mp3_to_bin.grid(row=4, column=4,padx=20, pady=7, columnspan=3)

progress_bin_to_dna = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_dna.grid(row=7, column=4, padx=20,pady=7, columnspan=3)

progress_dna_to_jpeg = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_jpeg.grid(row=10, column=4,padx=20, pady=7, columnspan=3)

progress_dna_to_bin = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_bin.grid(row=13, column=4, padx=20,pady=7, columnspan=3)

progress_bin_to_mp3 = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_mp3.grid(row=16, column=4, padx=20,pady=7, columnspan=3)

#main_frame.columnconfigure(3, weight=1)



# Set initial progress to 0
progress_mp3_to_bin['value'] = 0
progress_bin_to_dna['value'] = 0
progress_dna_to_jpeg['value'] = 0
progress_dna_to_bin['value'] = 0
progress_bin_to_mp3['value'] = 0

root.mainloop()
