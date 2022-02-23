# Ansible Collection - dseeley.ansible_vault_pipe

> *Note*: This plugin is included locally (rather than via galaxy) because plugins cannot be loaded dynamically at runtime (https://github.com/ansible/ansible/issues/72235) 

An Ansible action plugin to perform vault encrypt/decrypt operations inside a playbook.  Can use either user-provided id/pass, or can use already-loaded vault secrets.

## parameters:
+ `action`: [encrypt|decrypt]
+ `vaultid`: The vault-id if this is (or will be) associated with one. (optional)
+ `vaultpass`: The vault password (the current password for action: decrypt, the desired for action: encrypt).  If this is not provided, will attempt to use the already-loaded secrets (command-line or vault script).
+ `vaulttext`: (decrypt-only) the vault text to be decrypted
+ `plaintext`: (encrypt-only) the plain text to be encrypted
+ `multiline_out`: (encrypt-only) whether to break the encrypted ciphertext into 80-character lines (as ansible-vault encrypt does).  Default: no


## Execution
```yaml
- name: Encrypt using user-provided vaultid and vaultpass
  ansible_vault_pipe:
    action: encrypt
    vaultid: sandbox
    vaultpass: asdf
    plaintext: "sometext"
  register: r__ansible_vault_encrypt
- debug: msg={{r__ansible_vault_encrypt}}

- name: Decrypt using user-provided vaultid and vaultpass
  ansible_vault_pipe:
    action: decrypt
    vaultid: sandbox
    vaultpass: asdf
    vaulttext: "$ANSIBLE_VAULT;1.2;AES256;sandbox\n303562383536366435346466313764636533353438653463373765616365623130333633613139326235633064643338316665653531663030643139373131390a323233356239303864343336663238616535386638646566623036383130643638373465646331316664636564376161376137623432616561343631313262620a3561656131353364616136373866343963626561366236653538633734653165"
  register: r__ansible_vault_decrypt
- debug: msg={{r__ansible_vault_decrypt}}

- name: Encrypt using already-loaded vault secrets (from command-line, ansible.cfg etc)
  ansible_vault_pipe:
    action: encrypt
    multiline_out: yes
    plaintext: "sometext"
  register: r__ansible_vault_encrypt
- debug: msg={{r__ansible_vault_encrypt}}

- name: Decrypt using already-loaded vault secrets (from command-line, ansible.cfg etc)
  ansible_vault_pipe:
    action: decrypt
    vaulttext: "$ANSIBLE_VAULT;1.2;AES256;sandbox\n303562383536366435346466313764636533353438653463373765616365623130333633613139326235633064643338316665653531663030643139373131390a323233356239303864343336663238616535386638646566623036383130643638373465646331316664636564376161376137623432616561343631313262620a3561656131353364616136373866343963626561366236653538633734653165"
  register: r__ansible_vault_decrypt
- debug: msg={{r__ansible_vault_decrypt}}
```
