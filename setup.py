import setuptools

setuptools.setup(
    name='desksnake',
	version = "0.0.1",
    author='Ruckusist',
    author_email='ruckusist@outlook.com',
    url='https://ruckusist.com/snake',
    packages=setuptools.find_packages(),
    description="A Desksnake Game.",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    #########
    entry_points = {
        'console_scripts': [
            'desksnake=desksnake.desksnake:main',
            'desksnake_server=desksnake.desksnake:main',
        ]
    },
)
