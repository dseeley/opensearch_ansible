# Copyright 2022 Dougal Seeley <github@dougalseeley.com>
# BSD 3-Clause License

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.parsing.vault import VaultLib, VaultSecret, parse_vaulttext_envelope, parse_vaulttext
from ansible.utils.display import Display

display = Display()


#################################
# An action plugin to perform vault encrypt/decrypt operations inside a playbook.  Can use either user-provided id/pass, or will otherwise try to use already-loaded vault secrets.
# parameters:
#   action: [encrypt|decrypt]
#   vaultid: The vault-id if this is (or will be) associated with one. (optional)
#   vaultpass: The vault password (the current password for action: decrypt, the desired for action: encrypt).  If this is not provided, will attempt to use the already-loaded secrets (command-line or vault script).
#   vaulttext: (decrypt-only) - the vault text to be decrypted
#   plaintext: (encrypt-only) - the plain text to be encrypted
#   multiline_out: (encrypt-only) - whether to break the encrypted ciphertext into 80-character lines (as ansible-vault encrypt does).  Default: no
#################################
#
# - name: Encrypt using user-provided vaultid and vaultpass
#   ansible_vault_pipe:
#     action: encrypt
#     vaultid: sandbox
#     vaultpass: asdf
#     plaintext: "sometext"
#   register: r__ansible_vault_encrypt
# - debug: msg={{r__ansible_vault_encrypt}}
#
# - name: Decrypt using user-provided vaultid and vaultpass
#   ansible_vault_pipe:
#     action: decrypt
#     vaultid: sandbox
#     vaultpass: asdf
#     vaulttext: "$ANSIBLE_VAULT;1.2;AES256;sandbox\n303562383536366435346466313764636533353438653463373765616365623130333633613139326235633064643338316665653531663030643139373131390a323233356239303864343336663238616535386638646566623036383130643638373465646331316664636564376161376137623432616561343631313262620a3561656131353364616136373866343963626561366236653538633734653165"
#   register: r__ansible_vault_decrypt
# - debug: msg={{r__ansible_vault_decrypt}}
#
# - name: Encrypt using already-loaded vault secrets (from command-line, ansible.cfg etc)
#   ansible_vault_pipe:
#     action: encrypt
#     multiline_out: yes
#     plaintext: "sometext"
#   register: r__ansible_vault_encrypt
# - debug: msg={{r__ansible_vault_encrypt}}
#
# - name: Decrypt using already-loaded vault secrets (from command-line, ansible.cfg etc)
#   ansible_vault_pipe:
#     action: decrypt
#     vaulttext: "$ANSIBLE_VAULT;1.2;AES256;sandbox\n303562383536366435346466313764636533353438653463373765616365623130333633613139326235633064643338316665653531663030643139373131390a323233356239303864343336663238616535386638646566623036383130643638373465646331316664636564376161376137623432616561343631313262620a3561656131353364616136373866343963626561366236653538633734653165"
#   register: r__ansible_vault_decrypt
# - debug: msg={{r__ansible_vault_decrypt}}
#
#################################

class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp is deprecated

        # If user supplies vault-id and vault-pass, use them.  Otherwise use those that are automatically loaded with the playbook
        if 'vaultpass' in self._task.args:
            oVaultSecret = VaultSecret(self._task.args["vaultpass"].encode('utf-8'))
            if 'vaultid' in self._task.args:
                oVaultLib = VaultLib([(self._task.args["vaultid"], oVaultSecret)])
            else:
                display.v(u'No vault-id supplied, using default identity.')
                oVaultLib = VaultLib([(C.DEFAULT_VAULT_IDENTITY, oVaultSecret)])
        else:
            display.v(u'No vault-id or vault-pass supplied, using playbook-sourced variables.')
            oVaultLib = self._loader._vault
            if len(self._loader._vault.secrets) == 0:
                display.warning("No Vault secrets loaded by config and none supplied to plugin.  Vault operations are not possible.")

        if self._task.args["action"] == "encrypt":
            if "plaintext" not in self._task.args:
                return {"failed": True, "msg": "'plaintext' is required for encrypt."}

            b_vaulttext = oVaultLib.encrypt(self._task.args["plaintext"])
            b_ciphertext, b_version, cipher_name, vault_id = parse_vaulttext_envelope(b_vaulttext)

            vaulttext_header = b_vaulttext.decode('utf-8').split('\n', 1)[0]
            ciphertext = b_ciphertext.decode('utf-8')

            if 'multiline_out' in self._task.args and self._task.args["multiline_out"] == True:
                multiline_length = 80
                ciphertext = '\n'.join([ciphertext[i:i + multiline_length] for i in range(0, len(ciphertext), multiline_length)])

            result['vaulttext'] = vaulttext_header + "\n" + ciphertext
            result['plaintext'] = self._task.args["plaintext"]

        else:
            if "vaulttext" not in self._task.args:
                return {"failed": True, "msg": "'vaulttext' is required for decrypt."}

            plaintext = oVaultLib.decrypt(self._task.args["vaulttext"])
            result['vaulttext'] = self._task.args["vaulttext"]
            result['plaintext'] = plaintext

        result['failed'] = False

        return result
