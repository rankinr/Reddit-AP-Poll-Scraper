# This has been tested in Python 3.4.3 with BeautifulSoup 4 installed.

from bs4 import BeautifulSoup
import json, urllib.request

def loadUrl(url):
	try:
		local_url=url[url.find('//')+2:].replace('/','.')
		data=open(local_url,encoding='utf8').read()
	except:
		data=urllib.request.urlopen(url).read().decode('utf-8','ignore')
		open(local_url,'w',encoding='utf8').write(data)
	return data
ap_this_week=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll'),"html.parser")
last_week=ap_this_week.find('h2',{'class':'block-title'}).contents[0]
this_week=int(last_week[last_week.find(' ')+1:].strip())
last_week=this_week-1


ap_last_week=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/2015/'+str(last_week)),"html.parser")
teams={}
flair=BeautifulSoup(loadUrl('https://www.reddit.com/r/CFB/wiki/inlineflair'),"html.parser").getText()

games_this_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/')
games_next_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/week/'+str(this_week))
order=[]
ap_teams=[]
def apProcess(ap,pre=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)'}
	ap_table=ap.find('table')
	rows=ap_table.findAll('tr')
	for row in rows:
		rank=row.find('td',{'class':'trank'}).contents[0]
		team=row.find('div',{'class':'poll-team-name'})
		first_place_votes=team.getText()
		if first_place_votes.count('(') != 0:
			first_place_votes=first_place_votes[first_place_votes.find('(')+1:first_place_votes.find(')')]
		else: first_place_votes=''
		team=team.a.contents[0]
		if team in ap_conversions: team=ap_conversions[team]
		team=team.replace(' St.',' State')
		votes=row.find('div',{'class':'info-votes-wrap'}).getText().replace('Points','').strip()
		conference=row.find('div',{'class':'poll-conference'}).a.contents[0]
		record=row.find('div',{'class':'poll-record'}).contents[0]
		record=record[record.find(':')+1:].strip()
		if not team in teams:
			teams[team]={}
			print ('No record of '+team+'. Perhaps a bye week? Or a mismatch between ESPN and AP?')
		teams[team][pre+'rank']=rank
		teams[team][pre+'votes']=votes
		teams[team][pre+'conference']=conference
		teams[team][pre+'record']=record
		teams[team][pre+'first_place_votes']=first_place_votes
		if pre=='': order.append(team)
	ap_other=ap.find('div',{'class':'poll-footer'})
	if ap_other != None:
		ap_other=ap_other.find('p').contents[0]
		ap_other=ap_other[ap_other.find(':')+1:].strip()
		if ap_other.count(',') > ap_other.count(';'): separator=','
		else: separator=';'
		ap_other=ap_other.split(separator)
		for team_data in ap_other:
			team_data=team_data.strip()
			team=team_data[::-1]
			votes=team[:team.find(' ')][::-1].strip()
			team=team[team.find(' ')+1:][::-1].strip()
			if team.count('(') != 0:
				team=team[:team.find('(')].strip()
			if team in ap_conversions: team=ap_conversions[team]
			team=team.replace(' St.',' State')
			rank='NR'
			conference=''
			record=''
			if not team in ap_teams:
				ap_teams.append(team)
				if not team in teams: 
					print ('No record of '+team+'. Perhaps a bye week? Or a mismatch between ESPN and AP?')
					teams[team]={}
				teams[team][pre+'rank']=rank
				teams[team][pre+'votes']=votes
				teams[team][pre+'conference']=conference
				teams[team][pre+'record']=record
				if pre=='': order.append(team)


def espnProcess(games,pre=''):
	global teams
	games=games[games.find('window.espn.scoreboardData 	= ')+len('window.espn.scoreboardData 	= '):]
	games=json.loads(games[:games.find('};')+1])
	for game in games['events']:
		team=[]
		teamscores=[]
		team.append(game['competitions'][0]['competitors'][0]['team']['location'])
		teamscores.append(game['competitions'][0]['competitors'][0]['score'])
		team.append(game['competitions'][0]['competitors'][1]['team']['location'])
		teamscores.append(game['competitions'][0]['competitors'][1]['score'])
		if not team[0] in teams: teams[team[0]]={}
		if not team[1] in teams: teams[team[1]]={}
		if game['competitions'][0]['competitors'][0]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='vs. '+team[1]
			teams[team[1]][pre+'game']='@ '+team[0]
		elif game['competitions'][0]['competitors'][1]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='@ '+team[1]
			teams[team[1]][pre+'game']='vs. '+team[0]
		if int(teamscores[0]) < int(teamscores[1]):
			teams[team[0]][pre+'score']='**L** '+teamscores[0]+'-'+teamscores[1]
			teams[team[1]][pre+'score']='**W** '+teamscores[0]+'-'+teamscores[1]
		elif int(teamscores[1]) < int(teamscores[0]):
			teams[team[0]][pre+'score']='**W** '+teamscores[0]+'-'+teamscores[1]
			teams[team[1]][pre+'score']='**L** '+teamscores[0]+'-'+teamscores[1]
		if pre != '':
			if game['competitions'][0]['competitors'][0]['records'][3]['type']=='vsconf':
				teams[team[0]]['confRecord']=game['competitions'][0]['competitors'][0]['records'][3]['summary']
				teams[team[0]]['Record']=game['competitions'][0]['competitors'][0]['records'][0]['summary']
			else: print ('error')
			if game['competitions'][0]['competitors'][1]['records'][3]['type']=='vsconf':
				teams[team[1]]['confRecord']=game['competitions'][0]['competitors'][1]['records'][3]['summary']
				teams[team[1]]['Record']=game['competitions'][0]['competitors'][1]['records'][0]['summary']
			else: print('error')
