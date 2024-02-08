from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

with open('requirements-dev.txt') as f:
    install_dev = f.read().strip().split('\n')

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='wwc',
    version=version,
    description='Wine Website Checker',
    author='Ulysse Dansin',
    author_email='udansin@hotmail.fr',
    packages=find_packages(exclude=['tests']),
    package_data={'': ['*.json', 'VERSION']},
    include_package_data=True,
    install_requires=install_requires,
    tests_require=install_dev
)
