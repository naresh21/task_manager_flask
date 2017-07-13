# coding=utf-8
"""
Testing urllib and urllib2 in our ERP
"""
import cookielib
import urllib
import urllib2

from bs4 import BeautifulSoup

USERNAME = 'satyakam.pandya'
PASSWORD = 'Drc@1234'

URL_ERP_LOGIN = 'http://erp.drcsystems.com/'
URL_VIEW_PROFILE = 'http://erp.drcsystems.com/settings/viewprofile'
URL_ERP_LOGOUT = 'http://erp.drcsystems.com/login/logout'

login_info = {
    'LoginForm[username]': USERNAME,
    'LoginForm[password]': PASSWORD
}

cookies = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

# Login to ERP using login_info
login = opener.open(URL_ERP_LOGIN, urllib.urlencode(login_info))

# Opening view profile of current user
view_profile_response = opener.open(URL_VIEW_PROFILE)

# Logout from the system
logout = opener.open(URL_ERP_LOGOUT)

# creating BeautifulSoup object fro view profile response
soup = BeautifulSoup(view_profile_response, "lxml")
birth_date = soup.find("label", {"for": "date_of_birth"})

print "\nYour Birth-date is " + birth_date.text
