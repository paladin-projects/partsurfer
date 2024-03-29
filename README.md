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
                        append output to file
  -k, --skip-headers    skip headers (useful for appending to existing file
</pre>

Script runs in 3 modes:

 * When run with `-s` option, all other arguments are considered HPE serial numbers
 * When run with `-p` option, all other arguments are considered HPE product numbers
 * When run with `-n` option, all other argumetns are considered HPE part numbers


# Dependencies
`sudo apt install python3-httpx python3-h2`

# Using with Windows
 * Install Python from Microsoft Store.
 * Open Command Prompt.
 * Install dependencies: `pip install lxml bs4 h2 httpx`
 * Type `python partsurfer.py -h`