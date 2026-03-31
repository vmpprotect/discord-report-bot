#####################
# Credits
# - me, doing this in 2022/23 when the Report Server button came out on mobile
# - random kid, making "discord 0day" and reminding me of this
# - J***, giving me some proxies to test on for my first round to make sure it works
# - L***, tokens to test
# - and all the dumb kids that paid for this
#####################

import requests
import json
import time
import threading
from queue import Queue
from typing import List, Dict, Any
import random

class DiscordReporter: # note: the class is AI generated except some parts, mostly used off of ProxyMan
    def __init__(self, proxy=None):
        self.base_url = "https://discord.com/api/v9/reporting/guild"
        
        self.headers = {
            'Host': 'discord.com',
            'x-discord-timezone': 'America/New_York',
            'baggage': 'sentry-environment=stable,sentry-public_key=06e00b7472364e1986bc684e14371271,sentry-release=discord_ios%40321.0.96499%2B96499,sentry-trace_id=89f301d7552c4dff9838318686818e4e',
            'Accept': '*/*',
            'x-discord-locale': 'en-US',
            'sentry-trace': '89f301d7552c4dff9838318686818e4e-81797c7d883de255-0',
            'Accept-Language': 'en-US',
            'User-Agent': 'Discord/96499 CFNetwork/3860.400.51 Darwin/25.3.0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }
        
        self.cookies = {
            '_cfuvid': '6bgnI7waHlC5I_t9odH95kRjkJIAyPuDEHF3VzcD._U-1774973628.3332946-1.0.1.1-wntAlb7kfyrG1TGG5rfQQcVQ1Wzmv6uzqzji8qKOl9c',
            '__dcfduid': 'fded7790e0ed11f0b9482bbcd769f489',
            '__sdcfduid': 'fded7790e0ed11f0b9482bbcd769f4898cfae2079e4a0191c1f4d1a83b15520c1ec8778bad9f6223e78d8778741da8a7'
        }
        
        self.payload = {
            "version": "1.0",
            "variant": "4",
            "language": "en",
            "breadcrumbs": [4, 3, 2, 80, 126],
            "elements": {
                "guild_select": ["other"]
            },
            "name": "guild"
        }
        
        self.proxies = []
        if proxy:
            if isinstance(proxy, list):
                for p in proxy:
                    parts = p.split(':')
                    if len(parts) == 4:
                        host, port, user, password = parts
                        proxy_url = f"http://{user}:{password}@{host}:{port}"
                        self.proxies.append({"http": proxy_url, "https": proxy_url})
            else:
                parts = proxy.split(':')
                if len(parts) == 4:
                    host, port, user, password = parts
                    proxy_url = f"http://{user}:{password}@{host}:{port}"
                    self.proxies.append({"http": proxy_url, "https": proxy_url})
    
    def get_random_proxy(self):
        if self.proxies:
            return random.choice(self.proxies)
        return None
    
    def send_report(self, token: str, report_num: int, guild_id: str = None) -> Dict[str, Any]:
        headers = self.headers.copy()
        headers['Authorization'] = token
        
        payload = self.payload.copy()
        if guild_id:
            payload['guild_id'] = str(guild_id)
        
        proxy = self.get_random_proxy()
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                cookies=self.cookies,
                json=payload,
                proxies=proxy,
                timeout=30
            )
            
            if response.status_code == 200: # good
                print(f"[*] report #{report_num} success : {response.status_code}")
                return {
                    'report_num': report_num,
                    'success': True,
                    'status_code': response.status_code,
                    'token': token[:20] + "..."
                }
            elif response.status_code == 429: # rate limit
                try:
                    data = response.json()
                    retry_after = data.get('retry_after', 1)
                    print(f"[*] report #{report_num} rate limited (429) : wait {retry_after:.2f} seconds")
                    return {
                        'report_num': report_num,
                        'success': False,
                        'status_code': 429,
                        'retry_after': retry_after,
                        'token': token[:20] + "..."
                    }
                except:
                    print(f"[*] report #{report_num} rate limited (429) : wait unknown time")
                    return {
                        'report_num': report_num,
                        'success': False,
                        'status_code': 429,
                        'retry_after': 1,
                        'token': token[:20] + "..."
                    }
            else: # shouldn't ever reach here unless proxy issue
                print(f"[*] report #{report_num} failed : {response.status_code}")
                return {
                    'report_num': report_num,
                    'success': False,
                    'status_code': response.status_code,
                    'token': token[:20] + "..."
                }
        except Exception as e:
            print(f"[*] report #{report_num} failed : {str(e)}")
            return {
                'report_num': report_num,
                'success': False,
                'error': str(e),
                'token': token[:20] + "..."
            }

def worker(task_queue, results, guild_id, reporter):
    while True:
        try:
            token, report_num = task_queue.get(timeout=1)
            result = reporter.send_report(token, report_num, guild_id)
            results.append(result)
            task_queue.task_done()
            
            if result.get('status_code') == 429:
                time.sleep(result.get('retry_after', 1))
        except:
            break

def main():
    tokens = [
        "token1",
        "token2",
        "token3",
    ]
    
    proxies = [
        "ip:port:user:pass",
        "ip:port:user:pass",
        "ip:port:user:pass",
    ]

    
    total_reports = 50
    worker_count = 10 # how many threads
    guild_id = "" # set guild id
    
    reporter = DiscordReporter(proxy=proxies)
    
    task_queue = Queue()
    results = []
    
    for i in range(total_reports):
        token = tokens[i % len(tokens)]
        task_queue.put((token, i + 1))
    
    threads = []
    for _ in range(worker_count):
        t = threading.Thread(target=worker, args=(task_queue, results, guild_id, reporter))
        t.start()
        threads.append(t)
    
    task_queue.join()
    
    for t in threads:
        t.join()
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    rate_limited = sum(1 for r in results if r.get('status_code') == 429)
    
    print(f"Total reports: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Rate limited (429): {rate_limited}")
    print(f"Success rate: {(successful/len(results)*100):.1f}%")

if __name__ == "__main__":
    main()
