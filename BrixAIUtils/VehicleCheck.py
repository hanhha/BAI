import lxml.html 
from argparse import ArgumentParser as ArgParser

def check_violation (plate):
	link = "http://tracuuvipham.com/partials/list.php?"
	doc = lxml.html.parse(link + "type=2&bienso=" + plate)
	raw_list_of_vi = doc.xpath("//div[contains(@class, 'panel b text-center')]")
	list_of_vi = []
	for idx, raw_report in enumerate (raw_list_of_vi):
		report = raw_report.xpath(".//p")
		vi_entry = {
				'date'        : report[0].text_content().split(":")[1].strip(),
				'place'       : report[1].text_content().split(":")[1].strip(),
				'description' : report[2].text_content().split(":")[1].strip(),
				'dept'        : report[3].text_content().split(":")[1].strip(),
				}
		list_of_vi.append (vi_entry)

	return list_of_vi

#ap = ArgParser()
#ap.add_argument ('-p', '--plate', default = '51f-81420', help = 'Plate number')
#args = ap.parse_args ()
#plate = args.plate
#
#list_of_vi = check_violation (plate)
#
#for idx, report in enumerate(list_of_vi):
#	print 'Loi %d' %(idx + 1)
#	print 'Ngay vi pham: %s'  %(report['date'])
#	print 'Vi tri vi pham: %s'  %(report['place'])
#	print 'Loi vi pham: %s'  %(report['description'])
#	print 'Co quan xu ly: %s' %(report['dept'])

