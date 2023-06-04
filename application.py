from tkinter import *
from tkinter import filedialog,messagebox
from tkinter.ttk import Progressbar,Style
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

# adjust popup-window width and height
w_width = 1100
w_height =500
s_width = root.winfo_screenwidth()
s_height = root.winfo_screenheight()
x = (s_width // 2) - (w_width // 2)
y = (s_height // 2) - (w_height // 2)
root.geometry(f"{w_width}x{w_height}+{x}+{y}")


#delay of progress bar Updation (in millisecond)
PROGRESS_DELAY = 100

#convert .mp3 to Encrypted ..dna file with rsa algorithm
def mp3_to_dna():
    f_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if f_path:

        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

         #get file name from file path 
        f_n = os.path.basename(f_path).split('.')[0]

        #read the MP3 file in chunks  # because large file in one could not handle easily Data lose possible in that 
        chunk_sz = 8192
        bin_d = bytearray()
        with open(f_path, 'rb') as fid:
            while True:
                chunk = fid.read(chunk_sz)
                if not chunk:
                    break
                bin_d += chunk

        #generate RSA key pair using import rsa  
        (public_key, private_key) = rsa.newkeys(2048) # 2048 is length of the Private and Public Keys

        # encrypt binary Bytes using RSA public key
        key_sz = 2048
        chunk_sz = (key_sz // 8) - 11  # calculate chunk size based on key size
        enc_data =[]
        for i in range(0, len(bin_d), chunk_sz):
            chunk = bin_d[i:i+chunk_sz]
            enc_chunk = rsa.encrypt(chunk, public_key)
            enc_data.append(enc_chunk)   #Note - this encypted data is in Bytes(8 bit)
        #becease this function encrypt convert our binary Bytes to 8 bit and then Decimal then ecrypt using Keys

        #convert encrypted data to binary
        enc_bits = ''.join(format(byte, '08b') for enc_chunk in enc_data for byte in enc_chunk) 

        #mapping binary to AGCT
        dna_sequence = ""
        nucleotide_mapping = {
            "00": "A",
            "01": "T",
            "10": "G",
            "11": "C"
        }

        for i in range(0, len(enc_bits), 2):
            bits =enc_bits[i:i+2]
            dna_sequence += nucleotide_mapping[bits]

        #ask user to choose the output file path 
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_n}.dna", 
                                               defaultextension=".dna",filetypes=[("DNA Sequence",".dna")])

        #save DNA sequence to .dna file
        with open(op_path, 'w') as file:
            file.write(dna_sequence)   

        #attach public key in to our file
        pub_path = os.path.join(os.getcwd(), 'public_key.pem')
        with open(pub_path, 'wb') as file:
            file.write(public_key.save_pkcs1('PEM'))

        #attach private key in to our file
        priv_path = os.path.join(os.getcwd(), 'private_key.pem')
        with open(priv_path, 'wb') as file:
            file.write(private_key.save_pkcs1('PEM'))

        
        update_progress(progress_mp3_to_dna)
        messagebox.showinfo("Conversion Successful",
                             "mp3 to dna Encrypted conversion completed. Output file saved at: " + op_path)
        progress_mp3_to_dna['value'] = 0



#convert encrypted .dna file to .mp3 file 
def dna_to_mp3():
    f_path = filedialog.askopenfilename(title="Select DNA file to convert")
    priv_f_path = filedialog.askopenfilename(title="Select Private key file")
    if f_path and priv_f_path:

        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

        #extract the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        #get RSA private key from .pem file 
        with open(priv_f_path, 'rb') as key_file:
            private_key = rsa.PrivateKey.load_pkcs1(key_file.read())


        # open .dnac file to read data
        with open(f_path, 'r') as file:
            dna_sequence = file.read()

        #mapping AGCT to binary 
        bin_d = ""
        nucleotide_mapping = {
            "A": "00",
            "T": "01",
            "G": "10",
            "C": "11"
        }

        chunk_sz = 8192  #read large dna_sequence in samll chunk
        tot_len = len(dna_sequence)

        for i in range(0, tot_len, chunk_sz):
                chunk = dna_sequence[i:i+chunk_sz]
                bin_chunk = ''.join(nucleotide_mapping.get(chunk[j:j+1]) for j in range(0, len(chunk)))
                bin_d += bin_chunk
                
        #decrypt the binary data using RSA private key
        dec_data =bytearray()
        chunk_sz = (2048) 
        for i in range(0, len(bin_d), chunk_sz):
            chunk = bin_d[i:i+chunk_sz]
            dec_chunk = bytes(int(chunk[i:i+8], 2) for i in range(0, len(chunk), 8))
            dec_chunk = rsa.decrypt(dec_chunk, private_key)
            dec_data.extend(dec_chunk)  # binary data result is in Bytes(8-bit combination)

        #ask user to choose the output file path
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}.mp3", 
                                               defaultextension=".mp3",filetypes=[("mp3 file",".mp3")])

        #Write binary data to MP3 file
        with open(op_path, 'wb') as file:
            file.write(dec_data)

        update_progress(progress_dna_to_mp3)
        messagebox.showinfo("Conversion Successful", 
                            "Encrypted DNA sequence to Decrypted MP3 conversion completed. Output file saved at: " + op_path)
        progress_dna_to_mp3['value'] = 0

