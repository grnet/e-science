from argparse import ArgumentParser
from sys import argv
import xml.etree.ElementTree as ET
XML_FILE = '/home/developer/workspace/testhub/ember_django/backend/ansible/roles/yarn/templates/hdfs-site.j2'

def read_xml(file):

    with open(file, 'r') as f:
        return f.read().splitlines()


def main():

    # xml = opts['xml']
    xml = read_xml(XML_FILE)
    root = ET.fromstringlist(xml)
    doc = ET.ElementTree(root)
    doc.write('/tmp/{0}'.format('test'))

# orka_parser = ArgumentParser()
# orka_parser.add_argument("filename")
# orka_parser.add_argument("xml")
#
# opts = vars(orka_parser.parse_args(argv[1:]))

if __name__ == '__main__':
    main()
