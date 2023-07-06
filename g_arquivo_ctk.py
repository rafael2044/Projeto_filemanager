from tkinter import StringVar, X, BOTH, RIGHT, LEFT, Y, END, W, Menu, E, messagebox, BOTTOM, IntVar
from tkinter.ttk import Style, Treeview
from os import listdir, stat, remove, uname, popen
from os.path import isfile
from shutil import move, copy, copytree, rmtree
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
        self.load_widgets_main_windows()
        
        self.mainloop()
    
    def load_widgets_main_windows(self):
        #Icons
        self.icons = {'File folder': ImageTk.PhotoImage(data=b64decode(folder)),
                      'png':ImageTk.PhotoImage(data=b64decode(png)),
                      'bin':ImageTk.PhotoImage(data=b64decode(bin)),
                      'deb':ImageTk.PhotoImage(data=b64decode(deb)),
                      'py':ImageTk.PhotoImage(data=b64decode(py)),
                      'jpg':ImageTk.PhotoImage(data=b64decode(jpg))}
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
        print(self.style.theme_names())
        
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
        self.flag_sort_stats = IntVar()
        self.flag_sort_stats.set(0)
        self.flag_sort_stats_options = IntVar()
        self.flag_sort_stats_options.set(0)
        self.flag_sort_active = StringVar()
        self.flag_sort_active.set('Name')

        
        
        #Frames
        self.f_main = CTkFrame(self, corner_radius=25)
        self.f_browser = CTkFrame(self.f_main, height=50, fg_color='transparent')
        self.f_browser_files=CTkFrame(self.f_main, fg_color='transparent')
        self.f_info_folder = CTkFrame(self.f_browser_files, height=20, fg_color='transparent')
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
        self.f_info_folder.pack(side=BOTTOM, fill=X)
        self.scrollbar_x.pack(side=BOTTOM, fill=X)
        self.tview_files.pack(expand=True, fill=BOTH, side=LEFT)
        self.scrollbar_y.pack(side=RIGHT, fill=Y)
        
        #Loads frame widgets
        self.load_info_widgets()
        self.load_search_widgets()
        
        #Loads Files and Folders
        self.get_all_files()
        self.sort_files()
        
    def context_menu(self, event):
        context_menu_file = {'Open':'', 'Rename':self.window_rename, 'Copy':self.copy, 'Cut':self.cut, 'separator':1,
                             'Delete':self.delete}
        context_menu = {'Sort By':{'Name': 0 ,'Date Modified': 1,
                                   'Size':2, 'Type':3,
                                   'alternative':{'Name':{'A-Z': 0, 'Z-A': 1}, 
                                                       'Date Modified':{'Older':0, 'Newest': 1},
                                                       'Size':{'First the smallest':0, 'First the biggest':1},
                                                       'Type':{'A-Z':0, 'Z-A':1}}},
                        'Paste':self.to_paste, 'separator':1, 'Create new':{'Folder': self.window_creation_folder, 'File': ''}}
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
                        
                    elif name == 'Sort By':
                        cascade_menu = Menu(self.f_browser_files, font=('Roboto Slab', 12), activeborderwidth=2, bd=2)
                        for name_op_cascade, value in context_menu[name].items():
                            if name_op_cascade == 'alternative':
                                pass
                            else:
                                cascade_menu.add_radiobutton(label=name_op_cascade, var = self.flag_sort_stats, value=value, command= lambda x=name_op_cascade: self.flag_sort_active.set(x))
                        if self.flag_sort_stats.get() in [0,1,2,3]:
                            cascade_menu.add_separator()
                            for name_sort_options in context_menu[name]['alternative']:
                                if name_sort_options == self.flag_sort_active.get():
                                    for name_alt_sort_options, value_option in context_menu[name]['alternative'][name_sort_options].items():
                                        cascade_menu.add_radiobutton(label=name_alt_sort_options, var=self.flag_sort_stats_options ,value=value_option)        
                        self.f_browser_files.context_menu.add_cascade(label=name, menu=cascade_menu)
                        
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
            self.f_browser_files.context_menu.bind('<FocusOut>', self.close_context_menu)
        
    def close_context_menu(self, event):
        self.sort_files()
        self.f_browser_files.context_menu.delete(0, END)
        self.f_browser_files.context_menu.unpost()
    
    def copy(self):
        file = self.file_name_selected
        if file != '':
            self.current_copy_path = Path(self.current_path, file)
            self.file_name_copy = file
   
    def cut(self):
        self.copy()
        self.flag_cut = True
        
    def get_selectect_file_name(self, event):
        try:
            name, *_ = self.tview_files.item(self.tview_files.selection()[0]).get('values')
            if name != '...':
                file, *_ = list(filter(lambda x: x['name'] == name, self.list_all_files))
                self.full_name_selected_file = name
                if file['extension'] != 'File folder':
                    self.full_name_selected_file = f"{name}.{file['extension']}"
            self.file_name_selected = name
            
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
                copy(Path(self.current_path, self.file_name_copy), Path(self.current_path, new_name))
            else:
                if self.flag_cut:
                    move(self.current_copy_path, self.current_path)
                    self.flag_cut = not self.flag_cut
                else:
                    copy(self.current_copy_path, self.current_path)
        if Path.is_dir(self.current_copy_path):
            if self.flag_cut:
                move(self.current_copy_path, self.current_path, copy_function=move)
            else:
                copytree(self.current_copy_path, Path(self.current_path, self.file_name_copy), copy_function=copy)
        self.get_all_files()
        
    def delete(self):   
        file_name = self.file_name_selected
        full_file_name = self.full_name_selected_file
        
        file_path = Path(self.current_path, full_file_name)
        if file_path.exists():
            if file_path.is_dir():
                confirmation = messagebox.askyesno(title='Delete Alert',
                                                message="Do you want to delete the directory? (Subdirectories will also be excluded)")
                if confirmation:
                    rmtree(file_path, ignore_errors=True)
            if file_path.is_file():
                confirmation = messagebox.askyesno(title='Delete Alert',
                                    message='do you want to delete the file?')
                if confirmation:
                    remove(file_path)
                    
            self.list_all_files = list(filter(lambda x: x['name'] != file_name, self.list_all_files))
            self.sort_files()
   
    def window_creation_folder(self):
        def create_folder():
            folder = Path(self.current_path, window.name_folder.get())
            folder.mkdir(exist_ok=True)
            folder = stat(folder)
            
            self.list_all_files.append({'name':window.name_folder.get(), 'date':folder.st_mtime,
                                        'extension':'File folder', 'size': folder.st_size, 'icon':self.icons['File folder']})
            self.sort_files()
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
            full_name_file = self.full_name_selected_file
            file_name = self.file_name_selected
            
            file_path = Path(self.current_path, full_name_file)
            extension_file = file_path.suffix
            
            new_name_file = window.new_name.get()
            
            new_full_name_file = new_name_file
            if extension_file:
                new_full_name_file = new_name_file + extension_file
                
            new_file_path = Path(self.current_path, new_full_name_file)
            file_path.rename(new_file_path)
            
            file, *_ = list(filter(lambda x: x['name'] == file_name, self.list_all_files))
            file['name'] = new_name_file
            self.current_copy_path = ''
            self.sort_files()
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
         
    def upload_files(self, list_all_files):
        self.tview_files.delete(*self.tview_files.get_children())
        if self.current_path != Path('/'):
             self.tview_files.insert('', END, values='...')
        for file in list_all_files:
            if file['icon'] != None:
                self.tview_files.insert('',END, values=(file['name'], dt.datetime.fromtimestamp(file['date']).strftime('%d/%m/%Y %H:%M:%S'), file['extension'], 
                                                        sz(file['size'], system=alternative)), image=file['icon'])
            else: 
                self.tview_files.insert('',END, values=(file['name'], dt.datetime.fromtimestamp(file['date']).strftime('%d/%m/%Y %H:%M:%S'), file['extension'], 
                                                        sz(file['size'], system=alternative)))
        self.load_current_path()
        self.load_info_folder()
        self.tview_files.bind('<<TreeviewSelect>>', self.get_selectect_file_name)
        self.tview_files.bind('<Double-1>', self.load_next_files)
        self.tview_files.bind('<Button-3>', self.context_menu)
        self.tview_files.bind('<Return>', self.load_next_files)
             
    def get_all_files(self):
        all_files = listdir(self.current_path)
        if self.hidden_folder.get() == 'off':
            all_files = filter(lambda x: x[0] != '.', all_files)
        self.list_all_files = []
            
        for file in all_files:
            file_path = Path(self.current_path, file)
            if file_path.is_dir() or file_path.is_file():
                stat_file = stat(Path(self.current_path, file))
                if file[0] != '.':
                    extension_file = file[file.rfind('.')+1:] if file.rfind('.') !=  -1 else 'File folder'
                    file = file[:file.rfind('.')] if file.rfind('.') !=  -1 else file
                else:
                    extension_file = 'File folder'
                date_modified = stat_file.st_mtime
                size = stat_file.st_size
                if extension_file in self.icons:
                    self.list_all_files.append({'name': file, 'date':date_modified, 'extension':extension_file,'size':size, 'icon':self.icons[extension_file]})
                else:
                    self.list_all_files.append({'name': file,'date':date_modified, 'extension':extension_file,'size':size, 'icon':None})
    
        self.sort_files()
        
    def sort_files(self):
        if self.flag_sort_stats.get() in [0,1,2,3]:
            sort_by = self.flag_sort_active.get()
            option = self.flag_sort_stats_options.get()
            
            if sort_by == 'Name':
                if option:
                    self.sort_by_name_ZA()
                else:
                    self.sort_by_name_AZ()
            if sort_by == 'Date Modified':
                if option:
                    self.sort_by_date_modified_older()
                else:
                    self.sort_by_date_modified_newest()
            if sort_by == 'Size':
                if option:
                    self.sort_by_size_smaller()
                else:
                    self.sort_by_size_bigger()
            if sort_by == 'Type':
                if option:
                    self.sort_by_type_ZA()
                else:
                    self.sort_by_type_AZ()
        else:
            self.upload_files(self.list_all_files)
        
    def sort_by_name_AZ(self):
        list_sorted_all_files = sorted(self.list_all_files,key=lambda x: x['name'].lower())
        self.upload_files(list_sorted_all_files)
    
    def sort_by_name_ZA(self):
        list_sorted_all_files = sorted(self.list_all_files,key=lambda x: x['name'].lower(), reverse=True)
        self.upload_files(list_sorted_all_files)
    
    def sort_by_date_modified_older(self):
        list_sorted_all_files = sorted(self.list_all_files,key=itemgetter('date'), reverse=True)
        self.upload_files(list_sorted_all_files)
        
    def sort_by_date_modified_newest(self):
        list_sorted_all_files = sorted(self.list_all_files,key=itemgetter('date'))
        self.upload_files(list_sorted_all_files)
        
    def sort_by_type_ZA(self):
        list_sorted_all_files = sorted(self.list_all_files,key=lambda x: x['name'].lower(), reverse=True)
        self.upload_files(list_sorted_all_files)
        
    def sort_by_type_AZ(self):
        list_sorted_all_files = sorted(self.list_all_files,key=lambda x: x['name'].lower())
        self.upload_files(list_sorted_all_files)    
    
    def sort_by_size_bigger(self):
        list_sorted_all_files = sorted(self.list_all_files,key=itemgetter('size'))
        self.upload_files(list_sorted_all_files)
        
    def sort_by_size_smaller(self):
        list_sorted_all_files = sorted(self.list_all_files,key=itemgetter('size'), reverse=True)
        self.upload_files(list_sorted_all_files)
        
    def load_next_files(self, event):
        #Loader files and folders of next folder    
        folder = self.file_name_selected
        if folder != '':
            if folder != '...':
                path_folder = Path(self.current_path, folder)
                if path_folder.is_dir():
                    self.current_path = path_folder
            if folder == '...':
                self.current_path = self.current_path.parent
            self.get_all_files()    
    
    def load_info_widgets(self):
        #Loads disks and sourcer dir
        if list(uname())[0] == 'Linux':
            user = list(popen('whoami'))[0].rsplit('\n')[0]
            source = Path('/')
            path_discs = Path(f"/media/{user}")
            if not path_discs.exists():
                path_discs = Path(f"/run/media/{user}")
            discs = listdir(path_discs)

            CTkButton(self.f_info, text=source, command= lambda : self.load_file_from_disk(source)).pack(side=LEFT, padx=10, pady=10)
            [CTkButton(self.f_info, text=discs[x], 
                        command= lambda x=x: self.load_file_from_disk(Path(path_discs, discs[x])))
            .pack(side=LEFT, padx=10, pady=10) for x in range(len(discs))]
            
    def load_info_folder(self):
        [x.destroy() for x in self.f_info_folder.winfo_children()]
        count_file = 0
        count_folder = 0
        for element in self.list_all_files:
            element_type = element['extension']
            if element_type == 'File folder':
                count_folder+=1
            else:
                count_file+=1
        
        self.f_info_folder.count_folder_file = CTkLabel(self.f_info_folder, text=f'{count_folder} Folders, {count_file} Files', font=self.label_font)
        self.f_info_folder.count_folder_file.pack(side=LEFT)
            
    def load_file_from_disk(self, path):
        #Loads disks and files on disk
        self.current_path = path
        self.get_all_files()
    
    def load_current_path(self):
        #Loads current path and menu into information frame
        [x.destroy() for x in self.f_current_path.winfo_children()]
        CTkLabel(self.f_current_path, text=self.current_path, font=self.label_font).pack(anchor=W, side=LEFT)
        self.f_current_path.menu_options = Menu(self.f_current_path, tearoff=0, font=('Roboto Slab', 14), background='white', borderwidth=2)
        self.f_current_path.b_menu = CTkButton(self.f_current_path, text='...', font=self.button_font, command=self.load_menu_options, width=50, height=30)
        self.f_current_path.b_menu.pack(side=RIGHT, anchor=E)
        
    def load_menu_options(self):
        x, y = self.f_current_path.b_menu.winfo_rootx(), self.f_current_path.b_menu.winfo_rooty()
        options_menu = {'Create new':{'Create Folder': self.window_creation_folder}, 'Show Hidden Folders':self.get_all_files}
        for name_option, command_option in options_menu.items():
            if 'Hidden' in name_option:
                self.f_current_path.menu_options.add_checkbutton(label=name_option, command=command_option, variable=self.hidden_folder, onvalue='on', 
                                                                 offvalue='off')
            if name_option == 'Create new':
                cascade_menu = Menu(self.f_current_path.menu_options,font=('Roboto Slab', 14), background='white', borderwidth=2)
                for name_casc_option, command_casc_option in options_menu[name_option].items():
                    cascade_menu.add_command(label=name_casc_option, command=command_casc_option)
                self.f_current_path.menu_options.add_cascade(label=name_option, menu=cascade_menu)
        self.f_current_path.menu_options.grab_release()
        self.f_current_path.menu_options.tk_popup(x,y+30)
        self.f_current_path.menu_options.bind('<FocusOut>', self.close_context_menu)
        
    def close_menu_options(self, event):
        self.f_current_path.menu_options.delete(0, END)
        self.f_current_path.menu_options.unpost()
        
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
        files = list(filter(lambda x: file_name.lower() in x['name'].lower(), self.list_all_files))
        if file_name != '':
            self.upload_files(files)
        else:
            self.sort_files()

App()