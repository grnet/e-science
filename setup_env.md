How to setup virtualenv and run orca
--
	[sudo]apt-get update
	[sudo]apt-get install git
	[sudo]apt-get install python-pip python-dev libpq-dev postgresql-9.1
	[sudo]pip install virtualenv
        
	
	mkdir .virtualenvs
	cd .virtualenvs
	virtualenv orca
	. ../.virtualenvs/orca/bin/activate

	cd ~/working_directory
	git clone <projecturl> orca
	pip install -r requirements.txt
