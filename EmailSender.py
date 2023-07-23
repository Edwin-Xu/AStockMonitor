# coding=UTF-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 发送多种类型的邮件
from email.mime.multipart import MIMEMultipart


def send_email(receivers, subject, content):
    msg_from = '1603837506@qq.com'  # 发送方邮箱
    passwd = 'znsjtgozdjtchfdj'  # 就是上面的授权码
    to = [receivers] if type(receivers) == 'string' else receivers   # 接受方邮箱

    # 设置邮件内容
    # MIMEMultipart类可以放任何内容
    msg = MIMEMultipart()
    # 把内容加进去
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    # 设置邮件主题
    msg['Subject'] = subject
    # 发送方信息
    msg['From'] = msg_from

    # 开始发送
    # 通过SSL方式发送，服务器地址和端口
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    # 登录邮箱
    s.login(msg_from, passwd)
    # 开始发送
    s.sendmail(msg_from, to, msg.as_string())
