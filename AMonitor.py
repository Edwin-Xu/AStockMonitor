# coding=UTF-8
# A股监控
import threading
from optparse import OptionParser

from Ashare import *
from EmailSender import *

# 默认配置
default_frequency = '1d'
default_incr_threshold = 1
default_reduce_threshold = -100
default_thread_num = 200


def read_stock_code(path):
    codes = []
    with open(path, 'rb+') as f:
        for line in f.readlines():
            code_name = line.decode('utf-8').strip().split(",")
            code = code_name[0]
            codes.append([code, code_name[1]])
    return codes


monitor_list = []

sh_codes = read_stock_code('./data/sh.txt')
sz_codes = read_stock_code('./data/sz.txt')


# sh_codes = [['600362', '1'], ['600198', '2']]
# print(sh_codes)
# print(sz_codes)

def monitor_part(codes, frequency, incr_threshold, reduce_threshold):
    for code in codes:
        monitor_one(code, frequency, incr_threshold, reduce_threshold)


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def monitor_all(codes, frequency=default_frequency, incr_threshold=default_incr_threshold,
                reduce_threshold=default_reduce_threshold, thread_num=default_thread_num):
    arrs = list_split(codes, thread_num)
    thread_list = []
    for arr in arrs:
        t = threading.Thread(target=monitor_part, args=(arr, frequency, incr_threshold, reduce_threshold))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()


def format_number(n):
    return format(n, '.2f')


def format_str(s, length):
    _len = len(str(s))
    if _len >= length:
        return s
    return " " * (length - _len) + s


def monitor_one(code, frequency, incr_threshold, reduce_threshold):
    # 默认重试3次
    retry_time = 1
    for i in range(0, retry_time):
        try:
            # 按时间段，获取一条记录
            scode = ('sh' if code[0].startswith('6') else 'sz') + code[0]
            df = get_price(scode, frequency=frequency, count=1)

            # 计算该时间段中的涨幅
            open = df['open'][0]
            close = df['close'][0]
            diff = close - open
            diff_rate = (diff / open) * 100
            # print("=======", df, open, close, diff, diff_rate)
            if diff_rate >= incr_threshold or diff_rate <= reduce_threshold:
                res = [code[0], code[1], format_number(open), format_number(close), format_number(diff),
                       format_number(diff_rate)]
                monitor_list.append(res)
            return 1
        except Exception as e:
            # logging.exception(e)
            print(code, e)


def notice(codes):
    if len(codes) == 0:
        return
    scodes = sorted(codes, key=lambda x: float(x[-1]), reverse=True)
    msg_content = "共监控到 {} 只股票:\n".format(len(scodes))
    print(msg_content.strip())
    for code in scodes:
        # 代码:{}, 简称: {}, 开:{}, 收:{}, 涨幅:{}
        code_msg = "{} {} {} {} {}".format(code[0], code[1], format_str(code[2], 6),
                                           format_str(code[3], 6),
                                           format_str(code[-1], 5))
        msg_content += code_msg + '\n'
        print(code_msg)
    send_email(['1603837506@qq.com', 'edwinxu83@gmail.com'], '股票监控', msg_content)


def monitor(codes, m_type, frequency, incr_threshold, reduce_threshold):
    print("类型: {}, 频率: {}, 增幅: {}, 跌幅: {}".format(m_type, frequency, incr_threshold, reduce_threshold))
    if isinstance(codes, str):
        all_codes = sh_codes + sz_codes
        arr = codes.split(',')
        codes = [x for x in all_codes if x[0] in arr]
    # 如果没有传，则是所有股票
    if not codes:
        codes = sh_codes + sz_codes
    monitor_res = []
    global monitor_list
    monitor_list = []
    monitor_all(codes, frequency, incr_threshold, reduce_threshold, thread_num=default_thread_num)
    monitor_res = monitor_res + monitor_list

    notice(monitor_res)


def get_parser():
    """
    从命令行输入 解析出具体参数
    """
    parser = OptionParser()
    # code, m_type, frequency, incr_threshold, reduce_threshold
    parser.add_option("-c", "--code", help="股票代码")
    parser.add_option("-t", "--type", help="监控类型", default='all')
    parser.add_option("-f", "--frequency", help="查询时间", default='15m')
    parser.add_option("-i", "--incr_threshold", help="涨幅", default=3)
    parser.add_option("-r", "--reduce_threshold", help="跌幅", default="-20")
    return parser


if __name__ == '__main__':

    # 解析参数
    option_parser = get_parser()
    (options, args) = option_parser.parse_args()
    if options.type == 'sh':
        codes = sh_codes
    elif options.type == 'sz':
        codes = sz_codes
    else:
        codes = sh_codes + sz_codes
    if options.code:
        codes = [x for x in codes if x[0] == str(options.code)]
    monitor(codes, options.type, options.frequency, float(options.incr_threshold), float(options.reduce_threshold))
