import numpy as np
import os
import json

class FilmDB:
	
	def __init__(self, arg=None, **params):
		self._initialize(params)
	
	def _initialize(self, params):
		# mapping title_string to t_s/dir. inits./color flag/year
		self.actionDB = {
			'3_Bad_Men' : ['3_Bad_Men', 'JF', 0, 1926],
			'3_Godfathers' : ['3_Godfathers', 'JF', 1, 1948],
			'A_Serious_Man': ['A_Serious_Man', 'CB', 1, 2009],
			'A_Woman_is_a_Woman': ['A_Woman_is_a_Woman' , 'JLG', 1, 1961],
			'Alphaville': ['Alphaville', 'JLG', 0, 1965],
			'Amistad': ['Amistad', 'SS', 1, 1997],
			'Arrowsmith': ['Arrowsmith', 'JF', 0, 1931],
			'Barton_Fink': ['Barton_Fink', 'CB', 1, 1991],
			'Belle_de_Jour': ['Belle_de_Jour', 'LB', 1, 1967],
			'Black_Swan': ['Black_Swan', 'DA', 1, 2010],
			'Blood_Simple': ['Blood_Simple', 'CB', 1, 1984],
			'Blue_Velvet': ['Blue_Velvet', 'DL', 1, 1986],
			'Bringing_Up_Baby': ['Bringing_Up_Baby', 'HH', 0, 1938],
			'Burn_After_Reading': ['Burn_After_Reading', 'CB', 1, 2008],
			'Catch_Me_If_You_Can': ['Catch_Me_If_You_Can', 'SS', 1, 2002],
			'Cheyenne_Autumn': ['Cheyenne_Autumn', 'JF', 1, 1964],
			'Death_in_the_Garden' : ['Death_in_the_Garden', 'LB', 1, 1956],
			'Dersu_Uzala': ['Dersu_Uzala', 'AK', 1, 1975],
			'Detective': ['Detective', 'JLG', 1, 1985],
			'Diary_of_a_Country_Priest': ['Diary_of_a_Country_Priest', 'RBr', 0, 1951],
			#'Discreet_Charm': ['Discreet_Charm', 'LB', 1, 1972],
			'Dreams': ['Dreams', 'AK', 1, 1990],
			'Drunken_Angel': ['Drunken_Angel', 'AK', 0, 1948],
			'Duel': ['Duel', 'SS', 1, 1971],
			'Dune': ['Dune', 'DL', 1, 1984],
			'Early_Spring' : ['Early_Spring', 'YO', 0, 1956],
			'Early_Summer' : ['Early_Summer', 'YO', 0, 1951],
			'Enthusiasm' : ['Enthusiasm', 'DzV', 0, 1930], #### DOC
			'Equinox_Flower' : ['Equinox_Flower', 'YO', 1, 1958],
			'Eraserhead': ['Eraserhead', 'DL', 0, 1977],
			'ET': ['ET', 'SS', 1, 1982],
			'Exterminating_Angel': ['Exterminating_Angel', 'LB', 0, 1962],
			'Fargo': ['Fargo', 'CB', 1, 1996],
			'Fata_Morgana': ['Fata_Morgana', 'WH', 1, 1971],
			'Foreign_Correspondent': ['Foreign_Correspondent', 'AH', 0, 1940],
			'Fort_Apache' : ['Fort_Apache', 'JF', 0, 1948],
			'Frenzy': ['Frenzy', 'AH', 1, 1972],
			'Gentlemen_Prefer_Blondes': ['Gentlemen_Prefer_Blondes', 'HH', 1, 1953],
			'Grapes_of_Wrath' : ['Grapes_of_Wrath', 'JF', 0, 1940],
			'Hangmans_House' : ['Hangmans_House', 'JF', 0, 1928],
			'High_and_Low' : ['High_and_Low', 'AK', 0, 1963],
			'His_Girl_Friday': ['His_Girl_Friday', 'HH', 0, 1940],
			'How_Green_Was_My_Valley' : ['How_Green_Was_My_Valley', 'JF', 0, 1941],
			'How_to_Survive_a_Plague' : ['How_to_Survive_a_Plague', 'DFr', 1, 2012],
			'I_Was_Born_But' : ['I_Was_Born_But', 'YO', 0, 1932],
			'In_Praise_of_Love' : ['In_Praise_of_Love', 'JLG', 1, 2001],
			'Indiana_Jones_and_the_Last_Crusade' : ['Indiana_Jones_and_the_Last_Crusade', 'SS', 1, 1989],
			'Indiana_Jones_and_the_Temple_of_Doom' : ['Indiana_Jones_and_the_Temple_of_Doom', 'SS', 1, 1984],	
			'Inland_Empire' : ['Inland_Empire', 'DL', 1, 2006],
			'Ivans_Childhood' : ['Ivans_Childhood', 'AT', 0, 1962],
			'Jeanne_Dielman':  ['Jeanne_Dielman', 'ChA', 1, 1975],
			'Kagemusha': ['Kagemusha', 'AK', 1, 1980],
			'Koyaanisqatsi': ['Koyaanisqatsi', 'GoR', 1, 1982],
			'L_Age_D_Or': ['L_Age_D_Or', 'LB', 0, 1930],
			'Las_Hurdes': ['Las_Hurdes', 'LB', 0, 1933], ## 'TERRE SANS PAIN"
			'Late_Autumn': ['Late_Autumn', 'YO', 1, 1960],
			'Late_Spring': ['Late_Spring', 'YO', 0, 1949],
			'Le_Petit_Soldat': ['Le_Petit_Soldat', 'JLG', 0, 1963],
			#'Le_Quattro_Volte': ['Le_Quattro_Volte', 'MFr', 1, 2010],
			'Les_Dames_du_Bois_de_Boulogne': ['Les_Dames_du_Bois_de_Boulogne', 'MD', 0, 1945],
			'Los_Olvidados': ['Los_Olvidados', 'LB', 0, 1950],
			'Lost_Highway': ['Lost_Highway', 'DL', 1, 1997],
			'Madadayo': ['Madadayo', 'AK', 1, 1993],
			'Made_in_USA': ['Made_in_USA', 'JLG', 1, 1966],
			'Marnie': ['Marnie', 'AH', 1, 1964],
			'Meshes_of_the_Afternoon': ['Meshes_of_the_Afternoon', 'AHa', 0, 1943],
			'Millers_Crossing': ['Millers_Crossing', 'CB', 1, 1990],
			'Mother': ['Mother', 'VsP', 0, 1926],
			'Mr_and_Mrs_Smith': ['Mr_and_Mrs_Smith', 'AH', 0, 1941],
			'Mulholland_Drive': ['Mulholland_Drive', 'DL', 1, 2001],
			'Munich': ['Munich', 'SS', 1, 2005],
			'My_Darling_Clementine': ['My_Darling_Clementine', 'JF', 0, 1946],
			'My_Name_is_Ivan' : ['My_Name_is_Ivan', 'AT', 0, 1962], ## same as Ivans Childhood
			'Nazarin': ['Nazarin', 'LB', 0, 1959],
			'No_Blood_Relation': ['No_Blood_Relation', 'MiN', 0, 1932],
			'North_by_Northwest': ['North_by_Northwest', 'AH', 1, 1959],
			'Notorious': ['Notorious', 'AH', 0, 1946],
			'Notre_Musique': ['Notre_Musique', 'JLG', 1, 2004],
			'O_Brother_Where_Art_Thou': ['O_Brother_Where_Art_Thou', 'CB', 1, 2000],
			'Only_Angels_Have_Wings': ['Only_Angels_Have_Wings', 'HH', 0, 1939],
			'Passing_Fancy' : ['Passing_Fancy', 'YO', 0, 1933],
			'Pi': ['Pi', 'DA', 0, 1998],
			'Pierrot_le_Fou': ['Pierrot_le_Fou', 'JLG', 1, 1965],
			'Psycho': ['Psycho', 'AH', 0, 1960],
			'Raiders_of_the_Lost_Ark': ['Raiders_of_the_Lost_Ark', 'SS', 1, 1981],
			'Raising_Arizona': ['Raising_Arizona', 'CB', 1, 1987],
			'Ran': ['Ran', 'AK', 1, 1985],
			'Rashomon': ['Rashomon', 'AK', 0, 1950],
			'Rear_Window': ['Rear_Window', 'AH', 1, 1954],
			'Rebecca': ['Rebecca', 'AH', 0, 1940],
			'Requiem_for_a_Dream': ['Requiem_for_a_Dream', 'DA', 1, 2000],
			'Rio_Bravo': ['Rio_Bravo', 'HH', 1, 1959],
			'Robinson_Crusoe': ['Robinson_Crusoe', 'LB', 1, 1954],
			'Rope': ['Rope', 'AH', 1, 1948],
			'Saving_Private_Ryan': ['Saving_Private_Ryan', 'SS', 1, 1998],
			'Schindlers_List': ['Schindlers_List', 'SS', 1, 1993],
			'Seven_Samurai': ['Seven_Samurai', 'AK', 0, 1954],
			'Shadow_of_a_Doubt': ['Shadow_of_a_Doubt', 'AH', 0, 1943],
			'Soigne_ta_Droite': ['Soigne_ta_Droite', 'JLG', 1, 1987],
			'Stagecoach': ['Stagecoach', 'JF', 0, 1939],
			'Straight_Story': ['Straight_Story', 'DL', 1, 1999],
			'Strangers_on_a_Train': ['Strangers_on_a_Train', 'AH', 0, 1951],
			'Sullivans_Travels': ['Sullivans_Travels', 'PSt', 0, 1941],
			'That_Obscure_Object_of_Desire': ['That_Obscure_Object_of_Desire', 'LB', 1, 1977],
			'The_39_Steps': ['The_39_Steps', 'AH', 0, 1935],
			'The_Big_Lebowski': ['The_Big_Lebowski', 'CB', 1, 1998],
			'The_Big_Sleep': ['The_Big_Sleep', 'HH', 0, 1946],
			'The_Birds': ['The_Birds', 'AH', 1, 1963],
			'The_Color_Purple': ['The_Color_Purple', 'SS', 1, 1985],
			'The_End_of_Summer': ['The_End_of_Summer', 'YO', 1, 1961],
			'The_Fountain': ['The_Fountain', 'DA', 1, 2006],
			'The_Hidden_Fortress': ['The_Hidden_Fortress', 'AK', 0, 1958],
			'The_Hudsucker_Proxy': ['The_Hudsucker_Proxy', 'CB', 1, 1994],
			'The_Lady_Vanishes': ['The_Lady_Vanishes', 'AH', 0, 1938],
			'The_Man_Who_Knew_Too_Much': ['The_Man_Who_Knew_Too_Much', 'AH', 1, 1956],
			'The_Man_Who_Shot_Liberty_Valance': ['The_Man_Who_Shot_Liberty_Valance', 'JF', 0, 1962],
			'The_Milky_Way': ['The_Milky_Way', 'LB', 1, 1969],
			'The_Mirror': ['The_Mirror', 'AT', 0, 1975],
			#'The_Phantom_of_Liberty': ['The_Phantom_of_Liberty', 'LB', 1, 1974],
			'The_Pleasure_Garden': ['The_Pleasure_Garden', 'AH', 0, 1925],
			'The_Quiet_Man': ['The_Quiet_Man', 'JF', 1, 1952],
			'The_Sacrifice' : ['The_Sacrifice', 'AT', 1, 1986],
			'The_Searchers': ['The_Searchers', 'JF', 1, 1956],
			'The_Wrestler': ['The_Wrestler', 'DA', 1, 2008],
			'The_Wrong_Man': ['The_Wrong_Man', 'AH', 0, 1956],
			'Throne_of_Blood': ['Throne_of_Blood', 'AK', 0, 1957],
			'Tokyo_Chorus': ['Tokyo_Chorus', 'YO', 0, 1931],
			'Tokyo_Story' : ['Tokyo_Story', 'YO', 0, 1953],
			'Tokyo_Twilight': ['Tokyo_Twilight', 'YO', 0, 1957],
			'Torn_Curtain': ['Torn_Curtain', 'AH', 1, 1966],
			'Tout_Va_Bien': ['Tout_Va_Bien', 'JLG', 1, 1972],
			'Tristana': ['Tristana', 'LB', 1, 1970],
			'Twin_Peaks': ['Twin_Peaks', 'DL', 1, 1992],
			'Twin_Peaks_Ep1': ['Twin_Peaks_Ep1', 'DL', 1, 1990],
			'Un_Chien_Andalou': ['Un_Chien_Andalou', 'LB', 0, 1929],
			'Uncle_Boonme_Who_Can_Recall_His_Past_Lives': ['Uncle_Boonme_Who_Can_Recall_His_Past_Lives', 'AWe', 1, 2010],
			'Vampyr': ['Vampyr', 'CTD', 0, 1932],
			'Vertigo': ['Vertigo', 'AH', 1, 1958],
			'Viridiana': ['Viridiana', 'LB', 0, 1961],
			'War_Horse': ['War_Horse', 'SS', 1, 2011],
			'Weekend': ['Weekend', 'JLG', 1, 1967],
			'Wild_at_Heart': ['Wild_at_Heart', 'DL', 1, 1990],
			'Young_Mr_Lincoln': ['Young_Mr_Lincoln', 'JF', 0, 1939]}
		
		self.actionDocumentariesDB = {
			'About_Russian_Ark' : ['About_Russian_Ark', 'Aleksandr Sokurov', 1, 2002],
			'Andrei' : ['Andrei', 'Andrei Tarkovsky', 1, 1966],
			'CHRONICLE_OF_A_SUMMER' : ['CHRONICLE_OF_A_SUMMER', 'Jean Rouch', 0, 1961],
			'ELEGY_OF_MOSCOW' : ['ELEGY_OF_MOSCOW', 'Aleksandr Sokurov', 1, 1987],
			'FALL_ROMANOV_DYNASTY' : ['FALL_ROMANOV_DYNASTY', 'Esfi Shub', 0, 1975],
			'HIROSHIMA_MON_AMOUR' : ['HIROSHIMA_MON_AMOUR', 'Alain Resnais', 0, 1959],
			'IN_THE_YEAR_OF_THE_PIG' : ['IN_THE_YEAR_OF_THE_PIG', 'Emile de Antonio', 0, 1968],
			'IRONHORSE_1924' : ['IRONHORSE_1924', 'John Ford', 0, 1924],
			'IRONHORSE_INTL_0' : ['IRONHORSE_INTL_0', 'John Ford', 0, 1924],
			'LET_THERE_BE_LIGHT' : ['LET_THERE_BE_LIGHT', 'John Huston', 0, 1946],
			'Murrow_Harvest' : ['Murrow_Harvest', 'Fred Friendly', 0, 1960],			
			'NANOOK' : ['NANOOK', 'Claude Massot', 0, 1922],
			'NOSTALGHIA' : ['NOSTALGHIA', 'Andrei Tarkovsky', 0, 1983],
			'Primary_1960' : ['Primary_1960', 'Robert Drew', 0, 1960],
			'Primary_Long_1960' : ['Primary_Long_1960', 'Robert Drew', 0, 1960],
			'RUSSIAN_ARK' : ['RUSSIAN_ARK', 'Aleksandr Sokurov', 1, 2002],			
			'SACRIFICE' : ['SACRIFICE', 'Andrei Tarkovsky', 1, 1986],
			'SHOAH_part1' : ['SHOAH_part1', 'Claude Lanzmann', 1, 1985],
			'STEAMROLLER_AND_VIOLIN' : ['STEAMROLLER_AND_VIOLIN', 'Andrei Tarkovsky', 0, 1960],
			'SYMBIOPSYCHOTAXIPLASM' : ['SYMBIOPSYCHOTAXIPLASM', 'William Greaves', 1, 1968],
			'SYMBIOPSYCHOTAXIPLASM_2' : ['SYMBIOPSYCHOTAXIPLASM_2', 'William Greaves', 1, 2005],
			'THE_MAN_WITH_THE_MOVIE_CAMERA' : ['THE_MAN_WITH_THE_MOVIE_CAMERA', 'Dziga Vertov', 0, 1929]}

		self.actionPaperPrintDB = {
			'A_Strange_Meeting_1909': ['A_Strange_Meeting_1909', 'other', 0, 1909],
			'At_the_Altar_1909': ['At_the_Altar_1909', 'other', 0, 1909],
			'Cord_of_Life_1909': ['Cord_of_Life_1909', 'other', 0, 1909],
			'Fools_of_Fate_1909': ['Fools_of_Fate_1909', 'other', 0, 1909],
			'Four_Sons_1928': ['Four_Sons_1928', 'other', 0, 1928],
			'Goddess_of_Sagebrush_Gulch_1912': ['Goddess_of_Sagebrush_Gulch_1912', 'other', 0, 1912],
			'Married_for_Millions': ['Married_for_Millions', 'other', 0, 1906],
			'Sherlock_Holmes_Baffled_1900': ['Sherlock_Holmes_Baffled_1900', 'other', 0, 1900],
			'The_Light_That_Came_1909': ['The_Light_That_Came_1909', 'other', 0, 1909],					
			'The_Necklace_1909': ['The_Necklace_1909', 'other', 0, 1909],
			'The_Restoration_1909': ['The_Restoration_1909', 'other', 0, 1909],
			'The_Tramp_and_the_Muscular_Cook_1898': ['The_Tramp_and_the_Muscular_Cook_1898', 'other', 0, 1898],
			'The_Two_Paths_1911': ['The_Two_Paths_1911', 'other', 0, 1911],
			'Whats_Your_Hurry_1909': ['Whats_Your_Hurry_1909', 'other', 0, 1909],
			'Who_Pays_for_the_Drinks_1903': ['Who_Pays_for_the_Drinks_1903', 'other', 0, 1903],
			'Winning_Back_His_Love_1910': ['Winning_Back_His_Love_1910', 'other', 0, 1910],
			'With_the_Enemys_Help_1912': ['With_the_Enemys_Help_1912', 'other', 0, 1912]}
		
		#self.actionDocumentariesDB...
		
		# mapping of directors from initials to name + number of films + b+w/color flag
		self.actionDirectors = {
			'AH'  : ['Alfred Hitchcock', 0, 0],
			'AHa' : ['Alexander Hammid', 0, 0],
			'AK'  : ['Akira Kurosawa', 0, 0],
			'AT'  : ['Andrei Tarkovsky', 0, 0],
			'AWe' : ['Apichatpong Weerasethakul', 0, 0],
			'CB'  : ['Coen Brothers', 0, 0],
			'ChA' : ['Chantai Akerman', 0, 0],
			'CTD' : ['Carl Theodor Dreyer', 0, 0],
			'DA'  : ['Darren Aronofsky', 0, 0],
			'DFr' : ['David France', 0, 0],
			'DL'  : ['David Lynch', 0, 0],
			'DzV' : ['Dziga Vertov', 0, 0],
			'JLG' : ['Jean-Luc Godard', 0, 0],
			'JF'  : ['John Ford', 0, 0],
			'GoR' : ['Godfrey Reggio', 0, 0],
			'HH'  : ['Howard Hawks', 0, 0],
			'LB'  : ['Luis Bunuel', 0, 0],
			'MD'  : ['Maya Deren', 0, 0],
			#'MFr' : ['Michelangelo Frammartino', 0, 0],
			'MiN' : ['Mikio Naruse', 0, 0],
			'PSt' : ['Preston Sturges', 0, 0],
			'RBr' : ['Robert Bresson', 0, 0],
			'SS'  : ['Steven Spielberg', 0, 0],
			'VsP' : ['Vsevolod Pudovkin', 0, 0],
			'WH'  : ['Werner Herzog', 0, 0],
			'YO'  : ['Yasujiro Ozu', 0, 0], 
			'other' : ['other', 0, 0]}
		
	def get_available_directors(self, justInits=False):
		if justInits:
			return sorted([self.actionDirectors[full][0] for full in self.actionDirectors.keys()])
		else:
			return sorted(self.actionDirectors.keys())
	
	def actionDB_ordered_by_title(self, full_directors=False):
		"""
		Return the information lists (4 items per film) sorted by title, with either the directors' initials or the full names.
		"""
		if full_directors:
			with_inits = [self.actionDB[ttl] for ttl in self.actionDB.keys()]
			with_inits.sort()
			return [[entry[0],self.actionDirectors[entry[1]][0],entry[2],entry[3]] for entry in with_inits]
		else:
			with_inits = [self.actionDB[ttl] for ttl in self.actionDB.keys()]
			with_inits.sort()
			return with_inits	
	
	def create_analysis_pool(self, directors, cflag):
		analysisPool = dict()
		for dir in directors:
			for entry in self.actionDB:
				# print self.actionDB[entry]
				if ((self.actionDB[entry][2] == cflag) or (cflag == 2)) and (self.actionDB[entry][1] in directors):
					# print "ADD TO SET: ", entry
					try:
						analysisPool[self.actionDB[entry][1]].add(self.actionDB[entry][0])
					except KeyError:
						analysisPool[self.actionDB[entry][1]] = set([self.actionDB[entry][0]])
		return analysisPool
	
	def films_for_director(self, director):
		"""
		Look up films by director initials.
		"""
		films = []
		for ttl in sorted(self.actionDB.keys()):
			if (self.actionDB[ttl][1] == director):
				films += [ttl]
		return films
	
	def films_for_director_with_year(self, director):
		films = []
		for ttl in sorted(self.actionDB.keys()):
			if (self.actionDB[ttl][1] == director):
				films += [[ttl, self.actionDB[ttl][3]]]
		return films
	
	def films_for_year(self, year):
		return [ttl for ttl in sorted(self.actionDB.keys()) if self.actionDB[ttl][3] == year]
	 
	def all_black_and_white_films(self):
		"""
		Returns a sorted list of all black and white film titles
		"""
		return [ttl for ttl in sorted(self.actionDB.keys()) if self.actionDB[ttl][2] == 0]

	def all_color_films(self):
		"""
		Returns a sorted list of all color film titles
		"""
		return [ttl for ttl in sorted(self.actionDB.keys()) if self.actionDB[ttl][2] == 1]

	def as_structured_array(self):
		fields=[('title','|S64'),('director','|S32'),('color','int'),('year','int')]
		A = self.actionDB_ordered_by_title()
		np.savetxt('actionDB.txt',np.array(A),fmt='%s %s %s %s')
		A = np.loadtxt('actionDB.txt', dtype=fields)
		return A

	def write_actionDB_html_table(self, fname='action_db.html', write_metadata_files=False, json_file_dir='actiondata'):
		A = self.actionDB_ordered_by_title()
		with open(fname,'w') as outfile:
			outfile.writelines(['<html>\n','<head>','</head>\n','<body>\n'])
			outfile.write('<h1>List of ActionDB Films</h1>\n')
			outfile.write('<h3>Click titles for example segmentations and similarity matrices.</h3>\n')
			outfile.write('<table cellpadding="4" style="border: 1px solid #000000; border-collapse: collapse;" border="1">\n')
			title = ''
			for film in A:
				outfile.write('<tr>')
				s = None
				for i,entry in enumerate(film):
					outfile.write('<td>')
					if i==0: # print film title without underscores
						title = entry
						s ='<a href="film_detail_trio.php?hash=%s">%s</a>'%(title,title.replace('_',' '))
					elif i==1: # print director full name from key
						s = self.actionDirectors[entry][0]
					elif i==2: # map 0/1 to B&W/COL
						if entry==0:
							s = 'B&W'
						else:
							s = 'COL'
					else: # year
						s = str(entry)
					outfile.write(s)
					outfile.write('</td>')
				outfile.write('</tr>\n')
			outfile.writelines(['</table>','</body>','</html>'])

		if write_metadata_files:
			for film in A:
				data= json.load(open(json_file_dir + os.sep + film[0] + '.json'))
				with open(json_file_dir + os.sep + film[0] + '.txt', 'w') as outfile:
					outfile.write(film[0]+'\n')
					outfile.write(film[0]+'\n')
					outfile.write('<a href="film_detail_trio.php?%s">Structure Visualization</a>\n'%film[0])
					outfile.write(self.actionDirectors[film[1]][0]+'\n')
					outfile.write(str(self.actionDB[film[0]][3])+'\n')
					if self.actionDB[film[0]][2]==0:
						outfile.write('B&W\n')
					else:
						outfile.write('COL\n')
					outfile.write(str(np.round(data['length'],2))+'s\n')

