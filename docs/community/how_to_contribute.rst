##################
How to contribute?
##################

The first step to a contribution is to set up a local development environment.
Below are the steps and additional information that will get you from your idea
to a code contribution, adding tests, and finally opening a pull request
to the main stable code branch.

Local Development Setup
=======================

#. Fork the `snowexsql` repo on to your GitHub account.

   `Here the official GitHub docs on how to do this <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>`_

#. Clone your fork locally

   .. attention:: Make sure to replace `your_name_here` with your GitHub user name

   .. code-block:: bash

     $ git clone git@github.com:your_name_here/snowexsql.git
     $ cd snowexsql/

#. Install your local copy into a virtualenv.

   Assuming you have virtualenvwrapper installed, this is how you set up your
   fork for local development:

   .. code-block:: bash

     $ mkvirtualenv snowexsql

   .. important:: Below command should be executed inside the cloned repository
      from the step above.

   .. code-block:: bash

     $ python setup.py develop

   If you are planning on running the tests or building the docs below also run:

   .. code-block:: bash

    $ pip install -r requirements_dev.txt
    $ pip install -r docs/requirements.txt

#. Create a branch for local development

   We recommend using the `GitHub flow <https://docs.github.com/en/get-started/using-github/github-flow>`_
   workflow that is used in many open-source projects for editing an existing
   code base.

   .. code-block:: bash

      $ git checkout -b name-of-your-bugfix-or-feature

#. Start editing the code and implement your idea.

#. You completed your changes

   When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox. Also note the
   setup steps below to set up a `test database <#tests>`_ .

   .. code-block:: bash

      $ pytest

#. Commit your changes and push your branch to GitHub

   .. code-block:: bash

      $ git add .
      $ git commit -m "Your detailed description of your changes."
      $ git push origin name-of-your-bugfix-or-feature

#. Submit a pull request through the GitHub website.

   If you haven't done this before - have a look at
   `the official GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_
   on how to do this.


Tests
=====

Before testing, in a separate terminal, we need to run a local instance
of the database. This can be done with

.. code-block:: bash

  $ docker-compose up -d

When you are finished testing, make sure to turn the docker off

.. code-block:: bash

  $ docker-compose down

Quickly test your installation by running:

.. code-block:: bash

  $ python3 -m pytest tests/

The goal of this project is to have high fidelity in data
interpretation/submission to the database. To see the current
test coverage run:

.. code-block:: bash

  $ make coverage

Tips
----

To run a subset of tests::

$ pytest tests.test_snowexsql

Pull Request Guidelines
=======================

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
3. The pull request should work for Python 3.5, 3.6, 3.7 and 3.8, and for PyPy.
   Check
   ..    https://github.com/SnowEx/snowexsql/pulls
   and make sure that the tests pass for all supported Python versions.


Deploying
=========

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed.
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Once the tag is merged, a release can be published with 
.. https://github.com/SnowEx/snowexsql/releases/new
The release name should follow the convention `snowexsql-v0.4.1`
