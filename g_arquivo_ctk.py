from tkinter import StringVar, X, BOTH, RIGHT, LEFT, Y, END, W, Menu, E, messagebox, BOTTOM
from tkinter.ttk import Style, Treeview, Menubutton
import os
import shutil
import datetime as dt
from PIL import ImageTk
from pathlib import Path
from hurry.filesize import alternative, size as sz
from customtkinter import CTk, CTkEntry, CTkLabel, CTkButton, CTkFrame, CTkFont, CTkScrollbar, CTkToplevel
from icons import *
from base64 import b64decode
from operator import itemgetter


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
        self.icons = {'File folder': ImageTk.PhotoImage(data=b64decode(folder)),
                      '.png':ImageTk.PhotoImage(data=b64decode(png)),
                      '.bin':ImageTk.PhotoImage(data=b64decode(bin)),
                      '.deb':ImageTk.PhotoImage(data=b64decode(deb)),
                      '.py':ImageTk.PhotoImage(data=b64decode(py)),
                      '.jpg':ImageTk.PhotoImage(data=b64decode(jpg))}
        self.icon_search = ImageTk.PhotoImage(data=b64decode(search))
        self.icon_return = ImageTk.PhotoImage(data=b64decode(icon_return))
        
        #Style
        self.style = Style()
        self.style.configure('Treeview.Heading', font=('Roboto Slab', 15, 'bold'), background='#939393', foreground='black',
                             padding=(10,2))
        self.style.configure('Treeview', font=('Roboto Slab', 13), rowheight=40, background='#242323', foreground='white',
                             padding=(10,5), )
        self.style.layout('Treeview', [('Treeview.theearea', {'sticky':'nswe'})])
        self.style.configure('TMenu.tk_popup', background='black')
        self.style.configure('TMenubutton', foreground='black', font=('Roboto Slab', 15), background="#1f538d", padding=5, width=3)
        
        
        #Fonts
        self.label_font = CTkFont(family='Roboto Slab', size=18, weight='bold')
        self.entry_font = CTkFont(family='Roboto Slab', size=18)
        self.button_font = CTkFont(family='Roboto Slab', size=15, weight='bold')
        
        #Variables
        self.current_path = Path('/')
        self.hidden_folder = StringVar()
        self.hidden_folder.set('off')
        self.flag_cut = False
        self.file_name_selected = ''
        self.current_copy_path = ''
        
        #flag sort
        self.flag_sort = False
        
        
        #Frames
        self.f_main = CTkFrame(self, corner_radius=25)
        self.f_browser = CTkFrame(self.f_main, height=50, fg_color='transparent')
        self.f_browser_files=CTkFrame(self.f_main, fg_color='transparent')
        self.f_info = CTkFrame(self.f_browser, height=30)
        self.f_search = CTkFrame(self.f_browser, height=20)
        self.f_current_path = CTkFrame(self.f_search, height=20, fg_color='transparent')
        
        #Context Menu
        self.f_browser_files.context_menu = Menu(self.f_browser_files, tearoff=0, font=('Roboto Slab', 12), activeborderwidth=2, bd=2)

        #Treeview
        self.columns_name = ['Name', 'Date Modified', 'Type', 'Size' ]
        self.tview_files = Treeview(self.f_browser_files, columns=['#01', "#02", "#03", "#04"], show='tree headings',
                                    selectmode='extended')
        
        self.tview_files.heading('#01',text=self.columns_name[0], anchor=W)
        self.tview_files.heading('#02',text= self.columns_name[1], anchor=W)
        self.tview_files.heading('#03', text=self.columns_name[2], anchor=W)
        self.tview_files.heading('#04', text=self.columns_name[3], anchor=W)
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
        self.load_info_widgets()
        self.load_search_widgets()
        
        #Loads Files and Folders
        self.get_all_files()
        
    def context_menu(self, event):
        context_menu_file = {'Open':'', 'Rename':self.window_rename, 'Copy':self.copy, 'Cut':self.cut, 'separator':1,
                             'Delete':self.delete}
        context_menu = {'Paste':self.to_paste, 'separator':1, 'Create new':{'Folder': self.window_creation_folder, 'File': ''}}
        try:
            if len(self.tview_files.selection()) == 1:
                for name, command in context_menu_file.items():
                    if name == 'separator':
                        self.f_browser_files.context_menu.add_separator()
                    else:
                        self.f_browser_files.context_menu.add_command(label=name, command=command)
                        
                self.check_copy()
                self.check_delete_option()
            else:
                for name, command in context_menu.items():
                    if name == 'separator':
                        self.f_browser_files.context_menu.add_separator()
                    elif name == 'Create new':
                        cascade_menu = Menu(self.f_browser_files, font=('Roboto Slab', 12), activeborderwidth=2, bd=2)
                        for n, c in context_menu[name].items():
                            cascade_menu.add_command(label=n, command=c)
                        self.f_browser_files.context_menu.add_cascade(label=name, menu=cascade_menu)
                    else:
                        self.f_browser_files.context_menu.add_command(label=name, command=command)
                self.check_paste_option()
            self.f_browser_files.context_menu.tk_popup(event.x_root, event.y_root)
            
        finally:
            self.f_browser_files.context_menu.grab_release()
            #self.check_creation_menu_options()
            self.f_browser_files.context_menu.bind('<FocusOut>', self.close_context_menu)
        
    def close_context_menu(self, event):
        self.f_browser_files.context_menu.unpost()
        self.f_browser_files.context_menu.delete(0, END)
    
    def copy(self):
        if self.file_name_selected != '':
            self.current_copy_path = Path(self.current_path, self.file_name_selected)
            self.file_name_copy = self.file_name_selected
            #self.check_paste_option()
   
    def cut(self):
        self.copy()
        self.flag_cut = True
        
    def get_selectect_file_name(self, event):
        try:
            self.file_name_selected = self.tview_files.item(self.tview_files.selection()[0]).get('values')[0]
        except IndexError as e:
            pass
        
    def check_copy(self):
        if len(self.tview_files.selection()) < 1:
            self.f_browser_files.context_menu.entryconfig('Copy', state='disabled')
        else:
            self.f_browser_files.context_menu.entryconfig('Copy', state='normal')
            
    def check_paste_option(self):
        if self.current_copy_path != '' and Path.exists(self.current_copy_path):
            self.f_browser_files.context_menu.entryconfig('Paste', state='normal')
        else:
            self.f_browser_files.context_menu.entryconfig('Paste', state='disabled')
    
    def check_creation_menu_options(self):
        if Path.owner(self.current_path) != str(Path.home()).split('/')[-1]:
            self.f_browser_files.context_menu_create.entryconfig('Folder', state = 'disabled')
            self.f_browser_files.context_menu_create.entryconfig('File', state = 'disabled')
        else:
            self.f_browser_files.context_menu_create.entryconfig('Folder', state = 'normal')
            self.f_browser_files.context_menu_create.entryconfig('File', state = 'normal')
        
    def check_delete_option(self):
        if Path.owner(self.current_path) == str(Path.home()).split('/')[-1] and len(self.tview_files.selection()) == 1:
            self.f_browser_files.context_menu.entryconfig('Delete', state='normal')
        else:
            self.f_browser_files.context_menu.entryconfig('Delete', state='disabled')

    def to_paste(self):
        if Path.exists(self.current_copy_path) and Path.is_file(self.current_copy_path):
            #Corrigir essa parte da copia de arquivos existentes
            if Path.exists(Path(self.current_path, self.file_name_copy)):
                file_name = self.file_name_copy.split('.')
                if file_name[0][-1] in '123456789':
                    new_name = f'{file_name[0][:-1]}{int(file_name[0][-1])+1}.{file_name[1]}'
                if file_name[0][-1] != '1':
                    new_name = f'{file_name[0]}1.{file_name[1]}'
                shutil.copy(Path(self.current_path, self.file_name_copy), Path(self.current_path, new_name))
            else:
                if self.flag_cut:
                    shutil.move(self.current_copy_path, self.current_path)
                    self.flag_cut = not self.flag_cut
                else:
                    shutil.copy(self.current_copy_path, self.current_path)
        if Path.is_dir(self.current_copy_path):
            if self.flag_cut:
                shutil.move(self.current_copy_path, self.current_path, copy_function=shutil.move)
            else:
                shutil.copytree(self.current_copy_path, Path(self.current_path, self.file_name_copy), copy_function=shutil.copy)
        self.upload_files() 
        
    def delete(self):   
        file = Path(self.current_path, self.file_name_selected)
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
                    
            self.file_name_selected = ''
            self.current_copy_path = ''
            self.upload_files()
   
    def window_creation_folder(self):
        def create_folder():
            Path(self.current_path, window.name_folder.get()).mkdir(exist_ok=True)
            window.name_folder.delete(0, END)
            self.upload_files()
            window.destroy()
            
        window = CTkToplevel(self)
        window.title("New Folder - Filemanager")
        window.geometry('500x100')
        window.resizable(False, False)
        
        window.name_folder = CTkEntry(window, placeholder_text='enter the name of the folder', font=self.entry_font)
        window.f_button = CTkFrame(window, fg_color='transparent')
        
        window.b_ok = CTkButton(window.f_button, text='Ok', font=self.button_font, command=create_folder)
        window.b_cancel = CTkButton(window.f_button, text='Cancel', command=window.destroy, font=self.button_font)
        
        window.name_folder.pack(padx=10, fill=X, pady=15)
        window.f_button.pack(fill=X, padx=10)
        window.b_ok.pack(side=LEFT, padx=30, fill=X, expand=True)
        window.b_cancel.pack(side=RIGHT, padx=25, fill=X, expand=True)

        window.focus_force()
        window.grab_set()
        window.bind('WM_DELETE_WINDOW', window.destroy)
        window.mainloop()
           
    def window_rename(self):
        def rename():
            if self.file_name_selected != '':
            
                self.current_copy_path = Path(self.current_path, self.file_name_selected)
                extension = Path(self.current_copy_path).suffix
                new_name = window.new_name.get()
                if extension != '':
                    new_name = new_name + extension
                Path.rename(self.current_copy_path, Path(self.current_path, new_name))
                self.current_copy_path = ''
                self.file_name_selected = ''
                self.upload_files()
                window.destroy()
            
        window = CTkToplevel(self)
        window.title("Rename - Filemanager")
        window.geometry('500x100')
        window.resizable(False, False)
        
        window.new_name = CTkEntry(window, placeholder_text='enter the new name', font=self.entry_font)
        window.f_button = CTkFrame(window, fg_color='transparent')
        
        window.b_ok = CTkButton(window.f_button, text='Ok', font=self.button_font, command=rename)
        window.b_cancel = CTkButton(window.f_button, text='Cancel', command=window.destroy, font=self.button_font)
        
        window.new_name.pack(padx=10, fill=X, pady=15)
        window.f_button.pack(fill=X, padx=10)
        window.b_ok.pack(side=LEFT, padx=30, fill=X, expand=True)
        window.b_cancel.pack(side=RIGHT, padx=25, fill=X, expand=True)

        window.focus_force()
        window.grab_set()
        window.bind('WM_DELETE_WINDOW', window.destroy)
        window.mainloop()   
         
    def upload_files(self):
        self.tview_files.delete(*self.tview_files.get_children())
        if self.current_path != Path('/'):
             self.tview_files.insert('', END, values='...')
        for file in self.list_all_files:
            if file['icon'] != None:
                self.tview_files.insert('',END, values=(file['name'], file['date'], file['extension'], 
                                                        file['size']), image=file['icon'])
            else: 
                self.tview_files.insert('',END, values=(file['name'], file['date'], file['extension'], 
                                                        file['size']))

        self.load_current_path()
        self.tview_files.bind('<<TreeviewSelect>>', self.get_selectect_file_name)
        self.tview_files.bind('<Button-1>', self.sort_files)
        self.tview_files.bind('<Double-1>', self.load_next_files)
        self.tview_files.bind('<Button-3>', self.context_menu)
        self.tview_files.bind('<Return>', self.load_next_files)
             
    def get_all_files(self):
        all_files = os.listdir(self.current_path)
        if self.hidden_folder.get() == 'off':
            all_files = filter(lambda x: x[0] != '.', all_files)
        self.list_all_files = []
            
        for file in all_files:
            stat_file = os.stat(Path(self.current_path, file))
            extension_file = Path(self.current_path, file).suffix
            date_modified = dt.datetime.fromtimestamp(stat_file.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            size = sz(stat_file.st_size, system=alternative)
            if '' == extension_file:
                extension_file = 'File folder'
            if extension_file in self.icons:
                self.list_all_files.append({'name': file, 'date':date_modified, 'extension':extension_file,'size':size, 'icon':self.icons[extension_file]})
            else:
                self.list_all_files.append({'name': file,'date':date_modified, 'extension':extension_file,'size':size, 'icon':None})  
    
        self.upload_files()
    def sort_files(self, event):
        region = self.tview_files.identify('region', event.x, event.y)
        if region == 'heading':
            column = self.tview_files.identify_column(event.x) 
            sort_by = self.tview_files.heading(column)['text']
            if sort_by in self.columns_name:
                if sort_by == self.columns_name[0]:
                    self.sort_by_name()
                elif sort_by == self.columns_name[1]:
                    self.sort_by_date_modified()
                elif sort_by == self.columns_name[2]:
                    self.sort_by_type()
                elif sort_by == self.columns_name[3]:
                    self.sort_by_size()
                self.upload_files()
                self.flag_sort = not self.flag_sort
    def sort_by_name(self):
        self.list_all_files.sort(key=itemgetter('name'), reverse=self.flag_sort)
    
    
    def sort_by_date_modified(self):
        self.list_all_files.sort(key=itemgetter('date'), reverse=self.flag_sort)
        
    def sort_by_type(self):
        self.list_all_files.sort(key=itemgetter('extension'), reverse=self.flag_sort)
    
    def sort_by_size(self):
        self.list_all_files.sort(key=itemgetter('size'), reverse=self.flag_sort)
        
    def load_next_files(self, event):
        #Loader files and folders of next folder    
        folder = self.tview_files.selection()
        if len(folder) == 1:
            folder = self.tview_files.item(folder[0])['values'][0]
            if folder != '...' and Path.is_dir(Path(self.current_path, folder)):
                self.current_path = Path(self.current_path, folder)
            if folder == '...':
                self.current_path = self.current_path.parent
            self.get_all_files()
    
    def load_info_widgets(self):
        #Loads disks and sourcer dir
        if list(os.uname())[0] == 'Linux':
            user = list(os.popen('whoami'))[0].rsplit('\n')[0]
            source = Path('/')
            discs = os.listdir(f'/media/{user}')
            CTkButton(self.f_info, text=source, command= lambda : self.load_file_from_disk(source)).pack(side=LEFT, padx=10, pady=10)
            [CTkButton(self.f_info, text=discs[x], 
                        command= lambda x=x: self.load_file_from_disk(Path(f'/media/{user}', discs[x])))
            .pack(side=LEFT, padx=10, pady=10) for x in range(len(discs))]
            
    def load_file_from_disk(self, path):
        #Loads disks and files on disk
        self.current_path = path
        self.get_all_files()
    
    def load_current_path(self):
        #Loads current path and menu into information frame
        [x.destroy() for x in self.f_current_path.winfo_children()]
        CTkLabel(self.f_current_path, text=self.current_path, font=self.label_font).pack(anchor=W, side=LEFT)
        #Alterar menu de opcoes
        self.f_current_path.menubutton_1 = Menubutton(self.f_current_path, text='...', style='TMenubutton',width=2)
        self.f_current_path.menubutton_1.menu = Menu(self.f_current_path.menubutton_1, tearoff=0, font=('Roboto Slab', 14), background='white', borderwidth=2)
        self.f_current_path.menubutton_1['menu'] = self.f_current_path.menubutton_1.menu
        self.f_current_path.menubutton_1.menu.add_checkbutton(label='Hidden Folders', onvalue='on',
                                                              offvalue='off', variable=self.hidden_folder, command=self.upload_files)
        self.f_current_path.menubutton_1.pack(anchor=E)
          
    def load_search_widgets(self):
        #Loads search frame widgets
        self.search = CTkEntry(self.f_search, font=self.entry_font, height=40)
        self.search.pack(side=LEFT, fill=X, expand=True, padx=10, pady=10)
        CTkButton(self.f_search, text='', image=self.icon_search, command=self.file_search,
                  width=30, fg_color='transparent').pack(side=RIGHT, padx=10, pady=10)
        self.search.bind("<KeyPress>", self.file_search)
        self.search.bind('<Return>', self.file_search)
        
    def file_search(self, event=None):
        #Upload files with searched name
        file_name = self.search.get()
        self.tview_files.delete(*self.tview_files.get_children())
        self.tview_files.insert('', END, values='...', image=self.icon_return)
        files = list(filter(lambda x: file_name in x['name'].lower(), self.list_all_files))
        self.tview_files.delete(self.tview_files.get_children())
        self.tview_files.insert('', END, values=('...'))
        for file in files:
            if file['icon'] != None:
                self.tview_files.insert('',END, values=(file['name'], file['date'], file['extension'], 
                                                        file['size']), image=file['icon'])
            else: 
                self.tview_files.insert('',END, values=(file['name'], file['date'], file['extension'], 
                                                        file['size']))

App()