# This has been tested in Python 3.5 with BeautifulSoup 4 installed.
#	This particular file remains a work in progress. I think I will integrate it with a javascript browser-based script to get the rankings up faster, inputting them as they're announced on television.

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
ap_this_week=BeautifulSoup(loadUrl('http://www.collegefootballplayoff.com/view-rankings'),"html.parser")
last_week='9'
#if last_week.count('Week') != 0: last_week=last_week.replace('Week','').strip()
#this_week=int(last_week[last_week.find(' ')+1:].strip())
#last_week=this_week-1
this_week=11
last_week=10
conf_flairs={'ACC':'[ACC](#l/acc)','American':'[American](#l/aac)','American Athletic':'[American](#l/aac)','The American':'[American](#l/aac)','Big 12':'[Big 12](#l/big12)','Big Ten':'[Big Ten](#l/bigten)','Conference USA':'[Conference USA](#l/cusa)','Division I FBS Independents':'[FBS Independents](#l/indep)','FBS Independents':'[FBS Independents](#l/indep)','Mid-American':'[MAC](#l/mac)','Mountain West':'[Mountain West](#l/mwc)','Pac-12':'[Pac-12](#l/pac12)','SEC':'[SEC](#l/sec)','Sun Belt':'[Sun Belt](#l/sunbelt)'}
#print (last_week)
#print (this_week)
ap_last_week=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/2015/'+str(last_week)),"html.parser")
teams={}
flair=BeautifulSoup(loadUrl('https://www.reddit.com/r/CFB/wiki/inlineflair'),"html.parser").getText()

games_this_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/')
games_next_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/week/'+str(this_week))
confs={}
conferences=BeautifulSoup(loadUrl('http://espn.go.com/college-football/teams'),"html.parser")
conferences_list=conferences.findAll('div',{'class':'mod-teams-list-medium'})
for conference in conferences_list:
	conf_name=conference.find('div',{'class':'mod-header'}).getText()
	teamms=conference.findAll('a',{'class':'bi'})
	for teamm in teamms:
		confs[teamm.getText()]=conf_name
order=[]
ap_teams=[]
last_week_ranks={}
def apProcess(ap,pre=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	global last_week_ranks
	ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)','Southern Cal':'USC'}
	ap_table=ap.find('table', {'class':'tablepress-id-24'})
	print (ap_table)
	rows=ap_table.findAll('tr')
	for row in rows:
		cols=row.findAll('td')
		if len(cols) > 0:
			rank=cols[0].getText()
			team=cols[1].getText().strip()
			if team in ap_conversions: team=ap_conversions[team]
			team=team.replace(' St.',' State')
			teams[team][pre+'rank']=rank
			if pre=='last_week_': last_week_ranks[team]=rank
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
		if game['competitions'][0]['competitors'][0]['records'][3]['type']=='vsconf':
			if game['competitions'][0]['competitors'][0]['records'][3]['summary'] != '': teams[team[0]]['confRecord']=game['competitions'][0]['competitors'][0]['records'][3]['summary']
			if game['competitions'][0]['competitors'][0]['records'][0]['summary'] != '': teams[team[0]]['Record']=game['competitions'][0]['competitors'][0]['records'][0]['summary']
		else: print ('error')
		if game['competitions'][0]['competitors'][1]['records'][3]['type']=='vsconf':
			if game['competitions'][0]['competitors'][1]['records'][3]['summary'] != '': teams[team[1]]['confRecord']=game['competitions'][0]['competitors'][1]['records'][3]['summary']
			if game['competitions'][0]['competitors'][1]['records'][0]['summary'] != '': teams[team[1]]['Record']=game['competitions'][0]['competitors'][1]['records'][0]['summary']
espnProcess(games_this_week,'last_week_')
espnProcess(games_next_week,'next_week_')
apProcess(ap_this_week)
#apProcess(ap_last_week,'last_week_')
print (last_week_ranks)
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
final_text='Rk| |Team|Chg|Votes (Chg)|Last week|Record|Next Week\n:--|:--|:--|:--|:--|:--|:--|:--|:--|\n'
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
		if teamLastWeek in teams and teamLastWeek in last_week_ranks and last_week_ranks[teamLastWeek] != 'NR':
			teamData['last_week_game']=teamData['last_week_game'][:teamData['last_week_game'].find(' ')].strip()+' ('+last_week_ranks[teamLastWeek]+') '+teamData['last_week_game'][teamData['last_week_game'].find(' ')+1:].strip()
 
	last_week=teamData['last_week_score']+' '+teamData['last_week_game']
	if not 'next_week_game' in teamData: teamData['next_week_game']='Bye'
	else:
		teamNextWeek=teamData['next_week_game'][teamData['next_week_game'].find(' ')+1:].strip()
		if teamNextWeek in teams and 'rank' in teams[teamNextWeek] and teams[teamNextWeek]['rank'] != 'NR':
			teamData['next_week_game']=teamData['next_week_game'][:teamData['next_week_game'].find(' ')].strip()+' ('+teams[teamNextWeek]['rank']+') '+teamData['next_week_game'][teamData['next_week_game'].find(' ')+1:].strip()
	if 'rank' in teamData: rk=teamData['rank']
	else: rk='NR'

	votes='N/A'

	if 'Record' in teamData and teamData['Record'].strip() != '': record=teamData['Record']+', '
	else: record=''

	if 'confRecord' in teamData: confRecord=teamData['confRecord']
	else: confRecord='N/A'

	if 'conference' in teamData and teamData['conference'].strip() != '': conference=teamData['conference']
	else:
		if team in confs: conference=confs[team]
		else: conference=' conference'
	if conference in conf_flairs: conference=conf_flairs[conference]


	if ork != 'NR' and rk == 'NR':
		ork=rk
	thisRow=[rk,teamData['flair'],team,record+confRecord+' '+conference]
	final_text+='|'.join(thisRow)+'\n'
open('data.txt','w').write(json.dumps(teams))
open('output.txt','w').write(final_text)
#records for teams on byes
