# An aadapter that takes CSV as input, performs a lookup to whois, then returns the CSV results
import csv,sys
import urllib

LOCATION_URL="http://adam.kahtava.com/services/whois.xml?query="


# Given an ip, return the whois response
def lookup(ip):
    try:
        whois_ret = urllib.urlopen(LOCATION_URL + ip)
        lines = whois_ret.readlines()
        return lines
    except:
        return ''

def main():
    if len(sys.argv) != 3:
        print "Usage: python whois_lookup.py [ip field] [whois field]"
        sys.exit(0)

    ipf = sys.argv[1]
    whoisf = sys.argv[2]
    r = csv.reader(sys.stdin)
    w = None
    header = []
    first = True

    for line in r:
        if first:
            header = line
            if whoisf not in header or ipf not in header:
                print "IP and whois fields must exist in CSV data"
                sys.exit(0)
            csv.writer(sys.stdout).writerow(header)
            w = csv.DictWriter(sys.stdout, header)
            first = False
            continue

        # Read the result
        result = {}
        i = 0
        while i < len(header):
            if i < len(line):
                result[header[i]] = line[i]
            else:
                result[header[i]] = ''
            i += 1

        # Perform the whois lookup if necessary
        if len(result[ipf]) and len(result[whoisf]):
            w.writerow(result)

        elif len(result[ipf]):
            result[whoisf] = lookup(result[ipf])
            if len(result[whoisf]):
                w.writerow(result)

main()
