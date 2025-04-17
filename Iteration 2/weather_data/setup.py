from setuptools import setup, find_packages

setup(

   name='weather-tools-DrewBuck',

   version='0.1.0',

   author='Andrew Buckland',

   author_email='10916844@uvu.edu',

   packages=find_packages(),

   python_requires='>=3.8',

   url='',

   license='license.txt',

   description='A Package for looking at weather data',

   long_description=open('README.md').read(),

   long_description_content_type='text/markdown',

   install_requires=[
        'Pandas'
   ],

   include_package_data=True
)