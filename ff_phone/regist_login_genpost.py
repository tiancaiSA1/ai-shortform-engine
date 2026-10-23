import json
import requests
import os
import gen_post
import shutil

# basic_url = "https://cw.kizstech.com"
conf = json.load(open("conf.json", 'r'))
basic_url = conf['b_url']

def get_img_datas(folder_path: str, already_post_record: int):
    _max_num = 0
    _num_img_pathlist = {}
    for fname in os.listdir(folder_path):
        if fname.endswith(".png") or fname.endswith(".jpg"):
            num = int(fname.split('.')[0].split("-")[0])
            if _max_num <= num < already_post_record:
                _max_num = num
            if num not in _num_img_pathlist:
                _num_img_pathlist[num] = []
            _num_img_pathlist[num].append(f"{folder_path}/{fname}")
    if _max_num in _num_img_pathlist:
        return _num_img_pathlist[_max_num], _max_num
    else:
        return None, None


def get_post_phone_datas():
    active_s_phone_numbers = {}
    with open("basic/pic_record.txt", "r", encoding="utf-8") as fb:
        fb.readline()
        for line in fb:
            lc = line.strip('\n').split('\t')
            if len(lc) == 10:
                phone_number, vercode, _, b_path, breed, notes, pwd, nickname, gender, is_close = lc
                if len(b_path) > 0:
                    local_path = f"D:/work/ccc/{b_path}"
                    already_post_js_path = f"{local_path}/already_post_js.json"
                    if os.path.exists(already_post_js_path):
                        already_post_js = json.load(open(already_post_js_path, 'r', encoding="utf-8"))
                        already_post_record = already_post_js['already_post_record']
                        last_post_ts = already_post_js['last_post_ts']
                    else:
                        already_post_record = 999999
                        last_post_ts = -1
                    if is_close == '0':
                        img_pathlist, max_num = get_img_datas(local_path, already_post_record)
                        if img_pathlist:
                            active_s_phone_numbers[phone_number] = {'img_pathlist': img_pathlist, 'max_num': max_num,
                                                                    'last_post_ts': last_post_ts, 'local_path': local_path,
                                                                    'vercode': vercode, 'pwd': pwd, 'nickname': nickname, 'gender': gender}
    post_datas = sorted(active_s_phone_numbers.items(), key=lambda x: x[1]['last_post_ts'], reverse=False)
    post_data = post_datas[0]
    _p_number, _p_datas = post_data
    _p_datas["phone_number"] = _p_number
    return _p_number, _p_datas


def regist_login(post_data, phone_number, password, nickname, gender, vercode):
    responses = requests.post(
        f"{basic_url}/account_sys/phonenumber_sendcode",
        json={"using_type": 10, "phonenumber":phone_number})
    status_code = responses.status_code
    if status_code != 200:
        print("send vercode error")
        return None

    responses = requests.post(
        f"{basic_url}/account_sys/verify_phonenumber_vercode",
        json={"ver_code": vercode, "phonenumber":phone_number})
    status_code = responses.status_code
    if status_code != 200:
        print("verify vercode error")
        return None
    verify_success_token = responses.json()['verify_success_token']

    responses = requests.post(
        f"{basic_url}/account_sys/regist_login_account",
        json={"verify_success_token": verify_success_token, "phonenumber":phone_number})
    status_code = responses.status_code
    if status_code != 200:
        print("login error")
        return None
    login_js = responses.json()
    token = login_js['token']
    if login_js['msg'] == "注册成功":
        responses = requests.post(
            f"{basic_url}/account_sys/set_pwd",
            json={"password": password}, headers={"X-User-ID": token})
        status_code = responses.status_code
        if status_code != 200:
            print("set pwd error")
            return None

    responses = requests.post(
        f"{basic_url}/account_sys/get_basic_msg_of_user",
        json={}, headers={"X-User-ID": token})
    status_code = responses.status_code
    if status_code != 200:
        print("get id error")
        return None
    user_msg = responses.json()
    post_data['unique_random_id'] = user_msg['unique_random_id']
    if user_msg['nickname'].startswith('用户'):
        responses = requests.post(
            f"{basic_url}/account_sys/reg_basic_msg_of_user",
            json={
                "nickname": nickname,
                "gender": gender
            }, headers={"X-User-ID": token})
        status_code = responses.status_code
        if status_code != 200:
            print(f"{responses.text}, update username error")
            return None
    return token


def upload_file(post_data):
    token = post_data['token']

    url = f"{basic_url}/upload/upload_pic"  # 根据你的 Flask 服务器地址和端口进行修改
    img_pathlist = post_data['img_pathlist']
    filename_path = {}
    cc = 0
    for path in img_pathlist:
        if cc >= 3:
            break
        filename_path[f"{cc}.png"] = path
        cc += 1
    files = {}
    for filename in filename_path:
        files[filename] = os.path.getsize(filename_path[filename])

    img_url_list = []
    response = requests.post(url, headers={"X-User-ID": token}, json={"ppj": "community", "files": files}, timeout=120)
    # 检查响应状态码
    if response.status_code == 200:
        output_data = response.json()
        # print("Received output JSON:", output_data)
        upload_presign_result = output_data["upload_presign_result"]
        for filename in upload_presign_result:
            presign_msg = upload_presign_result[filename]
            filepath = filename_path[filename]
            with open(filepath, 'rb') as data:
                # print(presign_msg)
                with requests.put(presign_msg["presign_url"], headers=presign_msg["headers"], data=data) as resp:
                    # print(resp.text)
                    js_data = json.loads(resp.text)
                    img_url_list.append(js_data['cdn_url'])
    else:
        print(response.text)
        print("Request failed with status code:", response.status_code)

    post_data['image_urls'] = img_url_list
    # json.dump(post_data, open("now_process/wait_for_post.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == '__main__':
    tmp_file_path = "now_process/tmp_file"
    if os.path.exists(tmp_file_path):
        shutil.rmtree(tmp_file_path)
    os.mkdir(tmp_file_path)
    s_phone_numbers = json.load(open("basic/s_phone_numbers.json", "r", encoding="utf-8"))

    sel_phone_number, sel_already_post_js = get_post_phone_datas()
    # print(sel_already_post_js)
    sel_token = regist_login(post_data=sel_already_post_js, phone_number=sel_phone_number, password=sel_already_post_js['pwd'],
                             nickname=sel_already_post_js['nickname'], gender=sel_already_post_js['gender'], vercode=sel_already_post_js['vercode'])
    if sel_token is not None:
        sel_already_post_js["token"] = sel_token
    for img_path in sel_already_post_js['img_pathlist']:
        shutil.copy(img_path, f"{tmp_file_path}/{img_path.split("/")[-1]}")
    upload_file(sel_already_post_js)
    gen_post.gen_post(sel_already_post_js, conf['api_key'])
    json.dump(sel_already_post_js, open("now_process/wait_for_post.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

