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

Running the test suite requires a locally running database and providing
the credentials to connect to it. Setting up an instance can be done via
the supplied Docker compose file (see steps below).

Setting up DB credentials
----
Copy the supplied sample file locally in a terminal

.. code-block:: bash

  mv tests/credentials.json.sample tests/credentials.json

The file contains the username and password for connecting to the DB within
the Docker container.

Docker commands
----

After `installing Docker <https://docs.docker.com/desktop/>`_,
you can start up a ready to go database instance.

Start a database
****
.. code-block:: bash

  $ docker-compose up -d

Stop a database
****
When you are finished testing, make sure to turn the docker off

.. code-block:: bash

  $ docker-compose down

Running the test suite
----
Quickly test your installation by running:

.. code-block:: bash

  $ python3 -m pytest tests/

Testing the code coverage
----
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
Then, in Github,
 1. Draft a new release https://github.com/SnowEx/snowexsql/releases/new
 2. Create a new tag in the style of `v0.x.x`_
 3. Set release title to `snowexsql v<version>`_
 4. Enter release notes
 5. Check that the action has released succesfully

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Once the tag is merged, a release can be published with 
.. https://github.com/SnowEx/snowexsql/releases/new
The release name should follow the convention `snowexsql-v0.4.1`
