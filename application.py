from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar, Style
from PIL import ImageTk, Image
import os
import time
import rsa
from tkinter import ttk
import numpy as np
import sounddevice as sd
import soundfile as sf

root = Tk()
root.title("File Conversion Application")

# Set window size and position
window_width = 1100
window_height =500
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

#convert .mp3 to Encrypted ..dna file
def mp3_to_dna():
    file_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if file_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

         # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

        # read the MP3 file in chunks
        chunk_size = 8192
        binary_data = bytearray()
        with open(file_path, 'rb') as fid:
            while True:
                chunk = fid.read(chunk_size)
                if not chunk:
                    break
                binary_data += chunk

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

        # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.dna", defaultextension=".dna",filetypes=[("DNA Sequence",".dna")])

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

        
        update_progress(progress_mp3_to_dna)
        messagebox.showinfo("Conversion Successful", "mp3 to dna Encrypted conversion completed. Output file saved at: " + output_path)
        progress_mp3_to_dna['value'] = 0



#convert encrypted .dna file to .mp3 file 
def dna_to_mp3():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    private_key_file_path = filedialog.askopenfilename(title="Select Private key file")
    if file_path and private_key_file_path:

        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

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

        # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.mp3", defaultextension=".mp3",filetypes=[("mp3 file",".mp3")])

        # Write binary data to MP3 file
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

        update_progress(progress_dna_to_mp3)
        messagebox.showinfo("Conversion Successful", "Encrypted DNA sequence to Decrypted MP3 conversion completed. Output file saved at: " + output_path)
        progress_dna_to_mp3['value'] = 0


# Convert MP3 to BIN
def mp3_to_bin():
    file_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if file_path:
        
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

        # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

        # read the MP3 file in chunks
        chunk_size = 8192
        binary_data = bytearray()
        with open(file_path, 'rb') as fid:
            while True:
                chunk = fid.read(chunk_size)
                if not chunk:           
                    break
                binary_data += chunk

        # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.bin", defaultextension=".bin",filetypes=[("Binary File",".bin")])

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
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
         # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

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

        # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.dna", defaultextension=".dna",filetypes=[("DNA Sequence",".dna")])

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
        messagebox.showinfo("Conversion Successful", "BIN to Encrypted DNA sequence conversion completed. Output file saved at: " + output_path)
        progress_bin_to_dna['value'] = 0


# Convert DNA to JPEG
def dna_to_jpeg():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    if file_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

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

        # ask user to choose the output file path
        output_image_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.jpeg", defaultextension=".jpeg",filetypes=[("JPEG",".jpeg")])
        image.save(output_image_path)

        update_progress(progress_dna_to_jpeg)
        messagebox.showinfo("Conversion Successful", "DNA to JPEG conversion completed. Output file saved at: " + output_image_path)
        progress_dna_to_jpeg['value'] = 0


# Convert DNA to BIN
def dna_to_bin():
    file_path = filedialog.askopenfilename(title="Select DNA file to convert")
    private_key_file_path = filedialog.askopenfilename(title="Select Private key file")
    if file_path and private_key_file_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

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

        

         # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}_decrypted.bin", defaultextension=".bin",filetypes=[("Binary File",".bin")])

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
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        # extract the file name from the file path
        file_name = os.path.basename(file_path).split('.')[0]

        #open bin file to read data
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        
        # ask user to choose the output file path
        output_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{file_name}.mp3", defaultextension=".mp3",filetypes=[("MP3",".mp3")])

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
    
def generate_audio():
    # Get user inputs from the entry widgets
    frequency = float(frequency_entry.get())
    function_str = clicked_function.get()
    amplitude = float(amplitude_entry.get())

    # Constants
    sample_rate = 44100  # Sample rate in Hz
    duration = 6       # Duration of the audio in seconds

    # Generate time vector
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Evaluate user-defined function
    try:
        # Create a dictionary for the math module functions
        math_functions = {
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'log': np.log,
            'sqrt': np.sqrt,
            'abs': np.abs,
            'np': np
        }

        # Evaluate the user-defined function for each element of t
        func = lambda x: eval(function_str, math_functions, {'t': x})
        signal = amplitude * func(t)

        # Create the sinusoidal signal
        sinusoid = np.sin(2 * np.pi * frequency * t)

        # Combine the signals
        final_signal = signal * sinusoid

        # Save the audio as a .wav file
        output_filename = filedialog.asksaveasfilename(title="Choose Output File",initialfile="output.wav", defaultextension=".wav",filetypes=[("WAV",".wav")])

        sf.write(output_filename, final_signal, sample_rate)

        print(f"Audio saved as {output_filename}")
        messagebox.showinfo("Generated Successfully", f".mp3 of function {function_str} is generated. Output file saved at: " + output_filename)


    except (NameError, ValueError, SyntaxError):
        print("Invalid function. Please check your input.")


