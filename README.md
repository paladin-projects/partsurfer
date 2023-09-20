# partsurfer
Fetch spare parts from HPE Partsurfer

# Usage
When run as `python3 partsurfer.py -h` or `./partsurfer.py -h` script shows its usage:
<pre>
usage: partsurfer.py [-h] [-s | -p | -n] [-o OUTPUT] NUM [NUM ...]

Fetch spare parts details fro HPE Partsurfer based on serial, product or part number

positional arguments:
  NUM                   number(s) to search for

options:
  -h, --help            show this help message and exit
  -s, --serial          search for serial number(s)
  -p, --product         search for product number(s)
  -n, --part            search for part number(s)
  -o OUTPUT, --output OUTPUT
                        send output to file

</pre>

Script runs in 3 modes:

 * When run with `-s` option, all other arguments are considered HPE serial numbers
 * When run with `-p` option, all other arguments are considered HPE product numbers
 * Whern run with `-n` option, all other argumetns are considered HPE part numbers
