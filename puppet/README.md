# puppet-digital_milliet
Puppet Module for Digital Milliet deployment

## Hiera Support
Defining Digital Milliet Resources in Hiera

```yaml
  digital_milliet::app_root: '/var/www/digital_milliet'
  digital_milliet::app_path: '/'
  digital_milliet::vhost: 'digital_milliet.yourdomain.org'
  digital_milliet::app_version: 'master'
  digital_milliet::config_file: 'full_path_to_digital_milliet_config_file'
  digital_milliet::repo_url: 'https://github.com/perseids-project/digital_milliet'
  digital_milliet::ssl_cert: 'full_path_to_ssl_certificate_file'
  digital_milliet::ssl_chain: 'full_path_to_ssl_keychain_file'
  digital_milliet::ssl_private_key: 'full_path_to_ssl_private_key.key'
  digital_milliet::user: 'user_to_own_the_files'
  digital_milliet::backup_dir: 'backup_directory_for_mongo_db'
```
