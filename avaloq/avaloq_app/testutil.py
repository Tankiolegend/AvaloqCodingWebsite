import os

def read_file(name):
    with open(name, 'r') as f:
        return f.read()

def write_file(name, content):
    with open(name, 'w') as f:
        f.write(content)

def box_path(id=0):
    return '/var/local/lib/isolate/{}/box'.format(id)

def get_all_tests(folder):
    tests = []
    for test_file in os.listdir(folder):
        if test_file.endswith(".in"):
            tests.append(folder + '/' + test_file[:-3])
    return tests


def get_sample_tests(folder):
    return [test for test in get_all_tests(folder) if os.path.basename(test).startswith('sample_')]

def parse_meta(content):
    meta = dict()
    for line in content.split('\n'):
        try:
            key, val = line.split(':')
            meta[key] = val
        except:
            pass
    return meta

def get_inputs(tests):
    return (read_file(test + '.in') for test in tests)