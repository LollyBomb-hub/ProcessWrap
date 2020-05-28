from sys import platform
from shutil import rmtree, copyfile
from random import randint
from os import system, getcwd, path, curdir, chdir, mkdir
from time import sleep, time
from multiprocessing import Process as p

mswin = (platform == "win32")
if mswin:
    from subprocess import Popen, REALTIME_PRIORITY_CLASS
else:
    from subprocess import Popen


PATH = path.dirname(__file__)
TASKS_PATH = path.join(PATH, "tasks")
FILE_NUMBER = 0
CWD = getcwd()

class FileIO:
    def __init__(self, path,create=True) -> None:
        self.__path = path
        if create:
            self.__create()
        return None

    def __create(self) -> None:
        with open(self.__path, mode="w") as f:
            f.write("")
            f.close()
        return None
        
    def writeln(self, text) -> bool:
        b = self.write(text)
        self.write("\n")
        return b

    def write(self, text) -> bool:
        try:
            with open(self.__path, mode="a") as f:
                for i in text:
                    f.write(i)
            return True
        except Exception as e:
            print("Error occured: ", e)
            return False

    def read(self):
        try:
            with open(self.__path, mode="r") as f:
                f.seek(0)
                return "".join(f.readlines())
        except Exception as e:
            print("Error occured: ", e)
            return str(e)

    def get_path(self) -> str:
        return self.__path


def stuff(task):
    if mswin:
        Popen(creationflags=REALTIME_PRIORITY_CLASS, shell=True, args=task)
    else:
        Popen(start_new_session=True, shell=True, args=task)


def force_clear():
    rmtree(TASKS_PATH)


class ProcessUnion:
    def __init__(self, *processes, condition=None):
        if condition is True or str(type(condition)) == "<class 'function'>":
            if condition is True:
                self.__ready = True
            else:
                self.__ready = False
        else:
            raise ValueError('Invalid condition argument')
        self.__cond = condition
        self.__procs = processes
        return None

    def __call__(self):
        self.run()
        return None

    def run(self):
        if self.__ready:
            self.__strtd = [i() for i in self.__procs]
        else:
            for i in self.__cond():
                for j in self.__procs:
                    j.send_data(i)
            self.__strtd = [i() for i in self.__procs]
    
    def state(self):
        try:
            return self.__states
        except:
            return [i.return_state() for i in self.__procs]

    def clearcache(self):
        if self.ready():
            self.__states = self.state()
            self.__cleared = [i.clear() for i in self.__procs]

    def ready(self):
        self.__ready = [i.is_ready() for i in self.__procs]
        return not (False in self.__ready)

    def wait(self):
        while not self.ready():
            sleep(0.05)
        sleep(0.3)
        self.__states = [i.return_state() for i in self.__procs]
        self.clearcache()
        #self.clearcache()


