import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import time
from urllib3.contrib.socks import SOCKSProxyManager
from itertools import islice  # 导入 islice


def test_http_proxy(ip, port):
    proxy = f"http://{ip}:{port}"
    # print(proxy)
    try:
        response_google = requests.get('http://www.google.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        response_baidu = requests.get('http://www.baidu.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        if response_google.status_code == 200 and response_baidu.status_code == 200:
            return f"{ip}:{port}"
    except Exception as e:
        pass
    return None


def test_socks5_proxy(ip, port):
    proxy = f"socks5://{ip}:{port}"
    session = requests.Session()
    session.proxies.update({
        'http': proxy,
        'https': proxy
    })

    # Create a SOCKSProxyManager for the session
    socks_adapter = SOCKSProxyManager(proxy)
    session.mount('http://', socks_adapter)
    session.mount('https://', socks_adapter)

    try:
        response_google = session.get('http://www.google.com', timeout=5)
        response_baidu = session.get('http://www.baidu.com', timeout=5)
        if response_google.status_code == 200 and response_baidu.status_code == 200:
            return f"{ip}:{port}"
    except Exception as e:
        pass
    finally:
        session.close()
    return None


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours}小时-{minutes:02d}分钟-{seconds:02d}秒"


def main():
    parser = argparse.ArgumentParser(description='验证IP地址作为代理的有效性。')
    parser.add_argument('-f', '--file', default='ips.txt', help='包含IP地址的输入文件（默认: ips.txt）')
    parser.add_argument('-p', '--port', type=int, help='要测试的端口号（如果指定了 -af 参数，则此参数无效）')
    parser.add_argument('-o', '--output', default=None,
                        help='保存有效代理的输出文件前缀（默认: 第一个IP地址的A段_端口号）')
    parser.add_argument('-t', '--threads', default=10, type=int, help='使用的线程数（默认: 10）')
    parser.add_argument('-s', '--save-interval', default=100, type=int,
                        help='每次探测得到多少个IP后写入文件（默认: 100）')

    args = parser.parse_args()

    valid_http_proxies = []
    valid_socks5_proxies = []
    total_valid_count = 0
    total_checked_count = 0
    start_time = time.time()

    def read_ips(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                ip = line.strip()
                if ip:
                    yield ip

    def generate_tasks(ips, port):
        tasks = []
        for ip in ips:
            if port == 1080:
                tasks.append(executor.submit(test_http_proxy, ip, port))
                tasks.append(executor.submit(test_socks5_proxy, ip, port))
            else:
                tasks.append(executor.submit(test_http_proxy, ip, port))
        return tasks

    def write_valid_proxies(http_proxies, socks5_proxies):
        nonlocal total_valid_count
        if http_proxies:
            with open(f"{output_prefix}", 'a') as file:
                for proxy in http_proxies:
                    file.write(proxy + '\n')
        if socks5_proxies:
            with open(f"{output_prefix}_socks5_.txt", 'a') as file:
                for proxy in socks5_proxies:
                    file.write(proxy + '\n')
        total_valid_count += len(http_proxies) + len(socks5_proxies)
        elapsed_time = time.time() - start_time
        avg_time_per_ip = elapsed_time / total_checked_count if total_checked_count > 0 else 0
        remaining_ips = sum(1 for _ in read_ips(args.file)) - total_checked_count
        estimated_remaining_time = avg_time_per_ip * remaining_ips
        formatted_remaining_time = format_time(estimated_remaining_time)
        print(f"当前探测过的IP总数: {total_checked_count}, 存入的IP总数: {total_valid_count}")
        print(f"预计还需运行时间: {formatted_remaining_time}")

    if not args.port:
        raise ValueError("必须指定 --port 参数")

    ips = read_ips(args.file)
    try:
        first_ip = next(ips)
    except StopIteration:
        raise ValueError(f"文件 {args.file} 内容为空")
    output_prefix = args.output if args.output else f"{first_ip.split('.')[0]}_{args.port}"
    ips = read_ips(args.file)  # 重新读取生成器

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        batch_size = 1000  # 每次读取1000个IP进行处理
        while True:
            ip_batch = list(islice(ips, batch_size))
            if not ip_batch:
                break
            futures = generate_tasks(ip_batch, args.port)
            for future in as_completed(futures):
                valid_proxy = future.result()
                if valid_proxy:
                    if ':80' in valid_proxy or ':8080' in valid_proxy:
                        valid_http_proxies.append(valid_proxy)
                    elif ':1080' in valid_proxy:
                        valid_socks5_proxies.append(valid_proxy)
                total_checked_count += 1
                # Write to file every `save_interval` valid proxies or when all futures are completed
                if (len(valid_http_proxies) >= args.save_interval or
                        len(valid_socks5_proxies) >= args.save_interval or
                        total_checked_count % batch_size == 0):
                    write_valid_proxies(valid_http_proxies, valid_socks5_proxies)
                    valid_http_proxies.clear()
                    valid_socks5_proxies.clear()


if __name__ == "__main__":
    main()