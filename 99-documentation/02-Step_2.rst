Install Stacks_workflow
***********************

Download and install the most recent version of this workflow
=============================================================

From the terminal, run:

.. code-block:: bash

 cd ~/Desktop
 wget https://github.com/enormandeau/stacks_workflow/archive/master.zip
 unzip master.zip

If ``git`` is installed on your computer (Mac user have it pre-installed on
Mavericks), you can run the following command instead to get a full ``git``
repository.

.. code-block:: bash

 git clone https://github.com/enormandeau/stacks_workflow

This will make it easier to update to the most recent version of the workflow,
which can be accomplished by running the following command from the
``stacks_workflow`` directory:

.. code-block:: bash

 git pull

For the rest of the project, use the extracted or cloned folder as your working
directory. **All the commands in this manual are launched from that
directory.**

Personal computer setup
=======================

Make sure you prepare your computer to run you GBS analyses. We have also
prepared a companion tutorial about GBS for cloud computing and computer setup
for GBS at: <http://gbs-cloud-tutorial.readthedocs.org/en/latest/>`_

Download and install `STACKS <http://creskolab.uoregon.edu/stacks/>`_
=====================================================================

Installing Google's SparseHash (reduces memory usage)
-----------------------------------------------------

.. code-block:: bash
 wget http://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz

 tar -xvf sparsehash-2.0.2.tar.gz
 cd sparsehash-2.0.2
 ./configure
 make
 sudo make install

Installing STACKS
-----------------

.. code-block:: bash

 # Modify the version number as needed
 wget http://creskolab.uoregon.edu/stacks/source/stacks-1.29.tar.gz

 tar -xvf stacks-1.29.tar.gz
 cd stacks-1.29
 
 # Install the binaries in /usr/local/bin
 ./configure --enable-sparsehash
 make
 sudo make install
 
 # Remove the folder and gz file
 cd ..
 sudo rm -R stacks-1.29 stacks-1.29.tar.gz sparsehash-2.0.2 sparsehash-2.0.2.tar.gz
 
Test the STACKS installation
----------------------------
 
.. code-block:: bash

 cstacks

This will output the help of the cstacks program. You will also be able to
confirm the version number of your STACKS installation.

Installing Cutadapt
-------------------

You can install cutadapt with the following command:

.. code-block:: bash

 sudo pip install --user --upgrade cutadapt

