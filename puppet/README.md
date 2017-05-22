# puppet-digital_milliet
Puppet Module for Digital Milliet production deployment. 

The recommended production deployment for the Digital Milliet is to run under Apache using mod_wsgi.  SSL is required if
OAuth is enabled.

The puppet module in this directory can be used with Puppet 4 to install the recommended deployment setup.

The following settings must be provided in your Hiera file to configure the deployment:

```yaml
  # path in which the Digital Milliet code will be installed
  digital_milliet::app_root: '/var/www/digital_milliet'
  # path to serve the app under Apache
  digital_milliet::app_path: '/'
  # the domain of the deployment server
  digital_milliet::vhost: 'digital_milliet.yourdomain.org'
  # the version of the code to install (i.e. github tag or branch)
  digital_milliet::app_version: 'master'
  # path to the production configuration file for the digital_milliet application
  # contains secret keys for OAuth setup, and other site-specific configuration
  digital_milliet::config_file: 'full_path_to_digital_milliet_config_file'
  # the github respository source for the code
  digital_milliet::repo_url: 'https://github.com/perseids-project/digital_milliet'
  # the ssl cert file for your Apache SSL host
  digital_milliet::ssl_cert: 'full_path_to_ssl_certificate_file'
  # the ssl keychain file for your Apache SSL host
  digital_milliet::ssl_chain: 'full_path_to_ssl_keychain_file'
  # the ssl private key file for your Apache SSL host
  digital_milliet::ssl_private_key: 'full_path_to_ssl_private_key.key'
  # user to own the Digital Milliet code on your system
  digital_milliet::user: 'user_to_own_the_files'
  # backup directory for the mongo database 
  digital_milliet::backup_dir: 'backup_directory_for_mongo_db'
  # the version of python to use
  digital_milliet::python_version: '3.5'
  # the name of the apache mod_wsgi package
  digital_milliet::python_apache_package: 'libapache2-mod-wsgi-py3'
```
