import setuptools

setuptools.setup(
    name = "mygit",    
    version = "0.0.1",
    author = "EasyPeasy",
    author_email = "EasyPeasyChannel@gmail.com",
    description = ("Super simple git"),
    license = "MIT",
    keywords = "git mygit",
    packages=setuptools.find_packages(),
    long_description=open('readme.md').read(),
    include_package_data=True,
    options={
        'build_scripts': {
            'executable': '/bin/mygit',
        },
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: MIT License",
    ],
)
        
"""
    entry_points={
        'console_scripts': [
            'mygit=mygit.__main__:main'
        ]
    },
    """                