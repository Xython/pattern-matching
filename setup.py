from setuptools import setup

with open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pattern-matching',
    long_description=readme,
    version='0.2',
    url='https://github.com/Xython/pattern-matching',
    license='MIT',
    author='thautwarm',
    author_email='twshere@outlook.com',
    description='effective and graceful pattern matching for original python',
    include_package_data=True,
    packages=['pattern_matching', 'pattern_matching.core', 'pattern_matching.core.parserlib'],
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'],
    zip_safe=False,
    install_requires=[
        "EBNFParser",
        "linq",
        "pipe_fn"
    ],
)
