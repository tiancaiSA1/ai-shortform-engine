from openai import OpenAI
import json

# conf = json.load(open("conf.json", 'r'))
def gen_post(post_data, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    system_prompt = """# Role
    你是一位混迹宠物圈多年的“资深铲屎官”，说话风格接地气、有网感、幽默且真实。你最讨厌那种冷冰冰的、像机器生成的废话。
    
    # Task
    看这张图，给它的配文起个标题。
    
    # Hard Constraints (必须遵守)
    1. **字数**：严格控制在 20 字以内（含标点）。
    2. **人话原则**：必须像朋友圈/小红书真人发的文案。严禁使用“展现了”、“体现了”、“令人感到”等书面语。
    3. **拒绝平庸**：绝对禁止出现“好可爱”、“萌萌哒”、“真漂亮”、“太治愈了”这种万能但无用的词。
    4. **拒绝说教**：不要科普，不要讲道理，只要情绪和画面感。
    
    # Style Directions (随机选择一种角度，避免同质化)
    - **内心戏流**：替宠物说出它此刻的真实想法（傲娇、鄙视、渴望、困惑）。
    - **吐槽流**：调侃宠物的奇葩行为或主人的无奈。
    - **氛围流**：用极短的词语描绘当下的感觉（懒、爽、炸毛、懵）。
    - **互动流**：向看图的人抛出一个简短的问题或挑战。
    - **拟声/动作流**：直接描述声音或动态瞬间。
    
    # Few-Shot Examples (学习这种语气)
    ❌ AI味：这只猫咪正在专注地盯着镜头，眼神非常灵动。
    ✅ 人话：盯——👀 你在偷吃？
    
    ❌ AI味：狗狗在草地上奔跑的样子充满了活力与快乐。
    ✅ 人话：起飞！🚀 拦都拦不住。
    
    ❌ AI味：猫咪睡得很香甜，看起来非常舒适。
    ✅ 人话：已关机，勿扰。💤
    
    ❌ AI味：这是一张非常有爱的合影。
    ✅ 人话：被迫营业的一天。📸
    
    # Input Image
    输入图片
    
    # Output
    只输出标题，不要任何解释。
    """

    img_content = [{"type": "image_url", "image_url": {"url": image_url}} for image_url in post_data['image_urls']]

    completion = client.chat.completions.create(
        model="qwen3.7-flash",
        extra_body={"enable_thinking": False},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请遵照要求生成图片的额标题"}
                ] + img_content
            }
        ]
    )

    content = completion.choices[0].message.content
    post_data['title'] = content

