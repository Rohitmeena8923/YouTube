from setuptools import setup, find_packages

setup(
    name="youtube-telegram-bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==20.3',
        'pytube==15.0.0',
        'moviepy==1.0.3',
        'python-dotenv==1.0.0',
    ],
)