import os
import io
import random
import time
import shutil
import subprocess


class SystemOperation:

    @staticmethod
    def popen_cmd(cmd, buffering=-1):
        if not isinstance(cmd, str):
            raise TypeError('cmd must be a string')
        if buffering == 0 or buffering is None:
            raise TypeError("popen() does not support unbuffered streams")
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   bufsize=buffering)
        print('CMD命令: {}--执行成功！'.format(cmd))
        return os._wrap_close(io.TextIOWrapper(process.stdout), process)
