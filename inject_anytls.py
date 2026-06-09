import os
import re
import glob

def patch_file(filepath, pattern, replacement, flags=0):
    if not os.path.exists(filepath): return False
    with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
    if re.search(pattern, content, flags):
        new_content = re.sub(pattern, replacement, content, flags=flags)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(new_content)
        return True
    return False

def safe_scrub_brand():
    print(">>> 开始安全清洗 UI 界面特征 (微创手术)...")
    
    # 1. 安全替换 Qt 界面排版文件 (.ui 本质是 XML，替换纯文本很安全)
    for filepath in glob.glob('./**/*.ui', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
            content = re.sub(r'Nekobox', 'XRAY', content, flags=re.IGNORECASE)
            content = re.sub(r'Nekoray', 'XRAY', content, flags=re.IGNORECASE)
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
        except: pass

    # 2. 针对 C++ 源码，严格限制：只替换被双引号 "" 括起来的字符串！绝对不碰函数名！
    for filepath in glob.glob('./**/*.cpp', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
            content = re.sub(r'"Nekobox"', '"XRAY"', content, flags=re.IGNORECASE)
            content = re.sub(r'"Nekoray"', '"XRAY"', content, flags=re.IGNORECASE)
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
        except: pass

    # 3. 篡改系统底层固化的版本号
    if os.path.exists("nekoray_version.txt"):
        with open("nekoray_version.txt", "w", encoding="utf-8") as f:
            f.write("2026.1.0-Stealth")
    print(">>> 界面特征清洗完成！")

def main():
    print(">>> 开始执行核心代码级注入...")
    
    safe_scrub_brand()

    # 注入 AnyTLS UI 下拉菜单
    ui_files = ["libs/gui/profile/profile_editor.cpp", "main/forms/profile_form.cpp"]
    ui_pattern = r'(ui->comboBox_protocol->addItem\("VLESS"\);)'
    ui_replacement = r'\1\n    ui->comboBox_protocol->addItem("AnyTLS");'
    for f in ui_files: patch_file(f, ui_pattern, ui_replacement)

    # 注入 AnyTLS 核心逻辑
    engine_files = ["libs/core/singbox/singbox_engine.cpp", "libs/core/singbox/singbox_config.cpp"]
    engine_pattern = r'(if\s*\(profile.protocol\s*==\s*"VLESS"\)\s*\{[\s\S]*?^\s*\})'
    engine_replacement = r'''\1
    else if (profile.protocol == "AnyTLS") {
        QJsonObject out;
        out["type"] = "anytls";
        out["server"] = profile.serverAddress;
        out["server_port"] = profile.serverPort;
        out["password"] = profile.password;
        outbounds.append(out);
    }'''
    for f in engine_files: patch_file(f, engine_pattern, engine_replacement, flags=re.MULTILINE)

    print(">>> 手术结束。准备开始安全的 C++ 编译。")

if __name__ == "__main__":
    main()
