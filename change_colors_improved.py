#!/usr/bin/env python3
import os
import re

# #1、钢铁侠 Mark III 经典战甲配色 (R G B A) - 这些将涂在外壳上
# color_palette = {
#     "body_link0": "0.75 0.78 0.80 1.0", # 实验室拉丝银：高亮金属银色，像斯塔克工业的测试台底座
#     "link0": "0.78 0.12 0.12 1.0",      # 肩部外壳
#     "link1": "0.78 0.12 0.12 1.0",      # 大臂外壳
#     "link2": "0.85 0.65 0.10 1.0",      # 手肘外壳 (金)
#     "link3": "0.78 0.12 0.12 1.0",      # 小臂外壳
#     "link4": "0.85 0.65 0.10 1.0",      # 腕部上方外壳 (金)
#     "link5": "0.78 0.12 0.12 1.0",      # 腕部外壳
#     "link6": "0.60 0.60 0.65 1.0",      # 机械关节
#     "link7": "0.20 0.85 1.00 1.0",      # 法兰盘（掌心炮）
#     "hand": "0.78 0.12 0.12 1.0",       # 手掌外壳
#     "finger": "0.85 0.65 0.10 1.0",     # 手指
# }
# # 细节关节颜色 - 这些将涂在连接件上
# joint_color = "0.12 0.12 0.12 1.0"  # 碳黑/黑钨色：深邃压抑的内部关节结构

# #2、 赛博朋克风 (R G B A) 
# color_palette = {
#     "body_link0": "0.10 0.10 0.12 1.0", # 黑曜石底座：几乎纯黑，融入背景
#     "link0": "0.15 0.12 0.25 1.0",      # 深夜紫：肩部外壳
#     "link1": "0.15 0.12 0.25 1.0",      # 深夜紫：大臂外壳
#     "link2": "0.95 0.10 0.55 1.0",      # 霓虹粉：手肘点缀（强烈的视觉冲击）
#     "link3": "0.15 0.12 0.25 1.0",      # 深夜紫：小臂外壳
#     "link4": "0.95 0.10 0.55 1.0",      # 霓虹粉：腕部点缀
#     "link5": "0.15 0.12 0.25 1.0",      # 深夜紫：腕部外壳
#     "link6": "0.20 0.20 0.25 1.0",      # 碳纤维灰：机械关节
#     "link7": "0.00 0.90 0.95 1.0",      # 全息蓝：法兰盘（像发光的蓝色霓虹灯）
#     "hand": "0.15 0.12 0.25 1.0",       # 深夜紫：手掌外壳
#     "finger": "0.00 0.90 0.95 1.0",     # 全息蓝：发光的手指
# }
# # 细节关节颜色 
# joint_color = "0.05 0.05 0.05 1.0"  # 极夜黑：让连接件彻底隐形，突出霓虹色

# #3、 现代重工业风 (R G B A) 
# color_palette = {
#     "body_link0": "0.30 0.32 0.35 1.0", # 铸铁灰：稳固的工厂底座
#     "link0": "0.90 0.40 0.05 1.0",      # 安全橘：肩部主色，警示感十足
#     "link1": "0.90 0.40 0.05 1.0",      # 安全橘：大臂外壳
#     "link2": "0.40 0.42 0.45 1.0",      # 石墨灰：手肘关节处的加固件
#     "link3": "0.90 0.40 0.05 1.0",      # 安全橘：小臂外壳
#     "link4": "0.40 0.42 0.45 1.0",      # 石墨灰：腕部上方装甲
#     "link5": "0.90 0.40 0.05 1.0",      # 安全橘：腕部外壳
#     "link6": "0.65 0.65 0.68 1.0",      # 工业钢：未涂装的机械关节
#     "link7": "0.85 0.80 0.10 1.0",      # 警示黄：法兰盘，工业标准末端颜色
#     "hand": "0.90 0.40 0.05 1.0",       # 安全橘：手掌外壳
#     "finger": "0.65 0.65 0.68 1.0",     # 工业钢：金属原色手指，耐磨
# }
# # 细节关节颜色 
# joint_color = "0.15 0.15 0.15 1.0"  # 机油黑：带有工业油污感的深邃连接件

