#
# @see https://packaging.python.org/tutorials/distributing-packages/
#
from setuptools import setup, find_packages

__updated__ = "2017-09-25"

requires = [
    'PasteDeploy',
    'cython',
    'ujson',
    'falcon',
    'gunicorn',
    'RestrictedPython',
]

tests_require = [
    'WebTest >= 1.3.1',
    'tox',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-xdist'
]

setup_requires = [
    'setuptools-markdown',
    'pytest-runner'
]

setup(
    # ------------------------------------------------------------------------
    # Beschreibung des Pakets
    name='script',
    version='0.0',
    description='script',
    license='MIT',
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    # ------------------------------------------------------------------------
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Falcon',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        # --------------------
        # einen Status wählen:
        # --------------------
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
    ],

    # ------------------------------------------------------------------------
    # Einstiegspunkt
    entry_points={
        'paste.app_factory': [
            'main = script:app_factory',
        ],
    },

    # ------------------------------------------------------------------------
    # Paketkonfiguration

    long_description_markdown_filename='README.md',
    packages=find_packages(exclude=['docs', 'tests', 'static']),
    include_package_data=True,
    # can the package be run from within a zip-file
    zip_safe=True,

    python_requires='>=3',
    extras_require={
        'testing': tests_require,
    },
    test_suite='pytest',
    setup_requires=setup_requires,
    install_requires=requires,
)
