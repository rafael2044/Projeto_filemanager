from pathlib import Path
import os
print(Path.group(Path('/')))
print(Path.expanduser(Path('~')).stat())
print(str(Path.home()).split('/'))
print(Path("/home/rafael/Documentos/Programacao").owner())