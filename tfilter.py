import os
import shutil
import subprocess
from datetime import datetime

def list_files(directory, extensions):
    files = [f for f in os.listdir(directory) if any(f.endswith(ext) for ext in extensions)]
    return files

def extract_unique_ip_addresses(pcap_file):
    try:
        result = subprocess.run(
            ["tshark", "-r", pcap_file, "-T", "fields", "-e", "ip.addr"],
            capture_output=True,
            text=True,
            check=True
        )
        ip_addresses = result.stdout.split()
        unique_ip_addresses = sorted(set(ip for ip_pair in ip_addresses for ip in ip_pair.split(',')), key=lambda x: int(x.split('.')[0]))
        return unique_ip_addresses
    except subprocess.CalledProcessError as e:
        print(f"tshark命令失败，尝试修复文件：{e}")
        fixed_file = pcap_file.replace('.pcap', '_fixed.pcap').replace('.pcapng', '_fixed.pcap')
        subprocess.run(["editcap", "-F", "libpcap", pcap_file, fixed_file], check=True)
        return fixed_file, extract_unique_ip_addresses(fixed_file)

def convert_time_format(input_time):
    try:
        dt = datetime.strptime(input_time, "%m%d%H%M%S")
        formatted_time = dt.strftime("2024-%m-%d %H:%M:%S")
        return formatted_time
    except ValueError:
        print("日期时间格式无效，请输入MMDDHHMMSS格式。")
        return None

def main():
    current_dir = os.getcwd()
    extensions = ['.cap', '.pcap', '.pcapng']
    files = list_files(current_dir, extensions)

    if not files:
        print("当前目录下没有找到.cap、.pcap或.pcapng文件！")
        return

    print("可用的包文件：")
    for idx, f in enumerate(files):
        print(f"{idx + 1}: {f}")

    while True:
        try:
            choice = int(input(f"通过编号选择文件 (1-{len(files)}): "))
            if 1 <= choice <= len(files):
                file = files[choice - 1]
                break
            else:
                print(f"选择无效，请输入1到{len(files)}之间的数字。")
        except ValueError:
            print("输入无效，请输入一个数字。")

    dir = "test_filter"
    os.makedirs(dir, exist_ok=True)

    target_file = os.path.join(dir, file)
    if os.path.exists(target_file):
        try:
            os.remove(target_file)
        except PermissionError:
            print(f"权限被拒绝：无法删除 {target_file}。请手动删除此文件并重试。")
            return

    shutil.copy(file, target_file)

    try:
        ip_addresses = extract_unique_ip_addresses(target_file)
    except Exception as e:
        print(f"提取IP地址失败：{e}")
        return

    if isinstance(ip_addresses, tuple):
        target_file, ip_addresses = ip_addresses

    if not ip_addresses:
        print("没有找到IP地址。")
        return

    print("可用的IP地址：")
    for idx, ip in enumerate(ip_addresses):
        print(f"{idx + 1}: {ip}")

    ip_address = None
    while True:
        print("选择IP地址输入方式（或按Enter跳过）：")
        print("1: 通过编号选择IP地址")
        print("2: 手动输入IP地址")
        ip_input_choice = input("输入你的选择 (1/2): ")

        if ip_input_choice == "":
            break
        elif ip_input_choice == "1":
            try:
                ip_choice = int(input(f"通过编号选择IP地址 (1-{len(ip_addresses)}): "))
                if 1 <= ip_choice <= len(ip_addresses):
                    ip_address = ip_addresses[ip_choice - 1]
                    break
                else:
                    print(f"选择无效，请输入1到{len(ip_addresses)}之间的数字。")
            except ValueError:
                print("输入无效，请输入一个数字。")
        elif ip_input_choice == "2":
            ip_address = input("请输入要过滤的IP地址：")
            if ip_address in ip_addresses:
                break
            else:
                print("输入的IP地址不在数据包中，请重新输入。")
        else:
            print("选择无效，请输入'1'或'2'。")

    protocol = None
    while True:
        print("选择协议（tcp/udp或按Enter跳过）：")
        print("1: tcp")
        print("2: udp")
        protocol_choice = input("输入你的选择 (1/2): ")
        if protocol_choice == "":
            break
        elif protocol_choice == "1":
            protocol = "tcp"
            break
        elif protocol_choice == "2":
            protocol = "udp"
            break
        else:
            print("协议选择无效，请输入'1'或'2'。")

    filter_expression = []
    if ip_address:
        filter_expression.append(f"ip.addr == {ip_address}")
    if protocol:
        filter_expression.append(protocol)

    start_time_input = input("输入开始日期和时间（MMDDHHMMSS，或按Enter跳过）：")
    end_time_input = input("输入结束日期和时间（MMDDHHMMSS，或按Enter跳过）：")

    start_time = convert_time_format(start_time_input) if start_time_input else None
    end_time = convert_time_format(end_time_input) if end_time_input else None

    if protocol == "tcp":
        port = input("输入端口号（或按Enter跳过）：")
        if port:
            filter_expression.append(f"tcp.port == {port}")

    if start_time:
        filter_expression.append(f"frame.time >= \"{start_time}\"")
    if end_time:
        filter_expression.append(f"frame.time <= \"{end_time}\"")

    filter_str = " and ".join(filter_expression)
    print(f"生成的过滤表达式：{filter_str}")

    filename = os.path.basename(file)
    output_file = os.path.join(dir, f"filtered_{filename}")

    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except PermissionError:
            print(f"权限被拒绝：无法删除 {output_file}。请手动删除此文件并重试。")
            return

    if filter_str:
        try:
            subprocess.run(["tshark", "-r", target_file, "-Y", filter_str, "-w", output_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"tshark命令失败：{e}")
            return
    else:
        shutil.copy(target_file, output_file)

    print(f"过滤后的数据包已保存到 {output_file}")

if __name__ == "__main__":
    main()
    input("按Enter键退出...")