#convert .mp3 file to .bin file 
def mp3_to_bin():
    f_path = filedialog.askopenfilename(title="Select MP3 file to convert")
    if f_path:
        
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

        #extract the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        #read the MP3 file in chunks
        chunk_sz = 8192
        bin_data = bytearray()
        with open(f_path, 'rb') as fid:
            while True:
                chunk = fid.read(chunk_sz)
                if not chunk:           
                    break
                bin_data += chunk

        #ask user to choose the output file path
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}.bin",
                                                defaultextension=".bin",filetypes=[("Binary File",".bin")])

        #write binary data in output file
        with open(op_path, 'wb') as file:
            file.write(bin_data)
        
        update_progress(progress_mp3_to_bin)
        messagebox.showinfo("Conversion Successful",
                             "MP3 to BIN conversion completed. Output file saved at: " + f"{op_path}")
        progress_mp3_to_bin['value'] = 0

        

#convert .bin file to encrypted .dna file 
def bin_to_dna():
    f_path = filedialog.askopenfilename(title="Select BIN file to convert")
    if f_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        #get the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        #open bin file to read data
        with open(f_path, 'rb') as file:
            bin_d = file.read()

        #generate RSA key pair using import rsa  
        (public_key, private_key) = rsa.newkeys(2048)

        #encrypt binary Bytes using RSA public key
        key_sz = 2048
        chunk_sz = (key_sz // 8) - 11  # Calculate chunk size based on key size
        enc_data =[]
        for i in range(0, len(bin_d), chunk_sz):
            chunk = bin_d[i:i+chunk_sz]
            enc_chunk = rsa.encrypt(chunk, public_key)
            enc_data.append(enc_chunk)   #Note - this encypted data is in Bytes(8 bit)
        #becease this function encrypt convert our binary Bytes to 8 bit and then Decimal then ecrypt using Keys

        #convert encrypted data to binary
        enc_binstr = ''.join(format(byte, '08b') for encrypted_chunk in enc_data for byte in encrypted_chunk) 
        

        #mapping binary to AGCT
        dna_sqn = ""
        nucleotide_mapping = {
            "00": "A",
            "01": "T",
            "10": "G",
            "11": "C"
        }

        for i in range(0, len(enc_binstr), 2):
            bits =enc_binstr[i:i+2]
            dna_sqn += nucleotide_mapping[bits]

        # ask user to choose the output file path
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}.dna",
                                                defaultextension=".dna",filetypes=[("DNA Sequence",".dna")])

        #save DNA sequence to .dnac file
        with open(op_path, 'w') as file:
            file.write(dna_sqn)   

        #attach public key in to our file
        pub_path = os.path.join(os.getcwd(), 'public_key.pem')
        with open(pub_path, 'wb') as file:
            file.write(public_key.save_pkcs1('PEM'))

        #attach private key in to our file
        priv_path = os.path.join(os.getcwd(), 'private_key.pem')
        with open(priv_path, 'wb') as file:
            file.write(private_key.save_pkcs1('PEM'))

        
        update_progress(progress_bin_to_dna)
        messagebox.showinfo("Conversion Successful", 
                            "BIN to Encrypted DNA sequence conversion completed. Output file saved at: " + op_path)
        progress_bin_to_dna['value'] = 0


