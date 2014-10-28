from distutils.core import setup

setup(
    name='python_yousign',
    version='0.1.1',
    author='Nicolas Tobo',
    author_email='nico@coinvestclub.com',
    packages=['yousign'],
    package_dir={'': 'yousign'},
    url='https://github.com/coinvestclub/python-yousign',
    download_url='https://github.com/coinvestclub/python-yousign/releases',
    license='GNU GPL V3',
    description='a python client for Yousign API',
    long_description=open('README.rst').read()
)