class Process:
    def __init__(self, f, map_targets=None, cmd=False, timeout=10) -> None:
        self.__cmd = cmd
        self.__is_file = not map_targets==None
        self.__map_t = map_targets
        self.__source = path.join(CWD,f)
        self.__runing = False
        self.__prepfold()
        self.__preparation = "from time import sleep\nfrom os import system,getcwd\nimport sys\nif __name__ == '__main__':\n\tsys.stdin = open(r'{0}',mode='r')\n\tsys.stdout = open(r'{1}',mode='w')\n\tsys.stderr = open(r'{2}',mode='w')\n".format(self.__stdinp,self.__stdoutp,self.__stderrp)
        self.__stdin = FileIO(self.__stdinp)
        self.__stdout = FileIO(self.__stdoutp)
        self.__stderr = FileIO(self.__stderrp)
        self.__time = timeout
        self.__tofile()
        self.__error = False
        return None

    def __tofile(self) -> None:
        self.__task = FileIO(self.__fname)
        self.__task.write(self.__preparation)
        if self.__cmd:
            for i in self.__source.split(','):
                self.__task.writeln("system('" + i + "')")
        else:
            if self.__is_file:
                # self.__task_res.write(self.__preparation)
                self.__task.writeln("import "+self.__src_name)
                if isinstance(self.__map_t,list):
                    self.__task.writeln("from multiprocessing import Process")
                    self.__task.write("p=[")
                    for i in range(len(self.__map_t)):
                        self.__task.write(self.__gen_proc_string(self.__map_t[i]))
                        if i < len(self.__map_t) - 1:
                            self.__task.write(",")
                    self.__task.writeln("]")
                    for i in range(len(self.__map_t)):
                        self.__task.writeln("p["+str(i)+"].start()")
                        if i%2==0:
                            self.__task.writeln("p["+str(i)+"].join()")
                elif isinstance(self.__map_t,str):
                    self.__task.writeln("from threading import Thread")
                    self.__task.writeln("t = "+self.__gen_thread_string(self.__map_t))
                    self.__task.writeln("t.start()")
                    self.__task.writeln("t.join()")
            else:
                self.__task.write(self.__source)
        self.__task.writeln("")
        self.__task.writeln("print(__file__+' executed!')")
        self.__task.writeln("sleep(1)")
        if mswin:
            self.__task.writeln("system('del " + self.__sp + "')")
            self.__task.writeln("system('del ' + __file__)")
        else:
            self.__task.writeln("system('rm " + self.__sp + "')")
            self.__task.writeln("system('rm ' + __file__)")
        return None
            
    def __gen_thread_string(self,v) -> str:
        return "Thread(target="+self.__src_name+"."+str(v)+")"
        
    def __gen_proc_string(self,v) -> str:
        return "Process(target="+self.__src_name+"."+str(v)+")"

    def __get_state(self) -> tuple:
        self.__state = [self.__stdout.read(), self.__stderr.read()]
        if len(self.__state[0]) == len(self.__state[1]) == 0:
            return "Not ready"
        else:
            self.__state = [self.__state[0].split('\n'), self.__state[1].split('\n')]
        if len(self.__state[1]) > 0:
            self.__error = True
            return self.__state
        if self.is_ready():
            self.__state[0] = self.__state[0][:len(self.__state[0])-2]
        self.__state = (self.__state[0], self.__state[1])
        return self.__state

    def return_state(self) -> tuple:
        return self.__get_state()

    @classmethod
    def force_clear(self):
        rmtree(TASKS_PATH)

    def run(self) -> None:
        self.__run__()

    def __run__(self) -> None:
        if self.__runing:
            print("Error! Process already started it\'s execution.")
            return None
        self.__runing = True
        arg = p(target=stuff("python " + self.__task.get_path()), daemon=True)
        arg.start()
        del arg
        return None

    def send_data(self, *data) -> bool:
        if self.__runing:
            print("Can't send data! Process has started it\'s execution.")
            return False
        for i in data:
            self.__stdin.write(str(i))
            self.__stdin.write("\n")
        return False

    def __call__(self) -> None:
        self.run()
        return None

    def __repr__(self):
        return str(self.__class__)

    def wait(self):
        t = time()
        while True:
            if self.__error:
                break
            if self.__get_state() != "Not ready":
                break
            if time() - t > self.__time:
                break
            self.return_state()
            sleep(0.01)
        return self.__state

    def is_ready(self):
        self.__get_state()
        if self.__error:
            return True
        try:
            with open(self.__fname, mode="r") as src:
                res = src.readlines()
            return False
        except:
            return True

    def __prepfold(self):
        chdir(PATH)
        try:
            mkdir("tasks")
        except:
            pass   
        global FILE_NUMBER
        FILE_NUMBER += 1
        name = "task" + str(FILE_NUMBER)
        self.__stdinp = path.join(TASKS_PATH, name + "stdin.txt")
        self.__stdoutp = path.join(CWD, name + "stdout.txt")
        self.__stderrp = path.join(TASKS_PATH, name + "stderr.txt")
        self.__fname = path.join(TASKS_PATH, name + ".py")
        if self.__is_file:
            self.__src_name = "task_source" + str(FILE_NUMBER)
            self.__sp = copyfile(self.__source,path.join(TASKS_PATH,self.__src_name + ".py"))
            self.__task_res = FileIO(self.__sp,create=False)

    def clear(self):
        pref = "rm "
        if mswin:
            pref = "del "
        if self.is_ready():
            system(pref + self.__stdinp)
            system(pref + self.__stdoutp)
            system(pref + self.__stderrp)
            if self.__is_file:
                system(pref + self.__sp)
        else:
            print("Not ready")