# convert .dna file to . jpeg image 
def dna_to_jpeg():
    f_path = filedialog.askopenfilename(title="Select DNA file to convert")
    if f_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        #get the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        #open .dnac file to read data
        with open(f_path, 'r') as file:
            dna_sqn = file.read()
        
        #convert the DNA sequence to an image
        img_width = 1800  # Adjust the width of the image based on your requirements
        img_height = len(dna_sqn) // img_width + 1
        img = Image.new('RGB', (img_width, img_height))
        pixels = img.load()

        #map DNA bases to colors
        color_mapping = {'A': (255, 0, 0), 'C': (0, 0, 255), 'G': (0, 255, 0), 'T': (255, 255, 0)}

        #assign colors to pixels
        for i, base in enumerate(dna_sqn):
            x = i % img_width
            y = i // img_width
            color = color_mapping.get(base, (0, 0, 0))
            pixels[x, y] = color

        #ask user to choose the output file path
        op_img_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}.jpeg", 
                                                   defaultextension=".jpeg",filetypes=[("JPEG",".jpeg")])
        img.save(op_img_path)

        update_progress(progress_dna_to_jpeg)
        messagebox.showinfo("Conversion Successful", 
                            "DNA to JPEG conversion completed. Output file saved at: " + op_img_path)
        progress_dna_to_jpeg['value'] = 0


#convert Encrypted .dna file to Decrypted .bin file
def dna_to_bin():
    f_path = filedialog.askopenfilename(title="Select DNA file to convert")
    priv_f_path = filedialog.askopenfilename(title="Select Private key file")

    if f_path and priv_f_path:

        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")

        #get the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        # get RSA private key from .pem file 
        with open(priv_f_path, 'rb') as key_file:
            private_key = rsa.PrivateKey.load_pkcs1(key_file.read())


        #open .dnac file to read data
        with open(f_path, 'r') as file:
            dna_sqn = file.read()

        #mapping AGCT to binary 
        bin_d = ""
        nucleotide_mapping = {
            "A": "00",
            "T": "01",
            "G": "10",
            "C": "11"
        }

        chunk_sz = 8192 
        tot_len = len(dna_sqn)

        for i in range(0, tot_len, chunk_sz):
                chunk = dna_sqn[i:i+chunk_sz]
                bin_chunk = ''.join(nucleotide_mapping.get(chunk[j:j+1]) for j in range(0, len(chunk)))
                bin_d += bin_chunk
                
        #decrypt the binary data using RSA private key
        dec_data =bytearray()
        chunk_sz = (2048) 
        for i in range(0, len(bin_d), chunk_sz):
            chunk = bin_d[i:i+chunk_sz]
            dec_chunk = bytes(int(chunk[i:i+8], 2) for i in range(0, len(chunk), 8))
            dec_chunk = rsa.decrypt(dec_chunk, private_key)
            dec_data.extend(dec_chunk)  # binary data result is in Bytes(8-bit combination)

        #ask user to choose the output file path
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}_decrypted.bin",
                                                defaultextension=".bin",filetypes=[("Binary File",".bin")])

        #save DNA sequence to .bin file
        with open(op_path, 'wb') as file:
            file.write(dec_data)
        
        update_progress(progress_dna_to_bin)
        messagebox.showinfo("Conversion Successful", 
                            "DNA to BIN conversion completed. Output file saved at: " + op_path)
        progress_dna_to_bin['value'] = 0


#convert .bin file to .mp3
def bin_to_mp3():

    f_path = filedialog.askopenfilename(title="Select BIN file to convert")

    if f_path:
        messagebox.showinfo("", "Please  wait for conversion after Pressing OK")
        # extract the file name from the file path
        f_name = os.path.basename(f_path).split('.')[0]

        #open bin file to read data
        with open(f_path, 'rb') as file:
            bin_data = file.read()
        
        # ask user to choose the output file path
        op_path = filedialog.asksaveasfilename(title="Choose Output File",initialfile=f"{f_name}.mp3", 
                                               defaultextension=".mp3",filetypes=[("MP3",".mp3")])

        # Write binary data to MP3 file
        with open(op_path, 'wb') as file:
            file.write(bin_data)

        update_progress(progress_bin_to_mp3)
        messagebox.showinfo("Conversion Successful", 
                            "BIN to MP3 conversion completed. Output file saved at: " + op_path)
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
    #get user inputs from the entry widgets
    frq = float(frequency_entry.get())
    func_str = clicked_func.get()
    amp = float(amplitude_entry.get())

    #constants
    smpl_r = 44100  #sample rate in Hz
    duration = 10       #duration of the audio in seconds

    #generate time vector
    t = np.linspace(0, duration, int(smpl_r * duration))

    #evaluate user-defined function
    try:
        #create a dictionary for the math module functions
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

            #evaluate the user-defined function for each element of t
        func = lambda x: eval(func_str, math_functions, {'t': x})
        signal = amp * func(t)

        #create the sinusoidal signal
        sinusoid = np.sin(2 * np.pi * frq * t)

                #combine the signals
        final_signal = signal * sinusoid

        #save the audio as a .wav file
        output_filename = filedialog.asksaveasfilename(title="Choose Output File",initialfile="output.wav", 
                                                       defaultextension=".wav",filetypes=[("WAV",".wav")])

        sf.write(output_filename, final_signal, smpl_r)

        print(f"Audio saved as {output_filename}")
        messagebox.showinfo("Generated Successfully",
                             f".mp3 of function {func_str} is generated. Output file saved at: " + output_filename)


    except (NameError, ValueError, SyntaxError):
        print("Invalid function. Please check your input.")

