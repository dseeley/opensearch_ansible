# opensearch-ansible

This Ansible role is used to provision opensearch and opensearch-dashboards

This project can operate in isolation, but is designed to operate using [clusterverse](https://github.com/dseeley/clusterverse) to manage the base infrastructure.  Please see the [README.md](https://github.com/dseeley/clusterverse/blob/master/README.md) there for instructions on deployment. 

Please see the EXAMPLE directory in this repository for some basic configuration.

## EXAMPLE:

### Configuration
Cluster configuration is stored in `cluster_defs/**/cluster_vars[*].yml` files.
Application configuration is stored in `cluster_defs/**/app_vars.yml` files.

### Playbook execution
`cluster.yml` is included that is compatible with [clusterverse](https://github.com/dseeley/clusterverse).

`redeploy.yml` is included that functions only in conjunction with [clusterverse](https://github.com/dseeley/clusterverse).


### Invocation
To create a cluster:
```
ansible-playbook cluster.yml -e cloud_type=aws -e region=eu-west-1 -e buildenv=dev
```

To redeploy a cluster
```
ansible-playbook redeploy.yml -e cloud_type=aws -e region=eu-west-1 -e buildenv=dev -e canary=none
```

To delete a cluster
```
ansible-playbook cluster.yml -e cloud_type=aws -e region=eu-west-1 -e buildenv=dev --tags=clusterverse_clean -e clean=_all_
```