'''
An encryption plugin for Elixir utilizing the excellent PyCrypto library, which
can be downloaded here: http://www.amk.ca/python/code/crypto

Values for columns that are specified to be encrypted will be transparently
encrypted and safely encoded for storage in a unicode column using the powerful
and secure Blowfish Cipher using a specified "secret" which can be passed into
the plugin at class declaration time.

Example usage:

.. sourcecode:: python

    from elixir import *
    from elixir.ext.encrypted import acts_as_encrypted

    class Person(Entity):
        name = Field(Unicode)
        password = Field(Unicode)
        ssn = Field(Unicode)
        acts_as_encrypted(for_columns=['password', 'ssn'],
                          with_secret='secret')

The above Person entity will automatically encrypt and decrypt the password and
ssn columns on save, update, and load.  Different secrets can be specified on
an entity by entity basis, for added security.
'''

from Crypto.Cipher          import Blowfish
from elixir.statements      import Statement
from sqlalchemy.orm         import MapperExtension, EXT_CONTINUE

__all__ = ['acts_as_encrypted']
__doc_all__ = []


#
# encryption and decryption functions
#

def encrypt_value(value, secret):
    return Blowfish.new(secret, Blowfish.MODE_CFB) \
                   .encrypt(value).encode('string_escape')

def decrypt_value(value, secret):
    return Blowfish.new(secret, Blowfish.MODE_CFB) \
                   .decrypt(value.decode('string_escape'))


try:
    from sqlalchemy.orm import EXT_PASS
    SA05orlater = False
except ImportError:
    SA05orlater = True

#
# acts_as_encrypted statement
#

class ActsAsEncrypted(object):

    def __init__(self, entity, for_fields=[], with_secret='abcdef'):

        def perform_encryption(instance, decrypt=False):
            for column_name in for_fields:
                current_value = getattr(instance, column_name)
                if current_value:
                    if decrypt:
                        new_value = decrypt_value(current_value, with_secret)
                    else:
                        new_value = encrypt_value(current_value, with_secret)
                    setattr(instance, column_name, new_value)

        def perform_decryption(instance):
            perform_encryption(instance, decrypt=True)

        class EncryptedMapperExtension(MapperExtension):

            def before_insert(self, mapper, connection, instance):
                perform_encryption(instance)
                return EXT_CONTINUE

            def before_update(self, mapper, connection, instance):
                perform_encryption(instance)
                return EXT_CONTINUE

        if SA05orlater:
            def reconstruct_instance(self, mapper, instance):
                perform_decryption(instance)
                return True
            EncryptedMapperExtension.reconstruct_instance = reconstruct_instance
        else:
            def populate_instance(self, mapper, selectcontext, row, instance,
                                  *args, **kwargs):
                mapper.populate_instance(selectcontext, instance, row,
                                         *args, **kwargs)
                perform_decryption(instance)
                return True
            EncryptedMapperExtension.populate_instance = populate_instance

        # make sure that the entity's mapper has our mapper extension
        entity._descriptor.add_mapper_extension(EncryptedMapperExtension())


acts_as_encrypted = Statement(ActsAsEncrypted)

