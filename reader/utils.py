import urllib2


def url_to_domain(url):
    return urllib2.Request(url).get_host()
