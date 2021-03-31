from avaloq_app.langs import Java, Python, JavaScript

LANGS = {'java': Java(), 'python': Python(), 'javacript': JavaScript()}


class TestSystem:
    def __init__(self):
        pass

    @staticmethod
    def get_outputs(lang, source_code, test_inputs):
        return [('OK', '25\n', 'random input'), ('CE', '', 'random input 2')]

    @staticmethod
    def get_verdicts(lang, source_code, tests):
        return {"tasks/test_cases/1/sample_50": ["WA", "not 50"], "tasks/test_cases/1/sample_100": ["WA", "not 100"],
                "tasks/test_cases/1/1000": ["WA", "not 1000"], "tasks/test_cases/1/100000":
                    ["WA", "not 1 moc nul"], "tasks/test_cases/1/sample_1000": ["WA", "not 1000"],
                "tasks/test_cases/1/sample_10": ["WA", "not 10"]}
