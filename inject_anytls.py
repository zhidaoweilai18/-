import os
import re

def patch_file(filepath, pattern, replacement, flags=0):
    if not os.path.exists(filepath):
        print(f"[-] 找不到文件: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if re.search(pattern, content, flags):
        new_content = re.sub(pattern, replacement, content, flags=flags)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[+] 成功注入: {filepath}")
        return True
    else:
        print(f"[-] 正则未匹配到目标: {filepath}")
        return False

def scrub_brand_name():
    print(">>> 开始全量清洗品牌名称 (White-labeling)...")
    for ext in ('*.cpp', '*.h', '*.ui', 'CMakeLists.txt'):
        for filepath in glob.glob(f'./**/{ext}', recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 统一转成小写来判断，彻底解决 NekoBox, nekobox, NEKOBOX 等大小写漏网问题
                if 'neko' in content.lower():
                    content = re.sub(r'Nekoray', 'XRAY', content, flags=re.IGNORECASE)
                    content = re.sub(r'Nekobox', 'XRAY', content, flags=re.IGNORECASE)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
            except Exception:
                pass
    print(">>> 品牌清洗完成！")

def main():
    print(">>> 开始执行 AnyTLS 代码级注入手术...")

    ui_files = [
        "libs/gui/profile/profile_editor.cpp",
        "main/forms/profile_form.cpp"
    ]
    ui_pattern = r'(ui->comboBox_protocol->addItem\("VLESS"\);)'
    ui_replacement = r'\1\n    ui->comboBox_protocol->addItem("AnyTLS");'
    for f in ui_files:
        patch_file(f, ui_pattern, ui_replacement)

    engine_files = [
        "libs/core/singbox/singbox_engine.cpp",
        "libs/core/singbox/singbox_config.cpp"
    ]
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
    for f in engine_files:
        patch_file(f, engine_pattern, engine_replacement, flags=re.MULTILINE)

    print(">>> 注入流程结束。准备开始 C++ 编译。")

if __name__ == "__main__":
    main()
