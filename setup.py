from distutils.core import setup
setup(
  name = 'collada_wt',         # How you named your package folder (MyLib)
  packages = ['collada_wt'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='BSD 3-Clause License',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'This library allows you to easily create a 3D collada wind turbine for use in Google Earth Pro',   # Give a short description about your library
  author = 'Charlie Plumley',                   # Type in your name
  author_email = 'charlie.plumley@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/charlie9578/wind-turbine-kml',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/charlie9578/wind-turbine-kml/archive/refs/tags/v0.2-alpha.tar.gz',    # Found under the release version on GitHub
  keywords = ['wind turbine', 'collada', 'google earth', 'kml'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pycollada',
          'numpy',
          'simplekml',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which python versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)