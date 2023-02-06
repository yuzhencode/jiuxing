# 案例代码
from bs4 import BeautifulSoup
import requests
import time

def open_proxy_url(url):
    #user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    #headers = {'User-Agent': user_agent}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    try:
        r = requests.get(url, headers = headers, timeout = 20)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return(r.text)
    except:
        print('无法访问网页' + url)


def get_proxy_ip(response):
    proxy_ip_list = []
    soup = BeautifulSoup(response, 'html.parser')
    proxy_ips = soup.find(class_ = 'fl-table').find_all('tbody')
    proxy_ips = proxy_ips[0].find_all('tr')
    for proxy_ip in proxy_ips:
        ip = proxy_ip.select('td')[0].text.split(':')[0]
        port = proxy_ip.select('td')[0].text.split(':')[1]
        protocol = proxy_ip.select('td')[1].text
        if 'HTTPS' in protocol:
            protocol = 'https'
        #if protocol in ('HTTP','HTTPS','http','https'):
            # f-string字符串格式方法
            #proxy_ip_list.append(f'{protocol}://{ip}:{port}')
            proxy_ip_list.append(f'{ip}:{port}')
    return proxy_ip_list

if __name__ == '__main__':
    proxy_ip_filename = 'proxy_ip.txt'

    proxy_url = 'http://www.xiladaili.com/https/'
    text = open_proxy_url(proxy_url)
    with open(proxy_ip_filename, 'w',encoding='gb18030') as f:
        f.write(text)

    text = open(proxy_ip_filename, 'r',encoding='gb18030').read()
    proxy_ip_list = get_proxy_ip(text)
    print(len(proxy_ip_list))
    print(proxy_ip_list)