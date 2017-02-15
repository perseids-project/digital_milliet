from setuptools import setup

setup(
    name='digital_milliet',
    packages=['digital_milliet'],
    include_package_data=True,
    test_suite="tests",
    install_requires=[
        'flask==0.12',
        "Flask-OAuthlib>=0.9.3",
        "MyCapytain==.0.0.9",
        "Flask-Babel==0.9",
        "Flask-Bower==1.0.1",
        "requests>=2.5.0",
        "Flask-Cache==0.13.1",
        "requests-cache==0.4.9",
        "flask-cors==2.0.0",
        "Flask-PyMongo==0.3.1",
        "Flask-Markdown"
    ],
    setup_requires=[
    ],
    tests_require=[
        "PyYaml"
    ]
)
