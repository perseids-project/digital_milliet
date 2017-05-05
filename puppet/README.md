# puppet-digital_milliet
Puppet Module for Digital Milliet deployment

## Hiera Support
Defining Digital Milliet Resources in Hiera

```yaml
  digmill::app_root: '/var/www/digital_milliet'
  digmill::app_path: '/'
  digmill::vhost: 'digmill.yourdomain.org'
  digmill::app_version: 'master'
  digmill::repo_url: 'https://github.com/perseids-project/digital_milliet'
  digmill::ssl_cert: 'name_of_ssl_certificate_file.pem'
  digmill::ssl_chain: 'name_of_ssl_keychain_file.crt'
  digmill::ssl_private_key: 'name_of_ssl_private_key.key'
```
