# Install Python 3 and mod_wsgi
class digital_milliet::python3 {
  class { 'apache':
    default_vhost => false,
  }

  class { 'python':
    version    => 'python3',
    pip        => 'present',
    dev        => 'present',
    virtualenv => 'present',
  }

  ensure_packages('libapache2-mod-wsgi-py3')

  class { 'apache::mod::wsgi':
    mod_path     => 'mod_wsgi.so-3.4',
    package_name => 'libapache2-mod-wsgi-py3',
  }
}
