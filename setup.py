from setuptools import setup, find_packages

setup(
    name='vertica-sqlalchemy',
    version='0.13',
    description='Vertica dialect for sqlalchemy',
    long_description=open("README.rst").read(),
    author='James Casbon',
    author_email='casbon@gmail.com',
    license="MIT",
    url='https://github.com/jamescasbon/vertica-sqlalchemy',
    packages=find_packages(exclude=["tests.*", "tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points="""
    [sqlalchemy.dialects]
    vertica.pyodbc = sqlalchemy_vertica.base:VerticaDialect
    """
)

