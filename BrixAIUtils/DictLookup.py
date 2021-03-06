import lxml.html 
from .Cache import Cache

def lookup (word):
    pron, desc, rela = '', '', [] 
    link = "http://tratu.soha.vn/dict/en_vn/"
    doc = lxml.html.parse(link + word)
    raw_of_pron = doc.xpath("//div[contains(@id, 'content-5')]")
    raw_of_desc = doc.xpath("//div[contains(@id, 'show-alter')]")
    raw_of_rela = doc.xpath("//div[contains(@id, 'content-2')]")

    if len(raw_of_pron) is not 0:
        pron = raw_of_pron[0].text_content()
    if len(raw_of_desc) is not 0:
        desc = raw_of_desc[0].text_content()
    if len(raw_of_rela) is not 0:
        rela = [item.text_content() for item in raw_of_rela]

    return pron, desc, rela

class EV_dict_cache (Cache):
	def __init__ (self):
		Cache.__init__(self, "EV_dict_cache", 10)
	
	def fetch (self, tag):
		pron, desc, rela = lookup (tag)
		return pron + desc + ''.join(rela)
