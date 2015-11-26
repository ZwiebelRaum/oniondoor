# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name="oniondoor",
    packages=["oniondoor"],
    entry_points={
        "console_scripts": [
            "oniondoor = oniondoor.main:main",
        ]},
    description="RaspberryPi tool to manage our door buzzer system ",
    version="0.1.0",
    author="Donncha O'Cearbhail",
    author_email="donncha@donncha.is",
    url="https://github.com/ZwiebelRaum/oniondoor",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'arrow',
        'Flask',
        'pytimeparse',
        'RPi.GPIO',
        'fritzconnection',
    ],
)
