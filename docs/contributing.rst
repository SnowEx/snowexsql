.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/SnowEx/snowexsql/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

snowexsql could always use more documentation, whether as part of the
official snowexsql docs, in docstrings, or even on the web in blog posts,
articles, and such.

Adding an Upload Script
~~~~~~~~~~~~~~~~~~~~~~~

One way of making the database more valuable is to expand what data it holds.
To do this simply:

1. Add a python script under `./scripts` using the naming convention
   `add_<Your_awesome_data>.py`, this will allow for it to be detected by the
   `run.py` script automatically.

2. Add the follow code:

    .. code-block:: python

      # You may choose to import only your batch uploader
      from snowexsql.batch import *

      # Define your main function which will be called by run.py
      def main():
        '''
        Uploader script for <My Data>
        '''
        # 1. Define the files to be uploaded.

        # 2. Assign any constant metadata and pass it as keyword arguments to the uploader

        # 3, Pass them to you batch uploader you need

        # 4. Push to the database and collect the errors from push function

        errors = [] # replace me with your errors = <your_batch_class>.push()
        return errors

      # Add this so you can run your script directly without running run.py
      if __name__ == 'main':
        main()

3. If you are uploading a file with multiple datasets inside of it to the Layers
   or point data tables, you will need to add their data names to metadata.py.
   This will allow the uploaders to automatically detect the multiple profiles
   in a single file. Simply add you data name to the class variable
   `available_names <https://github.com/SnowEx/snowexsql/blob/b4a0fb2baadedcd96fa95275c3d2262c69ed0cf4/snowexsql/metadata.py#L390>`
   in metadata.py.


Adding Jupyter Notebooks
~~~~~~~~~~~~~~~~~~~~~~~~

This project can always use examples of using the data from the database. To
add an example simply:

1. Create a new jupyter notebook under `docs/gallery`. Name the notebook
   `<your_project>_example.ipynb`. Note it must have the `_example` to be found by
   sphinx (documentation software).

2. Add a brief goal of the notebook and an enumerate steps list. Then use
   markdown `###` e.g. `### Step 1:` to demarcate each step so it shows up in the table of contents

3. After you have created/ran it, tag a cell with figures to make use of
   thumbnails in the docs. Those are:
                              * `nbsphinx-thumbnail`
                              * `nbsphinx-gallery`

*Note: you can assign these tags pretty easy by accident to other blocks simultaneously which
will break the thumbnail generator. If your thumbnail doesn't show up then check
which blocks had tags enabled*

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/SnowEx/snowexsql/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `snowexsql` for local development.

1. Fork the `snowexsql` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/snowexsql.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv snowexsql
    $ cd snowexsql/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ pytest

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, 3.6, 3.7 and 3.8, and for PyPy. Check
..    https://travis-ci.com/SnowEx/snowexsql/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ pytest tests.test_snowexsql


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Travis will then deploy to PyPI if tests pass.
