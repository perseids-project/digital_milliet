class digital_milliet::node {

  class { 'nvm':
    version => 'v0.33.0',
    user => hiera('digital_milliet::user'),
  }

  nvm::node::install { '0.10.46':
    set_default => false,
    user => hiera('digital_milliet::user'),
  }

}
