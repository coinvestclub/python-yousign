from distutils.core import setup

setup(
    name='python_yousign',
    version='0.1.0',
    author='Nicolas Tobo',
    author_email='nico@coinvestclub.com',
    packages=['yousign'],
    url='',
    license='LICENSE',
    description='a python client for Yousign API',
    long_description=open('README.rst').read(),
    package_data={},
    install_requires=[
        "suds-jurko==0.6",
        "lxml==3.3.5",
        "pytz==2014.7"
    ],
)