espnProcess(games_this_week,'last_week_')
espnProcess(games_next_week,'next_week_')
apProcess(ap_this_week)
apProcess(ap_last_week,'last_week_')

rcfb_conversions={'Miami (FL)':'Miami','Florida Intl':'Florida International','Stephen F Austin':'Stephen F. Austin','Texas San Antonio':'UTSA','Southern Mississippi':'Southern Miss','Louisiana Lafayette':'Louisiana','Presbyterian College':'Presbyterian','Monmouth':'Monmouth (IL)','Massachusetts':'UMass','Hawaii':"Hawai'i",'Louisiana Monroe':'Louisiana-Monroe','NC State':'North Carolina State'}

for team,data in teams.items():
		if team in rcfb_conversions: teamString=rcfb_conversions[team]
		else: teamString=team
		team_flair=flair[flair.find('['+teamString+']'):]
		team_flair=team_flair[:team_flair.find(')')+1].strip()
		if len(team_flair) == 0 or team_flair[0] != '[' or team_flair[-1] != ')':
			print ('No flair record for '+teamString+'. Perhaps a mismatch between ESPN and /r/cfb?')
		data['flair']=team_flair
ork='-1'
final_text='Rk| |Team|Votes (Chg)|Record|Next Week|Chg|Last week\n:--|:--|:--|:--|:--|:--|:--|:--|:--|\n'
for team in order:
	teamData=teams[team]
	if 'rank' in teamData and 'last_week_rank' in teamData and teamData['rank'] != 'NR' and teamData['last_week_rank'] != 'NR': rankChange=str(int(teamData['last_week_rank'])-int(teamData['rank']))
	else: rankChange='N/A'
	if rankChange[0]!='-' and rankChange != 'N/A':rankChange='+'+rankChange
	if not 'last_week_game' in teamData or not 'last_week_score' in teamData:
		teamData['last_week_score']='Bye'
		teamData['last_week_game']=''
	else:
		teamLastWeek=teamData['last_week_game'].strip()[teamData['last_week_game'].strip().find(' ')+1:].strip()
		if teamLastWeek in teams and 'rank' in teams[teamLastWeek] and teams[teamLastWeek]['rank'] != 'NR':
			teamData['last_week_game']=teamData['last_week_game'][:teamData['last_week_game'].find(' ')].strip()+' ('+teams[teamLastWeek]['rank']+') '+teamData['last_week_game'][teamData['last_week_game'].find(' ')+1:].strip()
 
	last_week=teamData['last_week_score']+' '+teamData['last_week_game']
	if not 'next_week_game' in teamData: teamData['next_week_game']='Bye'
	else:
		teamNextWeek=teamData['next_week_game'][teamData['next_week_game'].find(' ')+1:].strip()
		if teamNextWeek in teams and 'rank' in teams[teamNextWeek] and teams[teamNextWeek]['rank'] != 'NR':
			teamData['next_week_game']=teamData['next_week_game'][:teamData['next_week_game'].find(' ')].strip()+' ('+teams[teamNextWeek]['rank']+') '+teamData['next_week_game'][teamData['next_week_game'].find(' ')+1:].strip()
	if 'rank' in teamData: rk=teamData['rank']
	else: rk='NR'

	if 'votes' in teamData:
		if not 'last_week_votes' in teamData: teamData['last_week_votes']='0'
		voteChange=str(int(teamData['votes'].replace(',',''))-int(teamData['last_week_votes'].replace(',','')))
		if voteChange[0] != '-': voteChange='+'+voteChange
		votes=teamData['votes']+' ('+voteChange+')'
	else: votes='N/A'

	if 'Record' in teamData and teamData['Record'].strip() != '': record=teamData['Record']+', '
	else: record=''

	if 'confRecord' in teamData: confRecord=teamData['confRecord']
	else: confRecord='N/A'

	if 'conference' in teamData and teamData['conference'].strip() != '': conference=teamData['conference']
	else: conference=' conference'

	if not 'first_place_votes' in teamData or teamData['first_place_votes'].strip() == '':
		teamData['first_place_votes']=''
	else:
		teamData['first_place_votes']=' ('+teamData['first_place_votes']+')'

	if ork != 'NR' and rk == 'NR':
		final_text+='\n\nOthers receiving votes:\n\n'+'Rk| |Team|Votes (Chg)|Record|Next Week|Chg|Last week\n:--|:--|:--|:--|:--|:--|:--|:--|:--|\n'
	ork=rk
	thisRow=[rk,teamData['flair'],team+teamData['first_place_votes'],votes,record+confRecord+' '+conference,teamData['next_week_game'],rankChange,last_week]
	final_text+='|'.join(thisRow)+'\n'
open('output.txt','w').write(final_text)
#records for teams on byes