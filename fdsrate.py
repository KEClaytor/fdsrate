# Main FDS Rating script
from bs4 import BeautifulSoup
import urllib2


# Scrape the main url for the students
def get_students(base_url):
    # Parse the page with the list of grad students
    page = urllib2.urlopen(base_url)
    soup = BeautifulSoup(page.read())
    # Remove the header with sort by links
    gradcontainer.h2.extract()
    # Find the links to the grad student pages
    grads = gradcontainer.findAll('a', href=True)
    return grads

def get_rating(current_student):
    student_page = urllib2.urlopen(current_student['href'])
    student_soup = BeautifulSoup(student_page.read())
    info = student_soup.find('div', {'id':'contentSecond'})
    # The b tag is associated with the information categories
    info.findAll('b')
    # Check for a picture
    info.findAll('img')



if __name__ == "__main__":
    base_url = 'http://fds.duke.edu/db/aas/Physics/grad'
    student_urls = get_students(base_url)
    for current_student in student_urls:
        rating = get_rating(current_student)
        send_rating(current_student, rating)
