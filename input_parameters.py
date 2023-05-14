import re
import datetime

question_string = input('\nInsert a question: ')
print('\nCalculating answer...\n')

question2 = question_string.lower()

why_synonims = ['why', 'which are the', 'tell me the factors', 'factors', 'reasons,' 'for what reason', 
	'what is the reason', 'what is the cause', 'what prompted', 'on what account', 'what is the purpose of', 'which are the factors',
	'what is the motive behind', 'with what intention', 'what is the justification', 'what led to', 'what brought about', 
	'what initiated', 'what provoked', 'what instigated', 'what drove', 'what was the catalyst for', 'what occasioned', 
	'what induced', 'what stirred up', 'what spurred on', 'what influenced', 'what triggered', 'what evoked', 'what elicited', 
	'what compelled', 'what propelled', 'what gave rise to', 'what resulted in', 'what caused', 'what brought on']

list_synonims =  ["list", "enumerate", "catalog", "record", "tabulate", "index", "itemize", "specify", "detail",
    "outline", "chronicle", "enter", "log", "jot down", "write down", "set forth", "register", "document", "schedule",
    "arrange", "organize", "group", "classify", "sort", "systematize", "compile", "inventory", "catalogue", "recite",
     "enumerate", "tabulate"]

# Identify the question type
question_type = "unknown"

for word in list_synonims:
    if word in question2:
        question_type = 'list'
        break
    
for word in why_synonims:
    if word in question2:
        question_type = "why" 
        break

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',' november', 'december']
for month in months:
	if month in question2:
		question2 = question2.replace(month, month[:3])

# Identify the identifiers 
identifyers = re.findall("[A-Z]{1,2}[0-9]+", question_string)
identifyers = tuple(identifyers)

# Identify the date range
date_pattern = r"(?:\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}(?:st|nd|rd|th)?|\d{1,2}[/-]\d{1,2}[/-](?:\d{2})?\d{2})\b)"

# Buscar las fechas en la pregunta y guardarlas en una lista
dates = re.findall(date_pattern, question2)

# Convertir las fechas en formato "%Y-%m-%d"
date_range = []
for date in dates:
	try:
		date_obj = datetime.datetime.strptime(date, "%b %d")
		date_obj = date_obj.replace(year=datetime.datetime.now().year)
		date_str = date_obj.strftime("%Y-%m-%d")
		date_range.append(date_str)
	except ValueError:
		try:
			date_obj = datetime.datetime.strptime(date, "%b %d")
			date_obj = date_obj.replace(year=datetime.datetime.now().year)
			date_str = date_obj.strftime("%Y-%m-%d")
			date_range.append(date_str)
		except ValueError:
			pass
			
if len(date_range) == 1:
	# Add one day to get the second date
	date_obj = datetime.datetime.strptime(date_range[0], "%Y-%m-%d")
	date_obj += datetime.timedelta(days=1)
	date_str = date_obj.strftime("%Y-%m-%d")
	list_date = date_str.split(sep='-')
	list_date[2] = str(int(list_date[2])-1)
	date_str = f"{list_date[0]}-{list_date[1]}-{list_date[2]}"
	date_range.append(date_str)

if len(date_range) == 0:
	date_range.append('')
	date_range.append('')
	
date_range = tuple(date_range)

# Identify the quantity variance
quantity_variance = ((None, None), False)

# Buscar los números que cumplan con los criterios de cantidad
numbers = re.findall(r'\d{1,2}\d*[U]{0,1}\d{2,}', question_string)
if len(numbers) == 2:
	if numbers[0] == numbers[1]:
		quantity_variance = ((float(numbers[0]), float(numbers[1])), False)
	else:
		quantity_variance = ((float(numbers[0]), float(numbers[1])), True)

elif len(numbers) == 1:
	#si hay un numero 0 en la pregunta, el segundo numero es 0
	if ' 0 ' in question_string:
		quantity_variance = ((float(numbers[0]), float('0')), True)
	else:
		quantity_variance = ((float(numbers[0]), float(numbers[0])), False)

def change_identifyers(identifyers):
	final_identifyers = ['', '', '', '', '', '']
	for element in identifyers:
			element = element.lower()
			if element[0] == 'a':
				final_identifyers[0] = element.upper()
			elif element[0] == 'b':
				final_identifyers[1] = element.upper()
			elif element[:2] == 'co':
				final_identifyers[3] = element.upper()
			elif element[:2] == 'cn':
				final_identifyers[5] = element.upper()
			elif element[:2] == 'pc':
				final_identifyers[4] = element.upper()
			elif element[0] == 'c':
				final_identifyers[2] = element.upper()
	return tuple(final_identifyers)

identifyers = change_identifyers(identifyers)

#Identify the transaction_info

transaction_info = ['', '', '']

InstrumentType = ['futures', 'cash', 'takes', 'options', 'given', 'pufix', 'executed not priced']

for word in InstrumentType:
    if word in question_string:
        transaction_info[2] = word.upper()

if 'sales' in question_string or 'sale' in question_string:
    transaction_info[1] = 'SALES'
    transaction_info[0] = 'Sell'

elif 'purchase' in question_string or 'purchases' in question_string:
    transaction_info[1] = 'PURCHASE'
    transaction_info[0] = 'Buy'

elif 'inventory' in question_string or 'inventories' in question_string:
    transaction_info[1] = 'INVENTORY'
    transaction_info[0] = 'Buy'

elif 'offset' in question_string or 'offsets' in question_string:
    transaction_info[1] = 'OFFSET'
    transaction_info[0] = 'Buy'

transaction_info = tuple(transaction_info)