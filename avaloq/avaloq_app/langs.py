import os
import subprocess
from avaloq_app.testutil import write_file

TIME = 2
WALL_TIME = 3

class Java:
    def __init__(self):
        self.bin = '/usr/lib/jvm/java-11-openjdk-amd64/bin/'

    def _javac(self, java_file):
        p = subprocess.Popen([self.bin + 'javac', '-cp', 'jars/*', java_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = p.communicate()
        return p.returncode, error.decode()

    def _java(self, class_file):
        p = subprocess.Popen(
            ['isolate', '--processes=32', '--meta=meta', f'--time={TIME}', f'--wall-time={WALL_TIME}', '--stdin=in', '--run', self.bin + 'java', class_file[:-6]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = p.communicate()
        return output.decode(), error.decode()

    # returns (class_file, error)
    def compile(self, source_code):
        write_file('Main.java', source_code)
        returncode, error = self._javac('Main.java')
        if returncode == 0:
            return 'Main.class', ''
        return '', error

    # assume "Main.class" and "in" are present in the box
    def run(self):
        output, error = self._java('Main.class')
        return output, error

class Python:
    def __init__(self):
        self.bin = '/usr/bin/'

    def _py_compile(self, python_file):
        p = subprocess.Popen([self.bin + 'python3', '-m', 'py_compile', python_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = p.communicate()
        return p.returncode, error.decode()

    def _python(self, python_file):
        p = subprocess.Popen(
            ['isolate', '--meta=meta', f'--time={TIME}', f'--wall-time={WALL_TIME}', '--stdin=in', '--run', self.bin + 'python3', python_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = p.communicate()
        return output.decode(), error.decode()

    def compile(self, source_code):
        write_file('main.py', source_code)
        returncode, error = self._py_compile('main.py')
        if returncode == 0:
            return 'main.py', ''
        return '', error

    def run(self):
        output, error = self._python('main.py')
        return output, error

class JavaScript:
    def __init__(self):
        self.bin = '/usr/bin/'

    def _node_check(self, js_file):
        p = subprocess.Popen([self.bin + 'node', '--check', js_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = p.communicate()
        return p.returncode, error.decode()

    def _node(self, js_file):
        p = subprocess.Popen(
            ['isolate', '--processes=32', '--meta=meta', f'--time={TIME}', f'--wall-time={WALL_TIME}', '--stdin=in', '--run', self.bin + 'node', js_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = p.communicate()
        return output.decode(), error.decode()

    def compile(self, source_code):
        write_file('main.js', source_code)
        returncode, error = self._node_check('main.js')
        if returncode == 0:
            return 'main.js', ''
        return '', error

    def run(self):
        output, error = self._node('main.js')
        return output, error

