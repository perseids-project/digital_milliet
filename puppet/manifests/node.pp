class digmill::node {

  class { 'nvm':
    version => 'v0.33.0',
  }

  nvm::node::install { '0.10.46':
    set_default => false,
  }

}