#4、科幻极简风 (R G B A) 
color_palette = {
    "body_link0": "0.30 0.32 0.35 1.0", # 哑光黑：与上方洁白机身形成强烈对比
    "link0": "0.92 0.92 0.95 1.0",      # 陶瓷白：肩部外壳，极简干净
    "link1": "0.92 0.92 0.95 1.0",      # 陶瓷白：大臂外壳
    "link2": "0.15 0.65 0.70 1.0",      # 医疗青：手肘处的科技感点缀色
    "link3": "0.92 0.92 0.95 1.0",      # 陶瓷白：小臂外壳
    "link4": "0.15 0.65 0.70 1.0",      # 医疗青：腕部上方点缀
    "link5": "0.92 0.92 0.95 1.0",      # 陶瓷白：腕部外壳
    "link6": "0.80 0.80 0.82 1.0",      # 抛光铝：极其干净的亮银色关节
    "link7": "0.30 0.70 1.00 1.0",      # 晶体蓝：法兰盘高光
    "hand": "0.92 0.92 0.95 1.0",       # 陶瓷白：手掌外壳
    "finger": "0.25 0.25 0.25 1.0",     # 橡胶灰：夹爪内侧的防滑材质色
}
# 细节关节颜色 
joint_color = "0.50 0.50 0.55 1.0"  # 深钛银：干净的内部机械结构

file_paths = {
    "body_link0": "meshes/body/v10/visual/body_link0.dae",
    "link0": "meshes/arm/v10/visual/link0.dae",
    "link1": "meshes/arm/v10/visual/link1.dae",
    "link2": "meshes/arm/v10/visual/link2.dae",
    "link3": "meshes/arm/v10/visual/link3.dae",
    "link4": "meshes/arm/v10/visual/link4.dae",
    "link5": "meshes/arm/v10/visual/link5.dae",
    "link6": "meshes/arm/v10/visual/link6.dae",
    "link7": "meshes/arm/v10/visual/link7.dae",
    "hand": "meshes/ee/openarmx_hand/visual/hand.dae",
    "finger": "meshes/ee/openarmx_hand/visual/finger.dae",
}

def update_dae_color(filepath, shell_color_str, joint_color_str):
    if not os.path.exists(filepath):
        print(f"❌ 找不到文件: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    # 查找所有 diffuse 标签
    pattern = r'<color sid="diffuse">(.*?)</color>'
    matches = list(re.finditer(pattern, content))

    if len(matches) == 0:
        print(f"⚠️ 在 {filepath} 中未找到颜色标签")
        return

    # 核心修复逻辑：颠倒涂色顺序
    if len(matches) == 1:
        # 如果只有一个颜色，说明这个零件是一体成型的，直接涂成外壳色
        content = content[:matches[0].start(1)] + shell_color_str + content[matches[0].end(1):]
    else:
        # 如果有两个颜色（根据你的图片）：
        # matches[0] (第1个颜色) 实际上是【内部关节/连接件】 -> 涂装 joint_color
        # matches[1] (第2个颜色) 实际上是【外部大壳子】 -> 涂装 shell_color
        
        # 1. 先替换第一个（关节色）
        content = content[:matches[0].start(1)] + joint_color_str + content[matches[0].end(1):]
        
        # 2. 重新查找位置（因为替换后字符串长度变了）
        matches = list(re.finditer(pattern, content))
        
        # 3. 替换第二个（外壳色）
        content = content[:matches[1].start(1)] + shell_color_str + content[matches[1].end(1):]

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"✅ {filepath} 涂装完毕！")

if __name__ == "__main__":
    print("🎨 开始启动 J.A.R.V.I.S. 战甲喷涂程序...\n")
    for link_name, rgba in color_palette.items():
        update_dae_color(file_paths[link_name], rgba, joint_color)
    print("\n🎉 喷涂完成！请重新启动 RViz。")