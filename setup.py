from setuptools import  setup

setup(
    name='ppty',       
    description='Run process in pseudoterminal',
    version='0.1.0',
    author='Tao Qingyun',
    author_email='84576765@qq.com',
    url='https://github.com/qingyunha/ppty',
    packages=['ppty'],
    keywords='pty terminal',
    entry_points={'console_scripts': ['ppty = ppty.__main__:main']},
)
