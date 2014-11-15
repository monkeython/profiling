"""
python setup.py bdist_egg
"""
import os
import sys

WD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, WD)

NAME = 'ptofiling'
PACKAGE = __import__(NAME)
AUTHOR, EMAIL = PACKAGE.__author__.rsplit(' ', 1)

with open(os.path.join(WD, 'README.rst'), 'r') as README:
    DESCRIPTION = README.readline().strip()
    LONG_DESCRIPTION = '\n'.join((DESCRIPTION, README.read()))

URL = 'https://github.com/monkeython/%s' % NAME

EGG = {
    'name': NAME,
    'version': PACKAGE.__version__,
    'author': AUTHOR,
    'author_email': EMAIL.strip('<>'),
    'url': URL,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'classifiers': PACKAGE.__classifiers__,
    'keywords': PACKAGE.__keywords__,
    'packages': [NAME],
    'include_package_data': True,
    'test_suite': 'loremipsum.tests.suite'
}

if __name__ == '__main__':
    import setuptools
    setuptools.setup(**EGG)