# Create Menu

#create frame for title
title_frame = Frame(root,bg="#016e9f")
title_frame.pack(fill=X,padx=5,pady=5)

title_label=Label(title_frame,text="MusiOtic 1.0",font=("Helvetica",14,"bold"))
title_label.pack()

#create main frames for button ,lables and progress bar
main_frame = Frame(root,bg="#fdffff")
main_frame.pack(expand=True,fill=BOTH,pady=4,side="left")

# title_label=Label(main_frame,text="File Conversions",font=("Helvetica",14,"italic"))
# title_label.grid(row=0,column=3,padx=5,pady=5, sticky="n",columnspan=3)

# add separator between to feature 
# separator = ttk.Separator(main_frame, orient="horizontal")
# separator.grid(row=1, column=2,sticky="ew", columnspan=3, padx=10, pady=10)
# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=2, column=2,sticky="ew", columnspan=3, padx=10, pady=10)

# Create Lable and buttons 
mp3_to_dna_label=Label(main_frame,text="Convert .mp3 file to Encrypted .dna file:",font=("Helvetica",14))
mp3_to_dna_label.grid(row=3,column=0,padx=10,pady=10,sticky="e",columnspan=3)
button_mp3_to_dna = Button(main_frame, text="Select .mp3 file", command=mp3_to_dna,bg="#ADD8E6")
button_mp3_to_dna.grid(row=4, column=0, padx=5,pady=5,sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=5, column=0,sticky="e",columnspan=3, padx=10, pady=10)

dna_to_mp3_label=Label(main_frame,text="Convert Encrypted .dna file to Decrypted .mp3 file:",font=("Helvetica",14))
dna_to_mp3_label.grid(row=3,column=4,padx=10,pady=10,sticky="e",columnspan=3)
button_dna_to_mp3 = Button(main_frame, text="Select .dna file", command=dna_to_mp3,bg="#ADD8E6")
button_dna_to_mp3.grid(row=4, column=4, padx=5,pady=5,sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=5, column=4,sticky="e", columnspan=3, padx=10, pady=10)

#############################################################  3,4,5

mp3_to_bin_label=Label(main_frame,text="Convert .mp3 file to .bin file:",font=("Helvetica",14))
mp3_to_bin_label.grid(row=6,column=0,padx=10,pady=10, sticky="e",columnspan=3)
button_mp3_to_bin = Button(main_frame, text="Select .mp3 file", command=mp3_to_bin,bg="#ADD8E6")
button_mp3_to_bin.grid(row=7, column=0, padx=5,pady=5, sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=8, column=0,sticky="e", columnspan=3, padx=10, pady=10)

bin_to_mp3_label=Label(main_frame,text="Convert .bin file to .mp3 file :",font=("Helvetica",14))
bin_to_mp3_label.grid(row=6,column=4,padx=10,pady=10, sticky="e", columnspan=3)
button_bin_to_mp3 = Button(main_frame, text="Select .bin file", command=bin_to_mp3,bg="#ADD8E6")
button_bin_to_mp3.grid(row=7, column=4,padx=5, pady=5, sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=8, column=4,sticky="e", columnspan=3, padx=10, pady=10)

################################################################## 6,7,8

bin_to_dna_label=Label(main_frame,text="Convert .bin file to Encrypted .dna file:",font=("Helvetica",14))
bin_to_dna_label.grid(row=9,column=0,padx=10,pady=10,sticky="e", columnspan=3)
button_bin_to_dna = Button(main_frame, text="Select .bin file", command=bin_to_dna,bg="#ADD8E6")
button_bin_to_dna.grid(row=10, column=0, padx=5,pady=5, sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=11, column=0, sticky="e", columnspan=3, padx=10, pady=10)

