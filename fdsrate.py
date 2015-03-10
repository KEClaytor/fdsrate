# Main FDS Rating script
from __future__ import division
from bs4 import BeautifulSoup
from collections import Counter
import urllib2
import simplemail as sm

base_url = 'http://fds.duke.edu/db/aas/Physics/grad'
fds_url = 'http://fds.duke.edu/db'
phy_url = 'http://www.phy.duke.edu/directory/grad'
duke_site_url = 'http://sites.duke.edu/getting-started/'
source_url = 'https://github.com/KEClaytor/fdsrate'


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
        self_fields['Image'] = 1
    # The b tag is associated with the information categories
    fields = info.findAll('b')
    for q in fields:
        key = q.text.strip(':')
        self_fields[key] = 1
    return self_fields

def write_header(f):
    f.write("This is an automated analysis of your Duke FDS entry.\n")
    f.write("Please do not reply to this message. Contact the current GSO President if you have any concerns.\n")
    f.write("You may modify your FDS entry at: %s\n" % (fds_url))
    f.write("Source code is located at: %s\n" % (source_url))

def write_rating(f, nstudents, totals, rating):
    # Make a shallow copy of the total, so we can modifiy it here.
    total_rating = Counter(totals)
    current_rating = Counter(rating)
    # Get the name and then remove them from the current list
    name = current_rating['name']
    email = current_rating['email']
    del current_rating['name']
    del current_rating['email']
    f.write("\nResult for %s: %s\n" % (name, email))
    # Give a simple score correcting for the name and email fields
    simple_score = (len(rating)-2) / len(total_rating)
    f.write("Simple rating: %4.1f%% Complete profile.\n" % (simple_score * 100))
    f.write("Shorthand: (Percent of grads with this field) Field\n")
    f.write("You have filled in:\n")
    for item in current_rating:
        f.write("  (%4.1f%%) %s\n" % (total_rating[item] / nstudents * 100, item))
        del total_rating[item]
    f.write("You have neglected:\n")
    for item in total_rating:
        f.write("  (%4.1f%%) %s\n" % (total_rating[item] / nstudents * 100, item))
    return True

def write_histogram(f, simple_score, totals, rating):
    score_hist = Counter(simple_score)
    short_score = len(rating) - 2
    f.write("\nHistogram:\n")
    for ii in range(len(totals)):
        if short_score == ii:
            f.write("%2d | %s %s\n" % (ii, score_hist[ii]*"=", "<-- YOU"))
        else:
            f.write("%2d | %s\n" % (ii, score_hist[ii]*"="))
    return True

def write_recommendations(f, rating):
    f.write("\nRecommendations:\n")
    f.write("You can update your information at: %s\n" % (fds_url))
    f.write("These are the most commonly filled-in items,")
    f.write(" and most appear on the physics directory page: %s\n" % (phy_url))
    f.write("It is strongly encouraged that you complete them so we have a useful, professional directory.\n")
    if not rating['Image']:
        f.write('Image: This helps people recognize you and that this is your info.\n')
    if not rating['Office Location']:
        f.write('Office Location: Visitors may like to know where to find you.\n')
    if not rating['Office Phone']:
        f.write('Office Phone: You should have an office phone.\n')
    if not rating['Research Description']:
        f.write('Research Description: This is displayed directly below your primary info.\n')
    if not rating['Recent Publications']:
        f.write('Recent Publications: You should probably get on this....\n')
    if not rating['Specialties']:
        f.write('Specialties: This helps people identify if they need to contact you.\n')
    if not rating['Web Page']:
        f.write('Web Page: You can easially create a Duke webpage at: %s\n'% (duke_site_url))
        f.write('          You can also create a webpage by dropping content in\n')
        f.write('          your public_html folder after ssh-ing into: login.oit.duke.edu\n')
        f.write('          it will appear at http://people.duke.edu/~netID/\n')

if __name__ == "__main__":
    student_urls = get_students(base_url)
    nstudents = len(student_urls)
    # First loop through getting all the info for all students
    print "Beginning first pass to obtain statistics..."
    totals = Counter()
    simple_score = []
    for current_student in student_urls:
        rating = get_rating(current_student)
        totals = totals + rating
        simple_score.append(len(rating) - 2)
    # We don't need a giant string of emails or names
    del totals['email']
    del totals['name']
    print "First Pass complete. Now generating user ratings..."
    # Now go back through the students and e-mail their results
    for current_student in student_urls:
        rating = get_rating(current_student)
        fname = rating['name'] + '.txt'
        f = open(fname, 'wb')
        write_header(f)
        write_rating(f, nstudents, totals, rating)
        write_histogram(f, simple_score, totals, rating)
        write_recommendations(f, rating)
        f.close()
    # Send out the e-mails
    sendyn = raw_input('E-mail results: [y/N]:')
    if sendyn == 'y' or sendyn == 'yes':
        print "Final pass. Sending email..."
        (server, netid) = sm.create_server()
        sub = "FDS Page Ranking"
        sender = '%s@duke.edu' % (netid)
        # For testing purposes, single out my entry
        #rating = get_rating(student_urls[9])
        # Run through all students e-mailing them
        for current_student in student_urls:
            rating = get_rating(current_student)
            # Read the message
            fname = rating['name'] + '.txt'
            f = open(fname, 'rb')
            msg = f.read()
            f.close()
            to = rating['email']
            sm.send_email(server, to, sender, sub, msg)
        # Done, close the email server
        sm.close_server(server)
