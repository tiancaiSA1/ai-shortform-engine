import json
import shutil
import time

import requests

conf = json.load(open("conf.json", 'r'))

basic_url = conf['b_url']

def post(post_data):
    responses = requests.post(
        f"{basic_url}/account_sys/get_basic_msg_of_user",
        json={}, headers={"X-User-ID": post_data['token']})
    status_code = responses.status_code
    if status_code != 200:
        print("get id error")
        return None
    unique_random_id = responses.json()['unique_random_id']

    responses = requests.post(
        f"{basic_url}/community/push_feed",
        json={
            "pic_url_list": post_data['image_urls'],
            "text": "",
            "visibility_type": "公开可见",
            "title": post_data['title'],
            "tags": ["宠物"],
            "author_unique_id": unique_random_id
        }, headers={"X-User-ID": post_data['token']})

    status_code = responses.status_code
    if status_code != 200:
        print("push vercode error")
        return None
    feed_id = responses.json()['feed_id']
    print(f"feed_id:{feed_id}")
    return 1


if __name__ == '__main__':
    _post_data = json.load(open("now_process/wait_for_post.json", 'r', encoding="utf-8"))
    result = post(_post_data)
    if result is not None:
        _post_data['already_post_record'] = _post_data['max_num']
        _post_data['last_post_ts'] = int(time.time())
        json.dump(_post_data, open(f"{_post_data['local_path']}/already_post_js.json", 'w', encoding="utf-8"), ensure_ascii=False, indent=2)

