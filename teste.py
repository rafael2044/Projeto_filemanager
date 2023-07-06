from os import listdir
from pathlib import Path



def search_file(name_file, path=Path.home()):
    if path.is_file():
        return
    if path.is_dir():
        files = list(filter(lambda x: x[0] != '.', listdir(path)))
        if name_file in files:
            return Path(path, name_file)
        if files:
            for dir in files:
                return search_file(name_file, Path(path, dir))
        
    
    
    

def get_all_folders(lista,path):
    if path.is_file():
        lista.append([path])
        return lista

    if path.is_dir():
        folders = list(filter(lambda x: x[0] != '.', listdir(path)))
        if folders:
            lista.append([[name, Path(path, name)] for name in folders])
    return get_all_folders(lista, path)




if Path.exists(Path.home()):
    folder_home = list(filter(lambda x: x[0] != '.', listdir(Path.home())))
    if folder_home:
        list_folder = [[name,Path(Path.home(), name)] for name in folder_home]
        for file in list_folder:
            if file[-1].exists:
                folders = list(filter(lambda x: x[0] != '.', listdir(file[-1])))
                if folders:
                    file.append([[n,Path(file[-1], n)] for n in folders])
        
print(search_file('Programacao'))