dna_to_bin_label=Label(main_frame,text="Convert Encrypted .dna file to Decrypted .bin file:",font=("Helvetica",14))
dna_to_bin_label.grid(row=9,column=4,padx=10,pady=10, sticky="e", columnspan=3)
button_dna_to_bin = Button(main_frame, text="Select .dna file", command=dna_to_jpeg,bg="#ADD8E6")
button_dna_to_bin.grid(row=10, column=4,padx=5, pady=5, sticky="e")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=11, column=4, sticky="e", columnspan=3, padx=10, pady=10)

############################################### 9,10,11

dna_to_jpeg_label=Label(main_frame,text="Convert .dna file to .jpeg file:",font=("Helvetica",14))
dna_to_jpeg_label.grid(row=12,column=2,padx=10,pady=10, sticky="ew", columnspan=3)
button_dna_to_jpeg = Button(main_frame, text="Select .dna file", command=dna_to_bin,bg="#ADD8E6")
button_dna_to_jpeg.grid(row=13, column=2,padx=5, pady=5, sticky="ew")

# add separator between to feature 
separator = ttk.Separator(main_frame, orient="horizontal")
separator.grid(row=14, column=2, sticky="ew", columnspan=3, padx=10, pady=10)

# create Progress Bar For File Downloading status

progress_mp3_to_dna = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_mp3_to_dna.grid(row=4, column=2,padx=20, pady=7)

progress_dna_to_mp3 = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_mp3.grid(row=4, column=5,padx=20, pady=7)

progress_mp3_to_bin = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_mp3_to_bin.grid(row=7, column=1,padx=20, pady=7, columnspan=3)

progress_bin_to_dna = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_dna.grid(row=7, column=5, padx=20,pady=7, columnspan=3)

progress_dna_to_jpeg = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_jpeg.grid(row=10, column=1,padx=20, pady=7, columnspan=3)

progress_dna_to_bin = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_bin.grid(row=10, column=5, padx=20,pady=7, columnspan=3)

progress_bin_to_mp3 = Progressbar(main_frame, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_mp3.grid(row=13, column=3, padx=20,pady=7, columnspan=3)

#main_frame.columnconfigure(3, weight=1)

# Set initial progress to 0
progress_mp3_to_dna['value'] = 0
progress_dna_to_mp3['value'] = 0
progress_mp3_to_bin['value'] = 0
progress_bin_to_dna['value'] = 0
progress_dna_to_jpeg['value'] = 0
progress_dna_to_bin['value'] = 0
progress_bin_to_mp3['value'] = 0

#  create frame for function to mp3 feature 
f_frame = Frame(root,bg="#fdffff")
f_frame.pack(expand=True,fill=BOTH,padx=1,pady=1,side="left")

# Frequency label and entry
frequency_label =Label(f_frame, text="Frequency (Hz):",font=("Helvetica",12))
frequency_label.pack(pady=10)
frequency_entry = Entry(f_frame)
frequency_entry.pack(pady=10)

# Amplitude label and entry
amplitude_label =Label(f_frame, text="Amplitude:",font=("Helvetica",12))
amplitude_label.pack(pady=10)
amplitude_entry =Entry(f_frame)
amplitude_entry.pack(pady=10)

# Function label and entry
function_label =Label(f_frame, text="Function:",font=("Helvetica",12))
function_label.pack(pady=10)
function_entry =Entry(f_frame)
function_entry.pack(pady=10)

# drop down menu for font style
function_list = ["sin(t)", "cos(t)", "tan(t)", "log(t)", "exp(t)", "sqrt(t)","abs(t)","All Numpy Function"]
clicked_function = StringVar()
clicked_function.set("")

# Additional option for All Numpy Functions
function_list = ["sin(t)", "cos(t)", "tan(t)", "log(t)", "exp(t)", "sqrt(t)", "abs(t)", "All Numpy Functions"]

def update_function(*args):
    selected_function = clicked_function.get()
    if selected_function == "All Numpy Functions":
        function_entry.delete(0, END)
        function_entry.insert(0, "np.")
    else:
        function_entry.delete(0, END)
        function_entry.insert(0, selected_function)

clicked_function.trace('w', update_function)
drop_function = OptionMenu(f_frame, clicked_function, *function_list)
drop_function.pack(pady=2)

def update_custom_function(event):
    custom_function = function_entry.get()
    clicked_function.set(custom_function)

function_entry.bind("<FocusOut>", update_custom_function)

# Generate audio button
generate_button =Button(f_frame, text="Generate .wav File", command=generate_audio,bg="#ADD8E6")
generate_button.pack(pady=10)

root.mainloop()