#create frame for title
title_f = Frame(root,bg="#016e9f")
title_f.pack(fill=X,padx=5,pady=5)

title_lbl=Label(title_f,text="MusiOtic 1.0",font=("Helvetica",14,"bold"))
title_lbl.pack()



#create main frames for button ,lables and progress bar
main_f = Frame(root,bg="#fdffff")

main_f.pack(expand=True,fill=BOTH,pady=4,side="left")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=2, column=2,sticky="ew", columnspan=3, padx=10, pady=10)

#Create Lable and buttons 
mp3_to_dna_lbl=Label(main_f,text="Convert .mp3 file to Encrypted .dna file:",font=("Helvetica",14))
mp3_to_dna_lbl.grid(row=3,column=0,padx=10,pady=10,sticky="e",columnspan=3)

button_mp3_to_dna = Button(main_f, text="Select .mp3 file", command=mp3_to_dna,bg="#ADD8E6")
button_mp3_to_dna.grid(row=4, column=0, padx=5,pady=5,sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=5, column=0,sticky="e",columnspan=3, padx=10, pady=10)

dna_to_mp3_lbl=Label(main_f,text="Convert Encrypted .dna file to Decrypted .mp3 file:",font=("Helvetica",14))
dna_to_mp3_lbl.grid(row=3,column=4,padx=10,pady=10,sticky="e",columnspan=3)
button_dna_to_mp3 = Button(main_f, text="Select .dna file", command=dna_to_mp3,bg="#ADD8E6")
button_dna_to_mp3.grid(row=4, column=4, padx=5,pady=5,sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=5, column=4,sticky="e", columnspan=3, padx=10, pady=10)

#############################################################  3,4,5

mp3_to_bin_lbl=Label(main_f,text="Convert .mp3 file to .bin file:",font=("Helvetica",14))
mp3_to_bin_lbl.grid(row=6,column=0,padx=10,pady=10, sticky="e",columnspan=3)

button_mp3_to_bin = Button(main_f, text="Select .mp3 file", command=mp3_to_bin,bg="#ADD8E6")
button_mp3_to_bin.grid(row=7, column=0, padx=5,pady=5, sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=8, column=0,sticky="e", columnspan=3, padx=10, pady=10)

bin_to_mp3_lbl=Label(main_f,text="Convert .bin file to .mp3 file :",font=("Helvetica",14))
bin_to_mp3_lbl.grid(row=6,column=4,padx=10,pady=10, sticky="e", columnspan=3)

button_bin_to_mp3 = Button(main_f, text="Select .bin file", command=bin_to_mp3,bg="#ADD8E6")
button_bin_to_mp3.grid(row=7, column=4,padx=5, pady=5, sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=8, column=4,sticky="e", columnspan=3, padx=10, pady=10)

################################################################## 6,7,8

bin_to_dna_lbl=Label(main_f,text="Convert .bin file to Encrypted .dna file:",font=("Helvetica",14))
bin_to_dna_lbl.grid(row=9,column=0,padx=10,pady=10,sticky="e", columnspan=3)

button_bin_to_dna = Button(main_f, text="Select .bin file", command=bin_to_dna,bg="#ADD8E6")
button_bin_to_dna.grid(row=10, column=0, padx=5,pady=5, sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=11, column=0, sticky="e", columnspan=3, padx=10, pady=10)

dna_to_bin_lbl=Label(main_f,text="Convert Encrypted .dna file to Decrypted .bin file:",font=("Helvetica",14))
dna_to_bin_lbl.grid(row=9,column=4,padx=10,pady=10, sticky="e", columnspan=3)
button_dna_to_bin = Button(main_f, text="Select .dna file", command=dna_to_bin,bg="#ADD8E6")
button_dna_to_bin.grid(row=10, column=4,padx=5, pady=5, sticky="e")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=11, column=4, sticky="e", columnspan=3, padx=10, pady=10)

