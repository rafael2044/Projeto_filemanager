from customtkinter import CTk, CTkFrame, CTkButton, CTkCheckBox

def open_menu():
    p_x,p_y = root.menu.rootx(), root.menu.winfo_rooty()
    frame_menu = CTkFrame(root)
    print(root.menu.winfo_rootx(), root.menu.winfo_rooty())
    frame_menu.place()

    

root = CTk()

root.geometry('800x500')
root.menu = CTkButton(root, text='Menu', command=open_menu)
root.menu.pack()
root.mainloop()