import tkinter as tk
from tkinter import ttk
import os
import datetime as dt
from PIL import Image, ImageTk
from pathlib import Path
from hurry.filesize import alternative, size as sz



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.geometry('1100x900')
        self.title('Gerenciador de Arquivos')
        self.configure(bg='#121111')
        self.loader_main_frame()
        
        self.mainloop()
    
    def loader_main_frame(self):
        self.icons = {'File folder': ImageTk.PhotoImage(Image.open('icons/folder.png')),
                      '.png':ImageTk.PhotoImage(Image.open('icons/picture.png'))}
        self.style = ttk.Style()
        self.style.configure('Treeview.Heading', font=('Roboto Slab', 15, 'bold'), background='#858585', foreground='white')
        self.style.configure('Treeview', font=('Roboto Slab', 13), rowheight=40, background='#242323', foreground='white')
        self.style.layout('Treeview', [('Treeview.theearea', {'sticky':'nswe'})])
        self.style.configure('TButton', font=('Roboto Slab', 15, 'bold'))
        self.style.configure('TLabel', font=('Roboto Slab', 15, 'bold'))
        print(self.style.theme_names())
        
        
        self.current_path = Path('/')
        self.hidden_folder = tk.StringVar()
        self.hidden_folder.set('off')
        
        self.f_main = tk.Frame(self, bg='#121111')
        self.f_browser = tk.Frame(self.f_main, bg='#242323', height=200)
        self.f_browser_files=tk.Frame(self.f_main, bg='#242323')
        self.f_info = tk.Frame(self.f_browser, bg='#242323', height=50)
        self.f_search = tk.Frame(self.f_browser, bg='#242323')
        self.f_current_path = tk.Frame(self.f_search, bg='#242323')
        self.tview_files = ttk.Treeview(self.f_browser_files, columns=['#01', '#02', '#03','#04'], show='tree headings')
        self.tview_files.heading('#01', text='Name', anchor=tk.W)
        self.tview_files.heading('#02', text='Date Modified', anchor=tk.W)
        self.tview_files.heading('#03', text='Type', anchor=tk.W)
        self.tview_files.heading('#04', text='Size', anchor=tk.W)
        self.tview_files.column('#0', width=30)
        self.tview_files.column('#01', width=500)
        self.tview_files.column('#02', width=150)
        self.tview_files.column('#03', width=80)
        self.tview_files.column('#04', width=80)

        self.scrollbar = tk.Scrollbar(self.f_browser_files, orient='vertical', command=self.tview_files.yview, width=20)
        self.tview_files.configure(yscroll=self.scrollbar.set)
        
        
        
        self.f_main.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.f_browser.pack(fill=tk.X, padx=10, pady=10, expand=True)
        self.f_browser_files.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.f_info.pack(expand=True, fill=tk.X, padx=10, pady=5)
        self.f_search.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.f_current_path.pack(expand=True, fill=tk.X, padx=10, pady=5)
        self.tview_files.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.loader_info_widgets()
        self.loader_search_widgets()
        self.loader_files()
        
    def loader_files(self):
        
        files = sorted(os.listdir(self.current_path), reverse=True)
        if self.hidden_folder.get() == 'off':
            files = filter(lambda x: x[0] != '.', files)
            
        self.tview_files.delete(*self.tview_files.get_children())
        if self.current_path != Path('/'):
            self.tview_files.insert('', tk.END, values=('...'))
        for file in files:
            stat_file = os.stat(Path(self.current_path, file))
            extension_file = Path(self.current_path, file).suffix
            date_modified = dt.datetime.fromtimestamp(stat_file.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            size = sz(stat_file.st_size, system=alternative)
            if '' == extension_file:
                extension_file = 'File folder'
            if extension_file in self.icons:
                self.tview_files.insert('',tk.END, values=(file, date_modified, extension_file, size), image=self.icons[extension_file])
            else: 
                self.tview_files.insert('',tk.END, values=(file, date_modified, extension_file, size))
        self.loader_current_path()
        self.tview_files.bind('<<TreeviewSelect>>', self.loader_next_folder)
    
    def loader_next_folder(self, event):
        
        folder = self.tview_files.selection()
        if len(folder) == 1:
            folder = self.tview_files.item(folder[0])['values'][0]
            if folder != '...' and Path.is_dir(Path(self.current_path, folder)):
                self.current_path = Path(self.current_path, folder)
            if folder == '...':
                self.current_path = self.current_path.parent
            self.loader_files()
    
    def loader_info_widgets(self):
        if list(os.uname())[0] == 'Linux':
            user = list(os.popen('whoami'))[0].rsplit('\n')[0]
            source = Path('/')
            discs = os.listdir(f'/media/{user}')
            ttk.Button(self.f_info, text=source, command= lambda : self.loader_file_disc(source)).pack(side=tk.LEFT, padx=10, pady=10)
            [ttk.Button(self.f_info, text=discs[x], 
                        command= lambda x=x: self.loader_file_disc(Path(f'/media/{user}', discs[x])))
            .pack(side=tk.LEFT, padx=10, pady=10) for x in range(len(discs))]
    def loader_file_disc(self, path):
        self.current_path = path
        self.loader_files()
    def loader_current_path(self):
        [x.destroy() for x in self.f_current_path.winfo_children()]
        ttk.Label(self.f_current_path, text=self.current_path, background='#242323', foreground='white').pack(anchor=tk.W, side=tk.LEFT)
        mb = tk.Menubutton(self.f_current_path, text='...', width=5, relief=tk.RAISED)
        self.f_current_path.menubutton_1 = tk.Menubutton(self.f_current_path, text='...', relief=tk.RAISED)
        self.f_current_path.menubutton_1.menu = tk.Menu(self.f_current_path.menubutton_1, tearoff=0)
        self.f_current_path.menubutton_1['menu'] = self.f_current_path.menubutton_1.menu
        self.f_current_path.menubutton_1.menu.add_checkbutton(label='Hidden Folders', onvalue='on',
                                                              offvalue='off', variable=self.hidden_folder, command=self.loader_files)
        self.f_current_path.menubutton_1.pack(anchor=tk.E)
          
    def loader_search_widgets(self):
        self.search = ttk.Entry(self.f_search)
        self.search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        ttk.Button(self.f_search, text='search').pack(side=tk.RIGHT, padx=10, pady=10)
        
App()