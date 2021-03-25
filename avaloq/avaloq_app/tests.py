from unittest import skip
from django.test import TestCase
from avaloq_app.testutil import get_all_tests, read_file
from avaloq_app.testsystem import LANGS, TestSystem

TEST_DIR = 'test_data'

class TestSystemTestCase(TestCase):
    def setUp(self):
        self.ts = TestSystem()
        self.all_tests = get_all_tests(f'{TEST_DIR}')

    def _ce(self, lang, source_code):
        verdict = self.ts.get_verdicts(lang, source_code, [])
        return type(verdict) == tuple

    def test_java_ce(self):
        self.assertTrue(self._ce(LANGS['java'], read_file(f'{TEST_DIR}/sols/ce.java')))

    def test_python_ce(self):
        self.assertTrue(self._ce(LANGS['python'], read_file(f'{TEST_DIR}/sols/ce.py')))

    def test_javascript_ce(self):
        self.assertTrue(self._ce(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/ce.js')))

    def _all(self, lang, source_code, tests, verdict):
        verdicts = self.ts.get_verdicts(lang, source_code, tests)
        for ver in verdicts.values():
            if ver[0] != verdict:
                return False
        return True

    def test_java_mle(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/mle.java'), self.all_tests, 'RE'))

    def test_python_mle(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/mle.py'), self.all_tests, 'RE'))

    def test_javascript_mle(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/mle.js'), self.all_tests, 'RE'))

    def test_java_ok(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/ok.java'), self.all_tests, 'OK'))

    def test_python_ok(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/ok.py'), self.all_tests, 'OK'))

    def test_javascript_ok(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/ok.js'), self.all_tests, 'OK'))

    def test_java_re(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/re.java'), self.all_tests, 'RE'))

    def test_python_re(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/re.py'), self.all_tests, 'RE'))

    def test_javascript_re(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/re.js'), self.all_tests, 'RE'))

    def test_java_to(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/to.java'), self.all_tests, 'TO'))

    def test_python_to(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/to.py'), self.all_tests, 'TO'))

    def test_javascript_to(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/to.js'), self.all_tests, 'TO'))

    def test_java_wa(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/wa.java'), self.all_tests, 'WA'))

    def test_python_wa(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/wa.py'), self.all_tests, 'WA'))

    def test_javascript_wa(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/wa.js'), self.all_tests, 'WA'))

    def test_apache_commons(self):
        self.assertTrue(self._all(LANGS['java'], read_file(f'{TEST_DIR}/sols/apache_commons.java'), self.all_tests, 'WA'))

    def test_forkbomb(self):
        self.assertTrue(self._all(LANGS['python'], read_file(f'{TEST_DIR}/sols/forkbomb.py'), self.all_tests, 'RE'))

    @skip('Doesn\'t work on the GitLab runner')
    def test_lodash(self):
        self.assertTrue(self._all(LANGS['javascript'], read_file(f'{TEST_DIR}/sols/lodash.js'), self.all_tests, 'WA'))

    
