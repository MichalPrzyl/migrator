class Finder:

	def fuzzy_find(self, phrase, where):
		found_elements = [element for element in where if phrase in element]
		if len(found_elements) == 0:
			return None
		elif len(found_elements) == 1:
			return found_elements[0]
		else:
			return sorted(found_elements, reverse=True)[0]
				