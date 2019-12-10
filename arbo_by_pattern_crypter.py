# coding: utf8
# works on python3.6+


from aggregator import Aggregator
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from logger import Clogger


LOGGING_LEVEL = 0
SALT = b'0123456789'*4
KEY = 'ma clé envoie du pâté'


class PyHasher:
    def __init__(self, PATH, pattern, passw, salt, mode):
        self.path = PATH
        self.pattern = pattern
        self.aggregator = Aggregator
        self.logger = Clogger(log_level=LOGGING_LEVEL, environ=7).get_logger()
        self.passw = passw.encode()
        self.mode = mode
        self.kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        self.key=base64.urlsafe_b64encode(self.kdf.derive(self.passw))
        self.fernet = Fernet(key=self.key)
        self.results=[]
        self.mode_checker()

    def mode_checker(self):
        assert self.mode in ['crypt', 'decrypt'], "unknown mode"
        assert self.passw, "need password to proceed"

    def return_str_from_file(self, filepath):
        mode = 'r' if self.mode == "crypt" else "rb" # todo maybe full rb
        with open(filepath, mode) as f:
            r = f.read()
        return r

    def write_str_in_file_return_filepath(self, string, filepath):
        mode = 'wb' if self.mode == "crypt" else "wb"
        with open(filepath, mode) as f:
            f.write(string)
        return filepath

    def routine(self):
        self. aggregator = self.aggregator(path_to_files=self.path, pattern=self.pattern)
        if self.aggregator.testfiles_list:
            self.logger.info("%s files in pipe. Proceeding..." % len(self.aggregator.testfiles_list))
            for elem in self.aggregator.testfiles_list:
                self.logger.info("working on %s" % elem)
                elem_path, elem_name = self.from_path_return_splitted_path_and_filename(elem)
                crypted_name = self.generate_name(elem_name)
                current_string = self.return_modded_string(self.return_str_from_file(elem))
                crypted_file = self.write_str_in_file_return_filepath(string=current_string,
                                                                      filepath=elem_path + crypted_name)
                self.results.append(crypted_file)
            print("---RESULTS---")
            for elem in self.results:
                print(elem)
        else:
            raise RuntimeError('no file matching pattern')

    def from_path_return_splitted_path_and_filename(self, filepath):
        path=""
        brute_path = [x for x in filepath.split("/")[:-1]]
        for elem in brute_path:
            path += elem + '/'
        return path, filepath.split('/')[-1:][0]

    def generate_name(self, filename):
        mode = "_CRYPT_" if self.mode == "crypt" else "_DECRYPTED_"
        if self.pattern in filename:
            return filename.replace(self.pattern, mode + "0_" + self.pattern)
        else:
            return mode + "1_" + filename

    def str_to_bytes(self, string):
        return string.encode()

    def bytes_to_str(self, string):
        if type(string)==bytes:
            return string.decode('utf-8')
        else:
            return string

    def return_modded_string(self, string):
        mode_string = ""
        if self.mode == 'crypt':
            if type(string) == str:
                string = self.str_to_bytes(string)
            mode_string = self.fernet.encrypt(string)
        else:
            if type(string) == bytes:
                mode_string = self.fernet.decrypt(string)
            elif type(string) == str:
                string = self.str_to_bytes(string)
                mode_string = self.fernet.decrypt(string)
        return mode_string


if __name__ == '__main__':
    from os import getcwd
    p = PyHasher(PATH=getcwd(), pattern="**/*.py", passw=KEY, mode="crypt", salt=SALT)
    p.routine()
    q = PyHasher(PATH=getcwd(), pattern="**/*_CRYPT_*.py",passw=KEY, mode="decrypt", salt=SALT)
    q.routine()
