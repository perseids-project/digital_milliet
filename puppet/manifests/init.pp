# Puppet configuration for Digital Milliet
class digital_milliet($app_root,
              $app_path,
              $app_version,
              $repo_url, 
              $vhost,
              $ssl_cert,
              $ssl_chain,
              $ssl_private_key) {
  include digital_milliet::python3
  include digital_milliet::node 

  ensure_packages('mongodb')

  file { "/etc/ssl/certs/${ssl_cert}":
    source => "puppet:///modules/site/ssl/${ssl_cert}",
  }

  file { "/etc/ssl/certs/${ssl_chain}":
    source => "puppet:///modules/site/ssl/${ssl_chain}",
  }

  file { "/etc/ssl/private/${ssl_private_key}":
    source => "puppet:///modules/site/ssl/${ssl_private_key}",
    mode   => '0640',
  }

  file { $app_root:
    ensure  => directory,
  }

  vcsrepo { $app_root:
    ensure   => latest,
    revision => $app_version,
    provider => git,
    source   => $repo_url,
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
    source  => 'puppet:///modules/digital_milliet/config.cfg',
    mode    => '0644',
    require => Vcsrepo[$app_root],
  }

  file { '/usr/local/bin/build-dm-js':
    content => epp('digital_milliet/build-dm-js.sh.epp',
    {
      'node_version' => '0.10.46'
    mode    => '0775',
  }

  exec { 'dm-bower':
    cwd     => "${app_root}/digital_milliet",
    command => 'bash --login "/usr/local/bin/build-dm-js"',
    require => [File['/usr/local/bin/build-dm-js'],Vcsrepo[$app_root]],
    creates => "${app_root}/digital_milliet/bower_components"
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
      'python-path' => "${app_root}/venv/lib/python3.4/site-packages"
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
    ssl_cert                    => "/etc/ssl/certs/${ssl_cert}",
    ssl_key                     => "/etc/ssl/private/${ssl_private_key}",
    ssl_chain                   => "/etc/ssl/certs/${ssl_chain}",
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
  firewall { '100 Allow py for digital_milliet':
    proto  => 'tcp',
    dport  => '5000',
    action => 'accept',
  }

  cron { 'dump-mongo':
    command => '/usr/bin/mongodump -o /usr/local/mongo_backup >/var/log/mongodump.log 2>&1',
    minute  => '45',
    hour    => '*/6',
  }

}
