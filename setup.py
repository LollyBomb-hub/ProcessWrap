from zipfile import ZipFile
from os.path import dirname, join
import subprocess

try:
    library = ZipFile(join(dirname(__file__), "processes.zip"))
    library.extractall(dirname(subprocess.__file__))
    library.close()
except Exception as e:
    print(e)