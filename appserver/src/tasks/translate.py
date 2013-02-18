#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import uuid

mt = {
	'en_de': {
		"This difference was not statistically significant.": "Der Unterschied war statistisch nicht signifikant."
	},
	'de_en': {
		"Der Unterschied war statistisch nicht signifikant.": "This difference was not statistically significant."
	}
}

def process_task(task):
	try:
		f = task['sourceLang']
		e = task['targetLang']
		key = f + "_" + e
		t = task['text']
		return {
			'translation': [
				{
					"translationId": uuid.uuid4().hex,
					"translated": mt[f + "_" + e][t] or "#NOT FOUND",
					"score": 100,
				}
			]
		}
	except:
		return {
				"error": "Translation not found or a malformed query (please consult CUNI)",
				"error_code": 101,
			}
