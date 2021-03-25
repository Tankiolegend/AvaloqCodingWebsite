import shutil
import threading

from avaloq_app.langs import Java, Python, JavaScript
from avaloq_app.testutil import box_path, parse_meta, read_file, write_file

LANGS = {'java': Java(), 'python': Python(), 'javascript': JavaScript()}

class TestSystem:
    def __init__(self):
        self.lock = threading.Lock()

    def _prepare(self, lang, source_code):
        executable, compile_error = lang.compile(source_code)
        if executable == '':
            return compile_error
        shutil.copy(executable, box_path())
        return None

    def _get_output(self, lang, test_input):
        write_file(box_path() + '/in', test_input)
        output, error = lang.run()
        meta = parse_meta(read_file('meta'))
        if 'status' in meta:
            return meta['status'], error, test_input
        return 'OK', output, test_input
    
    def get_outputs(self, lang, source_code, test_inputs):
        with self.lock:
            compile_error = self._prepare(lang, source_code)
            if compile_error != None:
                return 'CE', compile_error, test_inputs
            return [self._get_output(lang, test_input) for test_input in test_inputs]

    def _get_verdict(self, lang, test_input, test_output):
        verdict, details, _ = self._get_output(lang, test_input)
        if verdict != 'OK':
            return verdict, details
        return ('OK', '') if details == test_output else ('WA', '')

    def get_verdicts(self, lang, source_code, tests):
        with self.lock:
            compile_error = self._prepare(lang, source_code)
            if compile_error != None:
                return 'CE', compile_error
            verdicts = dict()
            for test in tests:
                verdicts[test] = self._get_verdict(lang, read_file(test + '.in'), read_file(test + '.out'))
            return verdicts
