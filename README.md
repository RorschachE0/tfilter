# tfilter

## 项目简介

本项目提供了一组Python脚本，用于处理和过滤网络数据包文件（.cap, .pcap, .pcapng）。脚本通过调用`tshark`和`editcap`等工具，实现从数据包中提取唯一的IP地址、转换时间格式，以及根据IP地址、协议、时间和端口等条件过滤数据包的功能。

## 功能说明

### list_files(directory, extensions)
- 列出指定目录中具有特定扩展名的文件。

### extract_unique_ip_addresses(pcap_file)
- 从数据包文件中提取唯一的IP地址。如果`tshark`命令失败，会尝试修复文件格式。

### convert_time_format(input_time)
- 将时间格式从“MMDDHHMMSS”转换为“2024-%m-%d %H:%M:%S”。

### main()
- 主函数，执行文件列表展示、文件选择、IP地址提取、IP和协议选择、时间过滤条件设置，并生成过滤后的数据包文件。

## 使用方法

1. 确保已安装`tshark`和`editcap`工具（通常安装wireshark即可）。
2. 将脚本放置在包含数据包文件的目录中。
3. 运行脚本：
   ```bash
   python script_name.py
   ```
4. 按照提示选择文件、IP地址和过滤条件，脚本会生成过滤后的数据包文件并保存到`test_filter`目录中。

## 注意事项

- 数据包文件扩展名必须为.cap、.pcap或.pcapng。
- 输入时间格式为“MMDDHHMMSS”。
- 脚本会在当前目录中创建一个名为`test_filter`的目录来保存过滤后的数据包文件。
- 如果目标文件已存在，脚本会尝试删除旧文件，请确保具有相应的权限。

## 依赖

- Python 3.x
- tshark
- editcap

## 示例

运行脚本后，用户会看到类似如下的交互提示：

```
可用的包文件：
1: sample.pcap
2: test.pcapng

通过编号选择文件 (1-2): 1

可用的IP地址：
1: 192.168.0.1
2: 192.168.0.2

选择IP地址输入方式（或按Enter跳过）：
1: 通过编号选择IP地址
2: 手动输入IP地址
输入你的选择 (1/2): 1

选择协议（tcp/udp或按Enter跳过）：
1: tcp
2: udp
输入你的选择 (1/2): 1

输入开始日期和时间（MMDDHHMMSS，或按Enter跳过）：0708153015
输入结束日期和时间（MMDDHHMMSS，或按Enter跳过）：0708153515

输入端口号（或按Enter跳过）：80
生成的过滤表达式：ip.addr == 192.168.0.1 and tcp and frame.time >= "2024-07-08 15:30:15" and frame.time <= "2024-07-08 15:35:15" and tcp.port == 80

过滤后的数据包已保存到 test_filter/filtered_sample.pcap
```
