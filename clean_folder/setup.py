from setuptools import setup, find_namespace_packages

setup(
    name='clean_folder',
    version='1.0',
    description='This script sort and clean folder',
    url='https://github.com/davydenkoo/homework_7',
    author='Oleh Davydenko',
    author_email='oleg.davidenko@gmail.com',
    license='MIT License (X11 License)',
    packages=find_namespace_packages(),
    entry_points={'console_scripts': [
        'clean-folder = clean_folder.clean:main']}
)
