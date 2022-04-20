import requests, os, bs4, time


# CONFIG
xkcd_root = "https://xkcd.com"  # Root directory for xkcd
num_downloaded = 0  # How many have been downloaded
bad_indexes = [404, 1350, 1416, 1608, 1663, 2198]  # Indexes that don't go to comic pages (eg. xkcd.com/404 is a 404 error and tripped up my code)


def strip_non_alphanum(text):  # Strips non-alphanumeric characters from text. Used to make sure that things like "OSError: [Errno 22] Invalid argument: '58 -- Why Do You Love Me?.png'" don't happen.
    return ''.join(filter(str.isalnum, text))

def index_to_link(index):
    return "%s/%d" % (xkcd_root, index)

def get_image_from_soup(soup):  # Returns image from bs4 soup as raw PNG data
    image_div = soup.find_all("div", {"id": "comic"})[0]  # Get the div that the comic image is in
    image_element = image_div.findChildren("img")[0]  # Get the img element of the comic image
    image_link = xkcd_root + image_element["src"]  # Get the link of the comic image
    image_req = requests.get(image_link)  # Downoad the comic image
    image = image_req.content  # Get the comic image in raw bytes (PNG format)
    return image

def get_image_file_name_from_soup(soup):  # Returns title from bs4 soup as string
    title_element = soup.find_all("div", {"id": "ctitle"})[0]  # Get the div that the title is in
    title = title_element.text  # Get the text from the div
    formatted_title = "%d -- %s" % (num, strip_non_alphanum(title))  # Format the title and removes non alpha-numeric characters from title
    file_name = formatted_title + ".png"  # Add .png to the file name
    return file_name

def save_image_to_file(file_name):  # Saves image to a file
    with open(file_name, "wb") as image_file:
        image_file.write(image)
    image_file.close()

# Create and move to a new directory
direc = "xkcd"

try:
    os.mkdir(direc)
except FileExistsError:
    pass
os.chdir(direc)

count_file_name = ".xkcd.txt"
try:
    with open(count_file_name, "rt") as count_file:
              num = int(count_file.read()) + 1
    count_file.close()
except FileNotFoundError:
    print("No counter file found...")
    num = 1


# Some statistics
total_time_elapsed = 0
start_time = time.time()

# Download comics
while True:
    if num in bad_indexes:  # If it's a "bad index," skip.
        num += 1
    req = requests.get(index_to_link(num))  # Download the comic page
    print("Downloaded page...")
    if req.status_code == 404:  # If the page doesn't exist, that means that it's downloaded every comic that exists
        print("done")
        break  # Stop downloading
    
    soup = bs4.BeautifulSoup(req.content, "html.parser")  # Makes a bs4 soup out of the comic page
    image = get_image_from_soup(soup)
    file_name = get_image_file_name_from_soup(soup)
    save_image_to_file(file_name)
    num_downloaded += 1  # Increase the amount downloaded
    
    print("Downloaded comic #%d" % num)  # Display comic number that just got downloaded
    time_elapsed = time.time() - start_time  # Calculate time elapsed
    print("Time elapsed (sec): %f, XKCD/s: %f" % (time_elapsed, num_downloaded / time_elapsed))  # Display some information
    
    num += 1  # Increase the page index

    with open(count_file_name, "wt") as count_file:
          count_file.write(str(num))
    count_file.close()

print("Succesfully downloaded %d XKCD comics!" % num_downloaded)
