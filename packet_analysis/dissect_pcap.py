import sys
import os

sys.path.insert(0, os.path.abspath(".."))
import re
import time
from pathlib import Path
from scapy.all import sniff
from scapy.all import Packet

from packet_analysis.sql.dao import *
from packet_analysis.sql.dao import sqlObject
from packet_analysis.sql.csv.csv_builder import CSVBuilder
from packet_analysis.sql.sql_helper import table_bindings, create_connection, bulk_insert

csv_collection = None

def analyze_pcap_file(path: str):
    """
    Method called per PCAP file to collect data
    :param path: Path to the PCAP file
    :return: None
    """
    global csv_collection
    csv_collection = CSVBuilder()
    correct_path = Path(path)
    print("*" * 50)
    print("Sniffing packets of: " + str(correct_path))
    sniff(offline=str(correct_path), prn=packet_handler, store=False)


def pull_layer(layer):
    """
    Pulls string descriptor from layer object of scapy Packet object
    :param layer: scapy Layer object
    :return: string
    """
    class_desc = str(layer).split('.')
    return re.match(r"^[^']*", class_desc[len(class_desc) - 1]).group(0)


def deconstruct_packet(pkt_type: str, pkt: Packet) -> sqlObject:
    """
    Deconstructs the packet based on its type.
    :param pkt_type: Type of packet being analyzed
    :param pkt: The packet object itself
    :return: sqlObject that can be inserted into the DB
    """
    # Switch statement keyed on pkt_type
    switcher = {
        "ARP": lambda p: arp.ARP(p),
        "DHCP": lambda p: dhcp.DHCP(p),
        "DNS": lambda p: dns.DNS(p),
        "EAPOL": lambda p: eapol.EAPOL(p),
        "Ethernet": lambda p: ethernet.Ethernet(p),
        "IP": lambda p: ip.IP(p),
        "NTPHeader": lambda p: ntp.NTPHeader(p),
        "TCP": lambda p: tcp.TCP(p),
        "UDP": lambda p: udp.UDP(p),
    }

    return switcher[pkt_type](pkt)


def packet_handler(pkt: Packet):
    """
    Handles the basic filtering for the packet, collections information if possible
    :param pkt: Packet to be analyzed
    :return: None
    """
    # Pull out the outer most layer of the PKT
    str_layer = pull_layer(pkt.layers()[-1])
    if str_layer == "Raw":
        str_layer = pull_layer(pkt.layers()[-2])

    # If system can handle to packet, analyze it
    if str_layer in table_bindings.keys():
        sql_dao = deconstruct_packet(str_layer, pkt)
        csv_collection.add_entry(str_layer, sql_dao.csv())

def main(argv):
    """
    Entry point for the program, handles arguments as paths to the PCAPs
    :param argv: Arguments for program
    :return:
    """
    call_info = "\"python(3) dissect_pcap.py Path/to/database.db [Path/to/file.pcap] ... \"."
    first_time = time.time()
    print("*" * 50)
    if len(argv) < 2:
        conn = create_connection("D:/Semester 6/Capstone/DB/analysis.db")
    else:
        conn = create_connection(argv[1])

    if len(argv) < 2:
        paths = []
        for subdir, dirs, files in os.walk(r'D:\Semester 6\Capstone\routerPCAP\Capstone-pcaps'):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".00") or filepath.endswith(".01") or filepath.endswith(
                        ".02") or filepath.endswith(".03") or filepath.endswith(".04") or filepath.endswith(
                        ".05") or filepath.endswith(".06"):
                    paths.append(filepath)
                    print("Found PCAP: " + str(filepath))
    else:
        paths = argv[1:]

    for path in paths:
        try:
            analyze_pcap_file(path)
            bulk_insert(conn, csv_collection.sql_objects)
        except:
            print("*" * 50)
            print("Error in processing PCAP, moving forward")
            print("*" * 50)

    elapsed_time = time.time() - first_time
    print("*" * 50)
    print("Elapsed Time:")
    print("-" * 50)
    print("Hours:   " + str((elapsed_time / 3600) % 86400))
    print("Minutes: " + str((elapsed_time / 60) % 3600))
    print("Seconds: " + str(elapsed_time % 60))


if __name__ == "__main__":
    main(sys.argv)
