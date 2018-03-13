# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
# from Cython.Build import cythonize
# from distutils.extension import Extension

__version__ = '1.0'
# sourcefiles = ['dmsic.py', 'declar.py', 'smev.py', 'about.py', 'qtui.py',
#                'translit.py']
# extensions = [Extension("dmsic", sourcefiles)]

setup(
    # ext_modules=cythonize(extensions),
    name='dmsic',
    version=__version__,
    description='Directum SMEV integration client',
    license='GPL',
    scripts=['dmsic.py', 'db.py', 'declar.py', 'smev.py', 'six.py',
             'cached_property.py', 'about.py', 'qtui.py', 'translit.py'],
    # scripts=cythonize(sourcefiles),
    packages=find_packages(),
    # packages=findall(),
    package_data={
        'lxml': ['*.pyd', '*.h', '*.dll', '*.rng', '*.xsl', '*.txt', '*.pxd',
                 'includes/*.pxd']
    },
    include_package_data=True,
    entry_points={'console_scripts': ['dmsic = dmsic:main']},
    install_requires=['setuptools', 'PyQt5', 'Cython']
)
