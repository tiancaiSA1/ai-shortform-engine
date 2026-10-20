import json
import random

def generate_digit_number():
    # 第一位：1~9
    first = random.randint(1, 9)
    # 后面19位：0~9
    rest = [random.randint(0, 9) for _ in range(17)]
    # 拼接成字符串
    num_str = str(first) + ''.join(str(x) for x in rest)
    return num_str

def generate_ver_code():
    rest = [random.randint(0, 9) for _ in range(6)]
    # 拼接成字符串
    num_str = ''.join(str(x) for x in rest)
    return num_str

# # 调用示例
# res = generate_20digit_number()
# print(res)

phone_numbers = {}

for i in range(300):
    phone_numbers[generate_digit_number()] = generate_ver_code()

# print(len(phone_numbers))
with open('s_phone_numbers.json', 'w') as ff, open('s_phone_numbers.txt', 'w') as ffs:
    json.dump(phone_numbers, ff)
    for phone_number in phone_numbers:
        ffs.write(f'{phone_number}\t{phone_numbers[phone_number]}\n')



