Introduction
------------

This repository provides the foundation for working with the F5 XC CLoud Modules for Ansible.
The architecture of the modules makes inherent use of the F5 XC Cloud REST APIs.

This repository is an **incubator** for Ansible modules. The modules in this repository **may be
broken due to experimentation or refactoring**.

The F5 XC Cloud Modules for Ansible are freely provided to the open source community for automating F5 XC Cloud configurations.


Installing the Build
----------------------------

```shell

    # Approach 1
    # To install build from the repository
    git clone git@github.com:yoctoalex/xc-cloud-ansible.git
    cd ./xc-cloud-ansible
    ansible-galaxy collection build --force
    ansible-galaxy collection install yoctoalex-xc_cloud_modules-0.0.6.tar.gz 

    # Approach 2
    # To install from the Ansible Galaxy
    ansible-galaxy collection install yoctoalex.xc_cloud_modules 
```

Usage Example
----------------------------
```yaml
- name: Create Virtual Kubernetes
  hosts: webservers
  collections:
    - yoctoalex.xc_cloud_modules
  connection: local

  environment:
    XC_API_TOKEN: "your_api_token"
    XC_TENANT: "console.ves.volterra.io"

  tasks:
    - name: create vk8s
      virtual_kubernetes:
        state: present
        wait: True
        metadata:
          namespace: "default"
          name: "demo-vk8s"
        spec:
          vsite_refs:
            - kind: "virtual_site"
              tenant: "ves-io"
              namespace: "shared"
              name: "ves-io-all-res"
```


**NOTE:** "-p" is the location in which the collection will be installed. This location should be defined in the path for
ansible to search for collections. An example of this would be adding ``collections_paths = ./collections``
to your **ansible.cfg**

Bugs, Issues
------------

Please file any bugs, questions, or enhancement requests by using GitHub Issues
