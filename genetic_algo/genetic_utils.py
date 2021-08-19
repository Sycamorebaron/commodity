import sys

system = sys.platform

if system.startswith('win'):
    continuous_contract_path = r'D:\commodity\data\continuous_contract'
    factor_path = r'C:\1d_factor'
elif system.startswith('linux'):
    continuous_contract_path = r'/home/sycamore/PycharmProjects/commodity/data/continuous_contract'
    factor_path = r'/home/sycamore/1d_factor'

