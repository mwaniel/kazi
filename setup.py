from setuptools import setup, find_packages

setup(
    name='kazi',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kazi=kazi.main:main',
        ],
    },
    description='Kazi - A distributed source control system',
    author='mwaniel',
    author_email='mwaniel03@gmail.com',
    license='MIT',
    install_requires=[],
)
