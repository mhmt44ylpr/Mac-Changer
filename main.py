# Gerekli modüller içe aktarılıyor
import ipaddress               # IP ve CIDR adreslerini doğrulamak için
import scapy.all as scapy     # Ağ paketlerini oluşturup göndermek için Scapy kütüphanesi
from optparse import OptionParser  # Komut satırından parametre almak için
from colorama import Fore, init     # Terminal yazılarına renk katmak için
from rich.console import Console    # Log çıktıları için modern ve renkli bir konsol
from pyfiglet import Figlet         # ASCII sanatıyla başlık yazdırmak için
import re                           # IP ve MAC adreslerini metinlerden ayıklamak için regex
from tabulate import tabulate       # Listeyi tablo biçiminde yazdırmak için
import sys, os
from contextlib import contextmanager  # stdout'u bastırmak için (gereksiz Scapy çıktısı)

# Scapy'nin default terminal çıktılarını gizlemek için bir context manager tanımlanıyor
@contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:  # Çıktıyı çöp dosyasına yönlendir
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield  # Bu bloğun içinde stdout bastırılır
        finally:
            sys.stdout = old_stdout  # İşlem bitince stdout eski haline döner

# Renkli çıktı desteğini başlat
init(autoreset=True)
console = Console()  # rich kütüphanesi ile renkli loglar yazmak için

# Ana sınıfımız: NetScanner
class NetScanner():
    def __init__(self):
        self.ip_address = '0.0.0.0'  # varsayılan IP (kullanıcı girmezse geçersiz olur)
        self.mac_and_ip_address_list = list()  # IP ve MAC adreslerini tutacak liste
        self.get_user_input()  # Kullanıcıdan IP al ve işlem başlat

    def get_user_input(self):
        # Komut satırından IP bilgisi almak için
        parser = OptionParser()
        parser.add_option('-i','--ip', dest='ipaddress',
                          help='İp adresi girilecek. Örnekler: 10.0.2.1/24, 192.168.1.1')

        (argument, _) = parser.parse_args()

        # IP veya CIDR blok doğrulayıcı
        def is_valid_ip_or_cidr(input_str):
            try:
                ipaddress.ip_network(input_str, strict=False)  # CIDR olsun veya olmasın kabul eder
                return True
            except ValueError:
                return False

        if not argument.ipaddress:
            console.log('[red]Lütfen bir ip adresi giriniz...[/red]')
        else:
            self.ip_address = argument.ipaddress
            if is_valid_ip_or_cidr(self.ip_address):
                self.brodcast_response()  # IP geçerliyse taramayı başlat
            else:
                console.log('[red]Lütfen geçerli bir ip adresi giriniz[/red]')

    def brodcast_response(self):
        console.log('[green]Tarama Yapılıyor....[/green]')

        # ARP isteği oluştur: hedef IP'ye "Sen kimsin?" paketi yollanır
        arp_req = scapy.ARP(pdst=self.ip_address)
        broadcat_response = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')  # Broadcast (herkese git)
        combine = broadcat_response/arp_req  # ARP + Ethernet paketini birleştir

        scapy.conf.verb = 0  # Scapy'nin varsayılan çıktısını kapat

        # Paketleri gönder ve yanıtları al (stdout gizlenmiş)
        with suppress_output():
            ans, uans = scapy.srp(combine, timeout=1)

        # Yanıtlar içinde IP ve MAC adreslerini bulmak için regex kullan
        for line in ans:
            ip_match = re.search(r'psrc=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', str(line))
            mac_match = re.search(r'hwsrc=([0-9a-fA-F:]{17})', str(line))

            if ip_match and mac_match:
                ip = ip_match.group(1)
                mac = mac_match.group(1)
                self.mac_and_ip_address_list.append([Fore.GREEN + ip, Fore.RED + mac])
            else:
                print("[-] IP veya MAC bulunamadı.")

        self.show_list()

    def show_list(self):
        # Eğer liste boş değilse, tabloyu yazdır
        if self.mac_and_ip_address_list:
            print(Fore.BLUE + '*'*10 + '     Mac ve Ip Günlüğü     ' + '*'*10)
            print(tabulate(self.mac_and_ip_address_list,
                           headers=[Fore.GREEN + "IP", Fore.RED +  "MAC Adresi"],
                           tablefmt="fancy_grid"))
        else:
            console.log('[red]Herhangi bir Günlük bulunamadı...[/red]')

# Ana çalıştırma bloğu (komut satırından çalıştırıldığında burası çalışır)
if __name__ == '__main__':
    figlet = Figlet(font='slant')
    print(Fore.CYAN + figlet.renderText('NET SCANNER'))

    NetScanner()  # Sınıf örneği oluşturulunca otomatik olarak çalışır
