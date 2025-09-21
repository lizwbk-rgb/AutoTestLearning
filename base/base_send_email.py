#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送封装模块
--------------------------------------------------
支持功能
1. 发送纯文本 / HTML 正文
2. 携带附件（Allure 压缩包、HTML 报告、XML 报告）
3. 自动根据端口选择 SSL 或 STARTTLS
--------------------------------------------------
"""

import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 项目内部公共库
from base.base_path import BasePath as BP
from utils import read_config_ini, make_zip


class HandleEmail(object):
    """
    邮件发送类
    配置来源：config.ini → [邮件发送配置]
    """

    def __init__(self):
        # 读取全局配置文件
        config = read_config_ini(BP.CONFIG_FILE)
        email_config = config['邮件发送配置']

        # 基本连接信息
        self.host = email_config['host']          # SMTP 服务器地址
        self.port = int(email_config['port'])     # SMTP 端口（465/587/25）
        self.sender = email_config['sender']      # 登录账号
        self.from_email = email_config['send_email']  # 发件人邮箱（可能同 sender）
        self.receiver = eval(email_config['receiver'])  # 收件人列表，配置中是字符串，需要 eval 成 list
        self.password = email_config['password']  # 登录授权码/密码
        self.subject = email_config['subject']    # 邮件主题

    # ------------------------------------------------------------------
    # 构造邮件内容组件
    # ------------------------------------------------------------------
    def add_text(self, text):
        """生成纯文本 MIMEText 对象"""
        return MIMEText(text, 'plain', 'utf-8')

    def add_html_text(self, html):
        """生成 HTML 格式 MIMEText 对象"""
        return MIMEText(html, 'html', 'utf-8')

    def add_accessory(self, file_path):
        """
        生成附件对象
        参数
        ----
        file_path : str
            待添加文件的绝对路径
        返回
        ----
        MIMEText
            可用于 attach 的附件对象
        """
        resource = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        # 设置附件头，filename 会显示在邮件客户端
        resource.add_header('Content-Disposition', 'attachment',
                            filename=os.path.basename(file_path))
        return resource

    # ------------------------------------------------------------------
    # 组装完整邮件
    # ------------------------------------------------------------------
    def add_subject_attachment(self, attach_info: tuple, send_date=None):
        """
        创建 MIMEMultipart 对象，加入主题、发件人、收件人、日期及所有附件

        参数
        ----
        attach_info : tuple
            由各类 MIMEText / MIMEApplication 对象组成的元组
        send_date : str, optional
            自定义发送日期（RFC 5322 格式），默认取当前时间
        返回
        ----
        MIMEMultipart
            可直接用于 sendmail 的完整邮件对象
        """
        msg = MIMEMultipart('mixed')  # 混合型，可同时存在文本与附件
        msg['Subject'] = self.subject
        msg['From'] = '{0} <{1}>'.format(self.sender, self.from_email)
        msg['To'] = ";".join(self.receiver)

        # 设置发送日期
        if send_date:
            msg['Date'] = send_date
        else:
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        # 逐个加入附件
        if isinstance(attach_info, tuple):
            for attach in attach_info:
                if attach:          # 防止 None 导致异常
                    msg.attach(attach)
        return msg

    # ------------------------------------------------------------------
    # 真正发送
    # ------------------------------------------------------------------
    def send_email(self, msg):
        """
        连接 SMTP 服务器并发送邮件

        参数
        ----
        msg : MIMEMultipart
            已完成组装的邮件对象
        """
        smtp = None
        try:
            # 根据端口自动选择 SSL 或 STARTTLS
            if self.port == 587:  # STARTTLS
                smtp = smtplib.SMTP(self.host, self.port)
                smtp.starttls()
            else:  # 465 或其它 SSL 端口
                smtp = smtplib.SMTP_SSL(self.host, self.port)

            # 登录并发送
            smtp.login(self.sender, self.password)
            smtp.sendmail(self.from_email, self.receiver, msg.as_string())
            print(f'{self.from_email} 发送成功 {datetime.now()}')
        except Exception as e:
            print(f'发送失败: {e}')
            raise  # 重新抛出，方便上层感知
        finally:
            if smtp:
                try:
                    smtp.quit()
                except:
                    # 部分服务器 quit 阶段可能抛异常，忽略即可
                    pass

    # ------------------------------------------------------------------
    # 一键发送公共邮件
    # ------------------------------------------------------------------
    def send_public_email(self, send_date=None, _text='', html='', file_type=''):
        """
        快速发送测试报告邮件

        参数
        ----
        send_date : str, optional
            自定义发送日期
        _text : str
            纯文本正文
        html : str
            HTML 正文（可选）
        file_type : str
            附件类型：'ALLURE' | 'HTML' | 'XML'，空串表示不带附件
        """
        attach_info = []

        # 1. 加入纯文本
        text_plain = self.add_text(_text)
        attach_info.append(text_plain)

        # 2. 加入 HTML
        if html:
            text_html = self.add_html_text(html)
            attach_info.append(text_html)

        # 3. 加入附件
        file_attach = None
        if file_type == 'ALLURE':
            # 先压缩 Allure 报告目录
            allure_zip = make_zip(BP.ALLURE_REPORT_DIR,
                                  os.path.join(BP.ALLURE_REPORT_DIR, 'allure.zip'))
            file_attach = self.add_accessory(allure_zip)
        elif file_type == 'HTML':
            file_attach = self.add_accessory(
                os.path.join(BP.HTML_DIR, 'autoTest_report.html'))
        elif file_type == 'XML':
            file_attach = self.add_accessory(
                os.path.join(BP.XML_DIR, 'autoTest_report.xml'))
        attach_info.append(file_attach)

        # 4. 组装并发送
        msg = self.add_subject_attachment(tuple(attach_info), send_date=send_date)
        self.send_email(msg)


# ----------------------------------------------------------------------
# 本地调试入口
# ----------------------------------------------------------------------
if __name__ == '__main__':
    text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好！以下是本次测试报告。'
    HandleEmail().send_public_email(send_date=None, _text=text, html='', file_type='HTML')