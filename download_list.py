import requests
import re
import os

DOWNLOADS_DIR = './downloads/'
FILES_DIR = './files/'
CONFIG_FILE = 'lists.conf'
CONF_PREFIX = 'BL-'
MAX_LINES = 130000
CATEGORY = 200
REPO = 'https://'

def download_file(url, filename):
  """
  Download file from url to filename
  """
  print("Downloading {} -> {}".format(filename, url))
  try:
      r = requests.get(url, allow_redirects=True, stream=True) 
      r.raise_for_status()
      open(DOWNLOADS_DIR+filename, 'wb+').write(r.content)  
      return write_to_file_in_chucks(filename)
  except requests.exceptions.HTTPError as errh:
      print ("Http Error:",errh)
  except requests.exceptions.ConnectionError as errc:
      print ("Error Connecting:",errc)
  except requests.exceptions.Timeout as errt:
      print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err:
      print ("OOps: Something Else",err)

def write_to_file_in_chucks(filename):
  """
  Write firts MAX_LINES lines to file
  """
  chunk_file = None
  chunk = 0
  with open(DOWNLOADS_DIR+filename) as file:    
    for lineno, line in enumerate(file):
        if lineno % MAX_LINES == 0:
            if chunk_file:
                chunk_file.close()
                chunk += 1
            small_filename = '{}_{}'.format(chunk,filename)
            chunk_file = open(FILES_DIR+small_filename, "w")
        chunk_file.write(line)
    if chunk_file:
        chunk_file.close()
  return chunk      

def remove_files(dir):
  for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

def main():
  file_sources = open('sources.txt', 'r')
  sources = file_sources.readlines()
  remove_files(DOWNLOADS_DIR)
  remove_files(FILES_DIR)
  print("Downloading files...")
  category = CATEGORY
  with open (CONFIG_FILE, 'w') as config: 
    for index, line in enumerate(sources):      
        filename = line.split(',')[0]
        type = line.split(',')[1]
        refresh = line.split(',')[2]
        url = line.split(',')[3]
        chunk = download_file(url.strip(),filename)
        for c in range(chunk):
            config.write('edit "{}{}_{}"\n'.format(CONF_PREFIX,c,filename))
            config.write('  set type {}\n'.format(type))
            config.write('  set category {}\n'.format(category))
            config.write('  set resource "{}/{}_{}"\n'.format(REPO,c,filename))
            config.write('  set refresh-rate {}\n'.format(refresh))
            config.write('next\n')
            category += 1
  file_sources.close()
  config.close()

if __name__ == '__main__':
    main()