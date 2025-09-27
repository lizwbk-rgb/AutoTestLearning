import paramiko


class SSH(object):

    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    def cmd(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            content = stdout.read().decode('utf-8')
            result = content.split('\n')
            ssh.close()
            return result
        except Exception as e:
            print('远程执行shell命令失败！！！', e)
            return False

    def upload(self, local_path, remote_path):
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(local_path, remote_path)
            transport.close()
            print('文件上传成功，上传路径：{}'.format(remote_path))
            return True
        except Exception as e:
            print('文件上传失败！！！', e)
            return False

    def download(self, local_path, remote_path):
        try:
            transport = paramiko.Transport((self.ip, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(local_path, remote_path)
            transport.close()
            print('文件下载成功，下载路径：{}'.format(local_path))
            return True
        except Exception as e:
            print('文件下载失败！！！', e)
            return False
