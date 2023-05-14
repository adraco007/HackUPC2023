import pandas as pd
from input_parameters import *

# Set the data frame
df = pd.read_csv('Challenge Dataset.csv', sep=';')
df['Position Date'] = pd.to_datetime(df['Position Date'], dayfirst=True)
df['Position Month'] = pd.to_datetime(df['Position Month'], dayfirst=True)
df['Quantity'] = df['Quantity'].astype(str).str.replace(",", ".")
df['Quantity'] = df['Quantity'].astype(float)
df = df.drop_duplicates()

# Function definitions
def question(question_type:str='list', # 'list', 'why'
					identifyers:tuple=('', '', '', '', '', ''), 
						transaction_info:tuple=('', '', ''), 
							date_range:tuple=('',''),
									quantity_variance:tuple=((None, None), False)):	
	answers = ['y', 'yes', 'y.', 'yes.']
	if question_type == 'list':
		return_df = clip_identifyers(df, identifyers)
		return_df = clip_date(return_df, date_range)
		return_df = clip_transaction_info(return_df, transaction_info)
		return_df = clip_quantity(return_df, identifyers, quantity_variance)
		print(only_indentifyers(return_df))
		if input('\nDo you want to see all the details of the table? [Yes/No]: ').lower() in answers:
			print('\n', return_df)
			if input('\nDo you want to save this full table in a new "Results.csv" file? [Yes/No]: ').lower() in answers:
				return_df.to_csv('Results.csv', index=False)

	elif question_type == 'why':
		return_df = clip_identifyers(df, identifyers)
		return_df = clip_date(return_df, date_range)
		return_df = clip_transaction_info(return_df, transaction_info)
		return_df = clip_quantity(return_df, identifyers, quantity_variance)
		print(return_df)
		if input('\nDo you want to save this full table in a new "Results.csv" file? [Yes/No]: ').lower() in answers:
			return_df.to_csv('Results.csv', index=False)
	else:
		print('Please repeat the process with a more clear question')
	return '\nFinished\n'

def clip_date(df, date_range:tuple):
	"""
	Returns a new dataframe with only the rows between the date range given, including both dates.
	"""
	if date_range[0] == '' and date_range[1] == '':
		return df

	start_date = date_range[0]
	final_date = date_range[1]
	return df[(df['Position Date'] >= start_date) & (df['Position Date'] <= final_date)]

def select_identifyer_column(identifyer:str):
	"""
	Returns the name of the column associated to the given identifyer.
	"""
	if identifyer == '' or pd.isna(identifyer):
		return None
	else:
		identifyer = identifyer.lower()
		if identifyer[0] == 'a':
			return 'Account Original'
		elif identifyer[0] == 'b':
			return 'Business Sub Unit'
		elif identifyer[:2] == 'co':
			return 'Commodity Original'
		elif identifyer[:2] == 'cn':
			return 'Contract Number'
		elif identifyer[:2] == 'pc':
			return 'Profit Center'
		elif identifyer[0] == 'c':
			return 'Commodity Sub Sub Group'

def clip_identifyers(df, identifyers:tuple):
	"""
	Returns a new df with only the rows that have the identifyers specifyed.
	"""
	new_df = df.copy()
	for identifyer in identifyers:
		if (column:=select_identifyer_column(identifyer)) is not None:
			new_df = new_df[new_df[column] == identifyer]
	return new_df

def select_transaction_info_column(transaction:str):
	"""
	Returns the name of the column associated with the transaction given.
	"""
	if transaction == '' or pd.isna(transaction):
		return None
	else:
		transaction = transaction.lower()
		if transaction in ('buy', 'sell'):
			return 'Buy Sell'
		elif transaction in ('purchase', 'inventory', 'sales', 'offset'):
			return 'Document Type'
		elif transaction in ('futures', 'cash', 'takes', 'options', 'gives', 'pufix', 'executed not priced'):
			return 'Instrument Type'

def clip_transaction_info(df, transaction_info:tuple):
	"""
	Returns a new df with only the rows that have the transactions specifyed. 
	"""
	new_df = df
	for transaction in transaction_info:
		if (column:=select_transaction_info_column(transaction)) is not None:
			new_df = new_df[new_df[column] == transaction]
	
	return new_df

# Necessary to have clipped by date
def clip_quantity(df, identifyers:tuple, quantity_variance:tuple):
		# Returns df
	if (quantity_variance[0][0] is None and quantity_variance[0][1] is None) and not quantity_variance[1]:
			return df

	elif ''.join(identifyers) == '': # There are no identifyers specifyed (we are looking for a particular quantity)
		new_df = pd.DataFrame(columns=df.columns) # Create an empty DataFrame

		# Returns all the contracts of a particular quantity that have not changed the quantities
		if (quantity_variance[0][0] == quantity_variance[0][1]) and (quantity_variance[0][0] is not None) and (not quantity_variance[1]):
			quantity_changes = df[round(abs(df['Quantity'])) == quantity_variance[0][0]]

			list_identifyers = []
			for _, row in quantity_changes.iterrows():
				new_identifyers = tuple(row[:6])
				if new_identifyers not in list_identifyers:
					list_identifyers.append(new_identifyers)
			
			for new_identifyers in list_identifyers:
				new_df = new_df._append(clip_identifyers(df, new_identifyers))

			return new_df

		# Returns all the contracts that have changed from a particular quantity to another particular quantity
		elif quantity_variance[0][0] != quantity_variance[0][1] and quantity_variance[1]:	
			list_identifyers1 = []
			df_1 = df.loc[round(abs(df['Quantity'])) == quantity_variance[0][0]]
			for _, row in df_1.iterrows():
				list_identifyers1.append(tuple(row[:6]))

			list_identifyers2 = []
			df_2 = df.loc[round(abs(df['Quantity'])) == quantity_variance[0][1]]
			for _, row in df_2.iterrows():
				list_identifyers2.append(tuple(row[:6]))

			list_identifyers3 = list(set(list_identifyers1) & set(list_identifyers2))			
			for final_identifyers in list_identifyers3:
				new_df = new_df._append(clip_identifyers(df, final_identifyers))
			
			return new_df
		
		# Returns all the contracts that have changed
		elif (quantity_variance[0][0] is None or quantity_variance[0][1] is None) and quantity_variance[1]:	
			# Crear un diccionario donde las claves son los identificadores y los valores son una lista de valores de la columna 'Quantity' correspondientes a ese identificador.
			identifier_dict = {}
			for index, row in df.iterrows():
				identifier = tuple(row[:6])
				quantity = round(row['Quantity'])
				if identifier in identifier_dict:
					identifier_dict[identifier].append(quantity)
				else:
					identifier_dict[identifier] = [quantity]

			# Iterar sobre el diccionario y buscar si hay algún identificador con más de un valor en su lista de 'Quantity'.
			duplicate_identifiers = []
			for identifier, quantity_list in identifier_dict.items():
				if len(set(quantity_list)) < len(quantity_list):
					duplicate_identifiers.append(identifier)

			# Crear un nuevo dataframe que contenga solo las filas con los identificadores repetidos.
			if duplicate_identifiers:
				return df[df.apply(lambda x: tuple(x[:6]) in duplicate_identifiers, axis=1)]
			else:
				return pd.DataFrame(columns=df.columns)

	else: # There are identifyers specifyed (we are looking for the sum of the contracts that have the given identifyers)
		# We assume that the values asked are correct, so we are not going to calculate these values		
		return df

def only_indentifyers(df):
	new_df = df.iloc[:, :6]
	new_df = new_df.drop_duplicates()
	return new_df
