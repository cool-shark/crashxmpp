from setuptools import setup, find_packages


setup(name='crashxmpp',
      version='0.0',
      description='crashxmpp plugin for supervisord',
      long_description='',
      classifiers=[
        "Development Status :: 1 - Alpha",
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: System :: Boot',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        ],
      author='Timu Eren',
      author_email='timu.eren@coolshark.com',
      url='http://github.com/cool-shark',
      keywords = 'supervisor monitoring',
      packages = find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'setuptools',
            'supervisor',
            ],
      tests_require=[
            'supervisor',
            ],
      test_suite="",
      entry_points = """\
      [console_scripts]
      crashxmpp = crashxmpp:main
      """
      )