############################################### 9,10,11

dna_to_jpeg_lbl=Label(main_f,text="Convert .dna file to .jpeg file:",font=("Helvetica",14))
dna_to_jpeg_lbl.grid(row=12,column=2,padx=10,pady=10, sticky="ew", columnspan=3)

button_dna_to_jpeg = Button(main_f, text="Select .dna file", command=dna_to_jpeg,bg="#ADD8E6")
button_dna_to_jpeg.grid(row=13, column=2,padx=5, pady=5, sticky="ew")

#add separator between to feature 
separator = ttk.Separator(main_f, orient="horizontal")
separator.grid(row=14, column=2, sticky="ew", columnspan=3, padx=10, pady=10)

#create Progress Bar For File Downloading status

progress_mp3_to_dna = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_mp3_to_dna.grid(row=4, column=2,padx=20, pady=7)

progress_dna_to_mp3 = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_dna_to_mp3.grid(row=4, column=5,padx=20, pady=7)


progress_mp3_to_bin = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_mp3_to_bin.grid(row=7, column=1,padx=20, pady=7, columnspan=3)

progress_bin_to_mp3 = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_mp3.grid(row=7, column=5, padx=20,pady=7, columnspan=3)


progress_bin_to_dna = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")
progress_bin_to_dna.grid(row=10, column=1, padx=20,pady=7, columnspan=3)

progress_dna_to_bin = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")

progress_dna_to_bin.grid(row=10, column=5, padx=20,pady=7, columnspan=3)



progress_dna_to_jpeg = Progressbar(main_f, orient=HORIZONTAL, length=200, mode='determinate', style="green.Horizontal.TProgressbar")

progress_dna_to_jpeg.grid(row=13, column=3,padx=20, pady=7, columnspan=3)


# #set initial progress to 0
# progress_mp3_to_dna['value'] = 0
# progress_dna_to_mp3['value'] = 0
# progress_mp3_to_bin['value'] = 0
# progress_bin_to_dna['value'] = 0
# progress_dna_to_jpeg['value'] = 0
# progress_dna_to_bin['value'] = 0
# progress_bin_to_mp3['value'] = 0

#create frame for function to mp3 feature 
f_frame = Frame(root,bg="#fdffff")
f_frame.pack(expand=True,fill=BOTH,padx=1,pady=1,side="left")

#frequency label and entry
freq_lbl =Label(f_frame, text="Frequency (Hz):",font=("Helvetica",12))
freq_lbl.pack(pady=10)
frequency_entry = Entry(f_frame)
frequency_entry.pack(pady=10)

#amplitude label and entry
ampl_lbl =Label(f_frame, text="Amplitude:",font=("Helvetica",12))
ampl_lbl.pack(pady=10)
amplitude_entry =Entry(f_frame)
amplitude_entry.pack(pady=10)

#function label and entry
func_lbl =Label(f_frame, text="Function:",font=("Helvetica",12))
func_lbl.pack(pady=10)
function_entry =Entry(f_frame)
function_entry.pack(pady=10)

#drop down menu for font style
func_lst = ["sin(t)", "cos(t)", "tan(t)", "log(t)", "exp(t)", "sqrt(t)","abs(t)","All Numpy Function"]
clicked_func = StringVar()
clicked_func.set("")

#additional option for All Numpy Functions
function_list = ["sin(t)", "cos(t)", "tan(t)", "log(t)", "exp(t)", "sqrt(t)", "abs(t)", "All Numpy Functions"]

def update_function(*args):
    selected_function = clicked_func.get()
    if selected_function == "All Numpy Functions":

        function_entry.delete(0, END)
        function_entry.insert(0, "np.")

    else:

        function_entry.delete(0, END)
        function_entry.insert(0, selected_function)

clicked_func.trace('w', update_function)
drop_func = OptionMenu(f_frame, clicked_func, *function_list)
drop_func.pack(pady=2)


def update_custom_function(event):

    custom_func= function_entry.get()
    clicked_func.set(custom_func)

function_entry.bind("<FocusOut>", update_custom_function)

#generate audio button
generate_button =Button(f_frame, text="Generate .wav File", command=generate_audio,bg="#ADD8E6")
generate_button.pack(pady=10)

root.mainloop()