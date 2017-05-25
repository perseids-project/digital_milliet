# Puppet configuration for Digital Milliet
class digital_milliet($app_root,
              $app_path,
              $app_version,
              $repo_url, 
              $config_file,
              $vhost,
              $ssl_cert,
              $ssl_chain,
              $ssl_private_key,
              $backup_dir,
              $python_version,
              $python_apache_package,
              $user) {

  ensure_packages('mongodb')
  class { 'apache':
    default_vhost => false,
  }

  class { 'python':
    version    => "python${python_version}",
    pip        => 'present',
    dev        => 'present',
    virtualenv => 'present',
  }

  ensure_packages($python_apache_package)

  class { 'apache::mod::wsgi':
    mod_path     => "mod_wsgi.so-${python_version}",
    package_name => $python_apache_package,
  }
 
  user { $user:
    ensure => present,
  }

  file { $app_root:
    ensure  => directory,
    owner   => $user,
  }

  vcsrepo { $app_root:
    ensure   => latest,
    revision => $app_version,
    provider => git,
    source   => $repo_url,
    user     => $user,
    require  => File[$app_root],
  }

  file { "${app_root}/app.wsgi":
    content => epp('digital_milliet/app.wsgi.epp', {
      'app_root' => $app_root,
    }),
    require => Vcsrepo[$app_root],
    notify  => Python::Virtualenv[$app_root],
  }

  file { "${app_root}/digital_milliet/config.cfg":
    owner   => $user,
    source  => $config_file,
    mode    => '0644',
    require => Vcsrepo[$app_root],
  }

  python::virtualenv { $app_root:
    ensure       => present,
    version      => '3',
    requirements => "${app_root}/requirements.txt",
    venv_dir     => "${app_root}/venv",
    cwd          => $app_root,
  }

  apache::vhost { 'digital_milliet':
    servername                  => $vhost,
    port                        => '80',
    docroot                     => $app_root,
    wsgi_daemon_process         => 'dm',
    wsgi_daemon_process_options => {
      'python-path' => "${app_root}/venv/lib/python${python_version}/site-packages"
    },
    wsgi_process_group          => 'dm',
    wsgi_script_aliases         => { $app_path => "${app_root}/app.wsgi" },
    directories                 => [
      { 'path'    => $app_root,
        'require' => 'all granted'
      }
    ],
    headers                     => [
      "set Access-Control-Allow-Origin '*'",
      "set Access-Control-Allow-Headers 'Origin, X-Requested-With, Content-Type, Accept'"
    ]
  }

  apache::vhost { 'digital_milliet-ssl':
    servername                  => $vhost, 
    port                        => '443',
    docroot                     => $app_root,
    ssl                         => true,
    ssl_cert                    => $ssl_cert,
    ssl_key                     => $ssl_private_key,
    ssl_chain                   => $ssl_chain,
    wsgi_daemon_process         => 'dm-ssl',
    wsgi_daemon_process_options => {
      'python-path' => "${app_root}/venv/lib/python3.4/site-packages"
    },
    wsgi_process_group          => 'dm-ssl',
    wsgi_script_aliases         => { $app_path => "${app_root}/app.wsgi" },
    directories                 => [
      { 'path'    => $app_root,
        'require' => 'all granted'
      }
    ],
    headers                     => [
      "set Access-Control-Allow-Origin '*'",
      "set Access-Control-Allow-Headers 'Origin, X-Requested-With, Content-Type, Accept'"
    ]
  }

  firewall { '100 Allow web traffic for digital_milliet':
    proto  => 'tcp',
    dport  => '80',
    action => 'accept',
  }

  firewall { '100 Allow ssltraffic for digital_milliet':
    proto  => 'tcp',
    dport  => '443',
    action => 'accept',
  }

  cron { 'dump-mongo':
    command => "/usr/bin/mongodump -o ${backup_dir} >/var/log/mongodump.log 2>&1",
    minute  => '45',
    hour    => '*/6',
  }

}
