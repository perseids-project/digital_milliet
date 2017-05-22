# puppet-digital_milliet
Puppet Module for Digital Milliet deployment

## Hiera Support
Defining Digital Milliet Resources in Hiera

```yaml
  digital_milliet::app_root: '/var/www/digital_milliet'
  digital_milliet::app_path: '/'
  digital_milliet::vhost: 'digital_milliet.yourdomain.org'
  digital_milliet::app_version: 'master'
  digital_milliet::repo_url: 'https://github.com/perseids-project/digital_milliet'
  digital_milliet::ssl_cert: 'name_of_ssl_certificate_file.pem'
  digital_milliet::ssl_chain: 'name_of_ssl_keychain_file.crt'
  digital_milliet::ssl_private_key: 'name_of_ssl_private_key.key'
```
