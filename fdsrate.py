# Main FDS Rating script
from bs4 import BeautifulSoup
from collections import Counter
from __future__ import division
import urllib2


# Scrape the main url for the students
def get_students(base_url):
    # Parse the page with the list of grad students
    page = urllib2.urlopen(base_url)
    soup = BeautifulSoup(page.read())
    # Remove the header with sort by links
    gradcontainer = soup.find('div', {'id':'contentSecond'})
    # Remove header and footer, leaving the grad info
    gradcontainer.h2.extract()
    gradcontainer.find('div', {'id':'sidenav'}).extract()
    # Find the links to the grad student pages
    grads = gradcontainer.findAll('a', href=True)
    return grads

def get_rating(current_student):
    print "Scraping info for: %s" % (current_student)
    student_page = urllib2.urlopen(current_student['href'])
    student_soup = BeautifulSoup(student_page.read())
    info = student_soup.find('div', {'id':'contentSecond'})
    # We return a dict with info if we have the field
    self_fields = Counter({})
    # Student name
    self_fields['name'] = info.h3.text.split(',')[0]
    self_fields['email'] = info.select('a[href^=mailto]')[0].text
    # Check for a picture
    img = info.findAll('img')
    if img:
        self_fields['img'] = 1
    # The b tag is associated with the information categories
    fields = info.findAll('b')
    for q in fields:
        key = q.text.strip(':')
        self_fields[key] = 1
    return self_fields

def send_rating(nstudents, total_rating, rating):
    print ""
    print "Result for %s: %s" % (rating['name'], rating['email'])
    print "Simple rating: %2.2f%%" % (len(rating) / len(total_rating))
    print "You have filled in:"
    for item in rating:
        print "  (%2.2fi%%) %s" % (total_rating[item]/nstudents, item)
        del total_rating[item]
    print "You have neglected:"
    for item in total_rating:
        print "  (%2.2f%%) %s" % (total_rating[item]/nstudents, item)
    return True
def send_rating(nstudents, totals, rating):
    # Make a shallow copy of the total, so we can modifiy it here.
    total_rating = Counter(totals)
    print ""
    print "Result for %s: %s" % (rating['name'], rating['email'])
    # Give a simple score correcting for the name and email fields
    simple_score = (len(rating)-2) / len(total_rating)
    print "Simple rating: %4.1f%% Complete profile." % (simple_score * 100)
    print "Shorthand: (Percent of grads with this field) Field"
    print "You have filled in:"
    for item in rating:
        print "  (%4.1f%%) %s" % (total_rating[item] / nstudents * 100, item)
        del total_rating[item]
    print "You have neglected:"
    for item in total_rating:
        print "  (%4.1f%%) %s" % (total_rating[item] / nstudents * 100, item)
    return True

def show_score_histogram(simple_score, totals, rating):
    score_hist = Counter(simple_score)
    short_score = len(rating) - 2
    for ii in range(len(totals)):
        if short_score == ii:
            print "%2d | %s %s" % (ii, score_hist[ii]*"=", "<-- YOU")
        else:
            print "%2d | %s" % (ii, score_hist[ii]*"=")
    return True

if __name__ == "__main__":
    base_url = 'http://fds.duke.edu/db/aas/Physics/grad'
    student_urls = get_students(base_url)
    nstudents = len(student_urls)
    # First loop through getting all the info for all students
    totals = Counter()
    simple_score = []
    for current_student in student_urls:
        rating = get_rating(current_student)
        totals = totals + rating
        simple_score.append(len(rating) - 2)
    # We don't need a giant string of emails or names
    del totals['email']
    del totals['name']
    # Now go back through the students and e-mail their results
    for current_student in student_urls:
        rating = get_rating(current_student)
        send_rating(nstudents, totals, rating)
