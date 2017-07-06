import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append(".")
import optimize_upip

setup(name='micropython-buzzer',
      version='1.0.0',
      description='Buzzer implemetion for MicroPython',
      long_description='simplae buzzer implemtion that can play nokia composer notes',
      url='https://github.com/micropython/micropython-lib',
      author='CPython Developers',
      author_email='python-dev@python.org',
      maintainer='MicroPython Developers',
      maintainer_email='micro-python@googlegroups.com',
      license='Python',
      cmdclass={'optimize_upip': optimize_upip.OptimizeUpip},
      py_modules=['ubuzzer'])
