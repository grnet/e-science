Installation of Ruby and Travis
---
    sudo apt-get install ruby
    sudo apt-get install ruby-dev
    sudo apt-get install rubygems build-essential
    sudo gem install travis

Encrypt the .config.txt file
---
    travis login
    travis encrypt-file super_secret.txt --add


