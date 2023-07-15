import requests
from threading import Thread, Lock
from queue import Queue
from colorama import init, Fore
import sys
import time






init()
GREEN = Fore.GREEN
RED = Fore.RED
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
RESET  = Fore.RESET

q = Queue()
list_lock = Lock()
discovered_domains = []


message = """                                                                            

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░   ░░░   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   ▒▒▒   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒    ▒   ▒   ▒▒▒▒▒   ▒▒▒▒▒   ▒    ▒  ▒▒     ▒▒▒▒▒    ▒▒▒▒   ▒▒▒▒▒   ▒   ▒▒▒   ▒   ▒▒▒▒▒▒   ▒▒▒▒▒  ▒    
▓▓   ▓▓  ▓▓   ▓▓  ▓▓▓   ▓▓   ▓▓▓   ▓▓▓   ▓▓▓▓▓▓   ▓▓▓▓▓   ▓▓   ▓▓▓   ▓▓   ▓▓   ▓▓   ▓▓  ▓▓▓   ▓▓▓   ▓▓▓
▓▓   ▓▓  ▓▓   ▓         ▓▓   ▓▓▓   ▓▓▓▓▓    ▓▓   ▓▓▓▓▓   ▓▓▓   ▓▓▓   ▓▓   ▓▓   ▓▓   ▓         ▓▓▓   ▓▓▓
▓▓   ▓▓  ▓▓   ▓  ▓▓▓▓▓▓▓▓▓   ▓▓▓   ▓ ▓▓▓▓▓   ▓▓   ▓▓▓▓   ▓▓▓   ▓▓▓   ▓▓   ▓▓   ▓▓   ▓  ▓▓▓▓▓▓▓▓▓▓   ▓▓▓
█    ██  ██   ███     ████   ████   ██      █████    ███   █    █    ██   █    ██   ███     ████    ███
███████████████████████████████████████████████████████████████████████████████████████████████████████


"""
message_line = """
__________________________________________________________________________
"""
start_message = """

"""

warning = """
__________________________________________________________________________
When using M3LTScan PLEASE DO NOT USE HTTP | HTTPS in your domain input
__________________________________________________________________________
"""



def scan_subdomains(domain):

    
    global q
    
    while True:
        # get the subdomain from the queue
        subdomain = q.get()
        # scan the subdomain
        url = f"http://{subdomain}.{domain}"
        try:
            requests.get(url)
        except requests.ConnectionError:
            pass
        else:
            
            print(f"{GREEN}"+"[+] Discovered subdomain:", url)
            # add the subdomain to the global list
            with list_lock:
                discovered_domains.append(url)

        # we're done with scanning that subdomain
        q.task_done()


def custom_messages():
    print(f"{YELLOW}"+message)
    print(f"{RED}"+message_line)
    print(f"{CYAN}"+start_message)
    print(f"{RED}"+message_line)
    print(f"{RED}"+warning)
    testtext()

def testtext():
    red = RED
    green = GREEN
    blue = CYAN
    yellow = YELLOW
    reset = RESET
    sys.stdout.write(f"{red}"+"Scanning Domains")
    time.sleep(1)
    sys.stdout.write(f"{green}"+"\rScanning Domains.")
    time.sleep(1)
    sys.stdout.write(f"{blue}"+"\rScanning Domains..")
    time.sleep(1)
    sys.stdout.write(f"{yellow}"+"\rScanning Domains...\n")
    time.sleep(3)
    sys.stdout.write(f"{reset}"+"\rShowing Found Domains\n")

def main(domain, n_threads, subdomains):

    custom_messages()
    global q

    # fill the queue with all the subdomains
    for subdomain in subdomains:
        q.put(subdomain)

    for t in range(n_threads):
        # start all threads
        worker = Thread(target=scan_subdomains, args=(domain,))
        # daemon thread means a thread that will end when the main thread ends
        worker.daemon = True
        worker.start()





if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Faster Subdomain Scanner using Threads")
    parser.add_argument("domain", help="Domain to scan for subdomains without protocol (e.g without 'http://' or 'https://')")
    parser.add_argument("-l", "--wordlist", help="File that contains all subdomains to scan, line by line. Default is subdomains.txt",
                        default="subdomains.txt")
    parser.add_argument("-t", "--num-threads", help="Number of threads to use to scan the domain. Default is 10", default=10, type=int)
    parser.add_argument("-o", "--output-file", help="Specify the output text file to write discovered subdomains", default="discovered-subdomains.txt")
    
    args = parser.parse_args()
    domain = args.domain
    wordlist = args.wordlist
    num_threads = args.num_threads
    output_file = args.output_file

    main(domain=domain, n_threads=num_threads, subdomains=open(wordlist).read().splitlines())
    q.join()

    # save the file
    with open(output_file, "w") as f:
        for url in discovered_domains:
            print(url, file=f)