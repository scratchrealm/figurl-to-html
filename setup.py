from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    scripts=[],
    include_package_data=True,
    package_data={
        'figurl_to_html': ['templates/*'],
    },
    install_requires=[
        'kachery-cloud',
        'click',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'figurl-to-html=figurl_to_html.cli:cli'
        ]
    }
)
