from socket import *
from threading import *
from tkinter import *
from tkinter import filedialog
import os
from PIL import Image, ImageTk
import sys

clientSocket = socket(AF_INET, SOCK_DGRAM)

hostIp = 'localhost'
portNumber = 8901

clientIP = 'localhost'
clientPortNumber = 8900
client_addr = (clientIP, clientPortNumber)

clientSocket.bind((hostIp, portNumber))

window = Tk()
window.title("Connected To: "+ hostIp+ ":"+str(portNumber))

txtMessages = Text(window, width=60)
txtMessages.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

txtYourMessage = Entry(window, width=50)
txtYourMessage.insert(0,"Enter message")
txtYourMessage.grid(row=1, column=0, padx=10, pady=10)

def click(*args):
    txtYourMessage.delete(0, 'end')
  
def leave(*args):
    txtYourMessage.delete(0, 'end')
    txtYourMessage.insert(0, 'Your message ')
    window.focus()

txtYourMessage.bind("<Button-1>", click)

def sendMessage():
    clientMessage = txtYourMessage.get()
    clientSocket.sendto(clientMessage.encode("utf-8"), client_addr)
    if clientMessage == "END":
        os._exit(1)
    else:
        print(f"You : {clientMessage}")
        txtMessages.insert(END, "\n" + "You: "+ clientMessage)
        txtYourMessage.delete(0, END)
        

btnSendMessage = Button(window, text="Send", width=20, command=sendMessage)
btnSendMessage.grid(row=1, column=1, padx=10, pady=10)

window.bind("<Return>", lambda x: sendMessage())

def img_send(url): 
    clientSocket.sendto("!!!IMAGE".encode(), client_addr)
    clientSocket.sendto(url.split('.')[1].encode(), client_addr)
    file = open(url, 'rb')
    image_data = file.read(1024)
    while image_data:
        clientSocket.sendto(image_data, client_addr)
        image_data = file.read(1024)

    file.close()

def upload_file():
    global n
    f_types = [('Jpg Files', '*.jpg'), ('PNG Files','*.png')]
    filename = filedialog.askopenfilename(filetypes=f_types)
    print(filename.split('.')[1])
    image = Image.open(filename)
    img_resized = image.resize((200,100))
    img.append(ImageTk.PhotoImage(img_resized))
    txtMessages.insert(END, "\nYou : ")
    txtMessages.image_create(END, image = img[n])
    n += 1
    img_send(filename)

def display_image(file_path):
    print(file_path)
    global n
    my_image = Image.open(file_path)
    img_resized = my_image.resize((200,100)) 
    img.append(ImageTk.PhotoImage(img_resized))
    txtMessages.insert(END, "\nPeer : \n")
    # txtMessages.insert(END, "\n")
    txtMessages.image_create(END, image = img[n])
    n += 1

def recv_img(ext):
    global img_no
    filename = 'server_image' + str(img_no) +'.'  + ext
    img_no += 1
    file = open(filename, "wb")
    image_chunk = clientSocket.recv(1024) 
    while sys.getsizeof(image_chunk) == 1057:
        file.write(image_chunk)
        image_chunk = clientSocket.recv(1024)

    file.write(image_chunk)
    file.close()
    display_image(filename)

def recvMessage():
    while True:
        serverMessage, addr = clientSocket.recvfrom(1024)
        serverMessage = serverMessage.decode("utf-8")
        if serverMessage == "!!!IMAGE":
            serverMessage,addr = clientSocket.recvfrom(1024)
            recv_img(serverMessage.decode())
        elif serverMessage == "END":
            txtMessages.insert(END, '\n!! Peer Left !!')
        else:
            print(f"Peer : {serverMessage}")
            txtMessages.insert(END, "\n"+"Peer : "+serverMessage)

img_no = 1
n = 0
b1 = Button(window, text='Upload Images', width=20,command = lambda:upload_file())
b1.grid(row=3,column=0,columnspan=2, padx=10, pady=10)
img = []

recvThread = Thread(target=recvMessage)
recvThread.daemon = True
recvThread.start()

window.mainloop()
