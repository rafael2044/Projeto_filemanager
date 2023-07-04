from tkinter import StringVar, X, BOTH, RIGHT, LEFT, Y, END, W, Menu, E, messagebox, BOTTOM
from tkinter.ttk import Style, Treeview, Scrollbar, Menubutton
import os
import shutil
import datetime as dt
from PIL import Image, ImageTk
from pathlib import Path
from hurry.filesize import alternative, size as sz
from customtkinter import CTk, CTkEntry, CTkLabel, CTkButton, CTkFrame, CTkFont, CTkScrollbar


class App(CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry('1100x900')
        self.title('Filemanager')
        self.configure(bg='#121111')
        self.loader_main_frame()
        
        self.mainloop()
    
    def loader_main_frame(self):
        #Icons
        self.icons = {'File folder': ImageTk.PhotoImage(Image.open('icons/folder.png')),
                      '.png':ImageTk.PhotoImage(Image.open('icons/arquivo-png.png')),
                      '.bin':ImageTk.PhotoImage(Image.open('icons/bin.png')),
                      '.deb':ImageTk.PhotoImage(Image.open('icons/deb.png')),
                      '.py':ImageTk.PhotoImage(Image.open('icons/py.png')),
                      '.jpg':ImageTk.PhotoImage(Image.open('icons/arquivo-jpg.png'))}
        self.icon_search = ImageTk.PhotoImage(Image.open('icons/search.png'),)
        self.icon_return = ImageTk.PhotoImage(Image.open('icons/turn-back.png'))
        
        #Style
        self.style = Style()
        self.style.configure('Treeview.Heading', font=('Roboto Slab', 15, 'bold'), background='#939393', foreground='black',
                             padding=(10,2))
        self.style.configure('Treeview', font=('Roboto Slab', 13), rowheight=40, background='#242323', foreground='white',
                             padding=(10,5), )
        self.style.layout('Treeview', [('Treeview.theearea', {'sticky':'nswe'})])
        self.label_font = CTkFont(family='Roboto Slab', size=18, weight='bold')
        self.entry_font = CTkFont(family='Roboto Slab', size=18)
        self.style.configure('TMenu.tk_popup', background='black')
        self.style.configure('TMenubutton', foreground='black', font=('Roboto Slab', 15), background="#1f538d", padding=5, width=3)
        #Variables
        self.current_path = Path('/')
        self.hidden_folder = StringVar()
        self.hidden_folder.set('off')
        self.copy_file_name = ''
        self.current_path_copy_file = ''
        #Frames
        self.f_main = CTkFrame(self, corner_radius=25)
        self.f_browser = CTkFrame(self.f_main, height=50, fg_color='transparent')
        self.f_browser_files=CTkFrame(self.f_main, fg_color='transparent')
        self.f_info = CTkFrame(self.f_browser, height=30)
        self.f_search = CTkFrame(self.f_browser, height=20)
        self.f_current_path = CTkFrame(self.f_search, height=20, fg_color='transparent')
        
        #menu right click
        self.f_browser_files.menu = Menu(self.f_browser_files, tearoff=0, font=('Roboto Slab', 12), activeborderwidth=2, bd=2)
        self.f_browser_files.menu.add_command(label='Copy', command=self.copy)
        self.f_browser_files.menu.add_command(label='Paste', command=self.paste_file)
        self.f_browser_files.menu.add_command(label='Delete', command=self.delete)
        
        #Treeview
        self.tview_files = Treeview(self.f_browser_files, columns=['#01', '#02', '#03','#04'], show='tree headings',
                                    selectmode='extended')
        self.tview_files.heading('#01', text='Name', anchor=W)
        self.tview_files.heading('#02', text='Date Modified', anchor=W)
        self.tview_files.heading('#03', text='Type', anchor=W)
        self.tview_files.heading('#04', text='Size', anchor=W)
        self.tview_files.column('#0', width=30)
        self.tview_files.column('#01', width=500)
        self.tview_files.column('#02', width=150)
        self.tview_files.column('#03', width=80)
        self.tview_files.column('#04', width=80)
        
        #Scrollbar
        self.scrollbar_y = CTkScrollbar(self.f_browser_files, orientation='vertical', command=self.tview_files.yview)
        self.scrollbar_x = CTkScrollbar(self.f_browser_files, orientation='horizontal', command=self.tview_files.xview)
        self.tview_files.configure(yscroll=self.scrollbar_y.set, xscroll=self.scrollbar_x.set)
        
        #Pack Widgets
        self.f_main.pack(expand=True, fill=BOTH, padx=10, pady=10)
        self.f_browser.pack(fill=X, padx=10, pady=10)
        self.f_browser_files.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.f_info.pack(fill=X, padx=10, pady=5)
        self.f_search.pack(fill=X, padx=10, pady=5)
        self.f_current_path.pack(fill=X, padx=10, pady=5)
        self.scrollbar_x.pack(side=BOTTOM, fill=X)
        self.tview_files.pack(expand=True, fill=BOTH, side=LEFT)
        self.scrollbar_y.pack(side=RIGHT, fill=Y)
        
        #Loads frame widgets
        self.loader_info_widgets()
        self.loader_search_widgets()
        
        #Loads Files and Folders
        self.loader_files()
        
    def menu(self, event):
        try:
            self.f_browser_files.menu.tk_popup(event.x_root, event.y_root)
            row = self.tview_files.selection()
            if len(row) >=1:
                self.copy_file_name = self.tview_files.item(row[0]).get('values')[0]
        finally:
            self.f_browser_files.menu.grab_release()
            self.f_browser_files.menu.bind('<FocusOut>', self.exit_menu)
    
    def exit_menu(self, event):
        self.f_browser_files.menu.unpost()
    
    def copy(self):
        if self.copy_file_name != '':
            self.current_path_copy_file = Path(self.current_path, self.copy_file_name)
            self.verific_paste()
   
    def verific_paste(self):
        if self.current_path_copy_file != '' and Path.exists(self.current_path_copy_file):
            self.f_browser_files.menu.entryconfig('Paste', state='normal')
        else:
            self.f_browser_files.menu.entryconfig('Paste', state='disabled')
    
    def paste_file(self):
        if self.current_path_copy_file != '' and Path.exists(self.current_path_copy_file) and Path.is_file(self.current_path_copy_file):
            #Corrigir essa parte da copia de arquivos existentes
            if Path.exists(Path(self.current_path, self.copy_file_name)):
                file_name = self.copy_file_name.split('.')
                if file_name[0][-1] in '123456789':
                    new_name = f'{file_name[0][:-1]}{int(file_name[0][-1])+1}.{file_name[1]}'
                if file_name[0][-1] != '1':
                    new_name = f'{file_name[0]}1.{file_name[1]}'
                shutil.copy(Path(self.current_path, self.copy_file_name), Path(self.current_path, new_name))
            else:
                shutil.copy(self.current_path_copy_file, self.current_path)
        if Path.is_dir(self.current_path_copy_file):
            shutil.copytree(self.current_path_copy_file, Path(self.current_path, self.copy_file_name), copy_function=shutil.copy)
        self.loader_files() 
        
    def delete(self):   
        file = Path(self.current_path, self.copy_file_name)
        if Path.exists(file):
            if Path.is_file(file):
                confirmation = messagebox.askyesno(title='Delete Alert',
                                       message='do you want to delete the file?')
                if confirmation:
                    os.remove(file)
            if Path.is_dir(file):
                confirmation = messagebox.askyesno(title='Delete Alert',
                                                   message="Do you want to delete the directory? (Subdirectories will also be excluded)")
                if confirmation:
                    shutil.rmtree(file, ignore_errors=True)
                    
            self.copy_file_name = ''
            self.current_path_copy_file = ''
            self.loader_files()
   
    def loader_files(self):
        #Loads Files and Folders from current Path
        files = sorted(os.listdir(self.current_path), reverse=True)
        if self.hidden_folder.get() == 'off':
            files = filter(lambda x: x[0] != '.', files)
        
        self.tview_files.delete(*self.tview_files.get_children())
        if self.current_path != Path('/'):
            self.tview_files.insert('', END, values=('...'), image=self.icon_return)
        for file in files:
            stat_file = os.stat(Path(self.current_path, file))
            extension_file = Path(self.current_path, file).suffix
            date_modified = dt.datetime.fromtimestamp(stat_file.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            size = sz(stat_file.st_size, system=alternative)
            if '' == extension_file:
                extension_file = 'File folder'
            if extension_file in self.icons:
                self.tview_files.insert('',END, values=(file, date_modified, extension_file, size), image=self.icons[extension_file])
            else: 
                self.tview_files.insert('',END, values=(file, date_modified, extension_file, size))
        self.loader_current_path()
        self.tview_files.bind('<Double-1>', self.loader_next_folder)
        self.tview_files.bind('<Button-3>', self.menu)
        self.tview_files.bind('<Return>', self.loader_next_folder)
        self.verific_paste()
    
    def loader_next_folder(self, event):
        #Loader files and folders of next folder    
        folder = self.tview_files.selection()
        if len(folder) == 1:
            folder = self.tview_files.item(folder[0])['values'][0]
            if folder != '...' and Path.is_dir(Path(self.current_path, folder)):
                self.current_path = Path(self.current_path, folder)
            if folder == '...':
                self.current_path = self.current_path.parent
            self.loader_files()
    
    def loader_info_widgets(self):
        #Loads disks and sourcer dir
        if list(os.uname())[0] == 'Linux':
            user = list(os.popen('whoami'))[0].rsplit('\n')[0]
            source = Path('/')
            discs = os.listdir(f'/media/{user}')
            CTkButton(self.f_info, text=source, command= lambda : self.loader_file_disc(source)).pack(side=LEFT, padx=10, pady=10)
            [CTkButton(self.f_info, text=discs[x], 
                        command= lambda x=x: self.loader_file_disc(Path(f'/media/{user}', discs[x])))
            .pack(side=LEFT, padx=10, pady=10) for x in range(len(discs))]
            
    def loader_file_disc(self, path):
        #Loads disks and files on disk
        self.current_path = path
        self.loader_files()
    
    def loader_current_path(self):
        #Loads current path and menu into information frame
        [x.destroy() for x in self.f_current_path.winfo_children()]
        CTkLabel(self.f_current_path, text=self.current_path, font=self.label_font).pack(anchor=W, side=LEFT)
        self.f_current_path.menubutton_1 = Menubutton(self.f_current_path, text='...', style='TMenubutton',width=2)
        self.f_current_path.menubutton_1.menu = Menu(self.f_current_path.menubutton_1, tearoff=0, font=('Roboto Slab', 14), background='white', borderwidth=2)
        self.f_current_path.menubutton_1['menu'] = self.f_current_path.menubutton_1.menu
        self.f_current_path.menubutton_1.menu.add_checkbutton(label='Hidden Folders', onvalue='on',
                                                              offvalue='off', variable=self.hidden_folder, command=self.loader_files)
        self.f_current_path.menubutton_1.pack(anchor=E)
          
    def loader_search_widgets(self):
        #Loads search frame widgets
        self.search = CTkEntry(self.f_search, font=self.entry_font, height=40)
        self.search.pack(side=LEFT, fill=X, expand=True, padx=10, pady=10)
        CTkButton(self.f_search, text='', image=self.icon_search, command=self.search_file,
                  width=30, fg_color='transparent').pack(side=RIGHT, padx=10, pady=10)
        self.search.bind('<Return>', self.search_file)
        
    def search_file(self, event=None):
        #Upload files with searched name
        file_name = self.search.get()
        current_path = self.current_path
        print(file_name, current_path)
        self.tview_files.delete(*self.tview_files.get_children())
        self.tview_files.insert('', END, values='...', image=self.icon_return)
        for file in os.listdir(Path(current_path)):
            if file_name in file:
                stat_file = os.stat(Path(self.current_path, file))
                extension_file = Path(self.current_path, file).suffix
                date_modified = dt.datetime.fromtimestamp(stat_file.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
                size = sz(stat_file.st_size, system=alternative)
                if '' == extension_file:
                    extension_file = 'File folder'
                if extension_file in self.icons:
                    self.tview_files.insert('',END, values=(file, date_modified, extension_file, size), image=self.icons[extension_file])
                else: 
                    self.tview_files.insert('',END, values=(file, date_modified, extension_file, size))

App()