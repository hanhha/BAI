import lxml.html 

def check_violation (plate):
	link = "http://tracuuvipham.com/partials/list.php?"
	doc = lxml.html.parse(link + "type=1&bienso=" + plate)
	#doc = lxml.html.parse(link + "type=2&bienso=" + plate)
	raw_list_of_vi = doc.xpath("//div[contains(@class, 'panel b text-center')]")
	list_of_vi = []
	for idx, raw_report in enumerate (raw_list_of_vi):
		report = raw_report.xpath(".//p/b/following-sibling::text()[1]")
		vi_entry = {
				'date'        : report[0].strip(),
				'place'       : report[1].strip(),
				'description' : report[2].strip(),
				'dept'        : report[3].strip(),
				}
		list_of_vi.append (vi_entry)

	return list_of_vi
