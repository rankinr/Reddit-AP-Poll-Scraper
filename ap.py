# This has been tested in Python 3.5 with BeautifulSoup 4 installed.

from bs4 import BeautifulSoup
import json, urllib.request, time

def loadUrl(url):
	try:
		local_url=url[url.find('//')+2:].replace('/','.')
		data=open(local_url,encoding='utf8').read()
	except:
		data=urllib.request.urlopen(url).read().decode('utf-8','ignore')
		open(local_url,'w',encoding='utf8').write(data)
	return data
ap_this_week=BeautifulSoup(urllib.request.urlopen('http://collegefootball.ap.org/poll/?t='+str(int(time.time()))).read().decode('utf-8','ignore'),"html.parser")
last_week=ap_this_week.find('h2',{'class':'block-title'}).contents[0]
if last_week.count('Week') != 0: last_week=last_week.replace('Week','').strip()
this_week=int(last_week[last_week.find(' ')+1:].strip())
last_week=this_week-1
conf_flairs={'ACC':'[ACC](#l/acc)','American':'[American](#l/aac)','American Athletic':'[American](#l/aac)','The American':'[American](#l/aac)','Big 12':'[Big 12](#l/big12)','Big Ten':'[Big Ten](#l/bigten)','Conference USA':'[Conference USA](#l/cusa)','Division I FBS Independents':'[FBS Independents](#l/indep)','FBS Independents':'[FBS Independents](#l/indep)','Mid-American':'[MAC](#l/mac)','Mountain West':'[Mountain West](#l/mwc)','Pac-12':'[Pac-12](#l/pac12)','SEC':'[SEC](#l/sec)','Sun Belt':'[Sun Belt](#l/sunbelt)'}
#print (last_week)
#print (this_week)
ap_last_week=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/2015/'+str(last_week)),"html.parser")
teams={}
flair=BeautifulSoup(loadUrl('https://www.reddit.com/r/CFB/wiki/inlineflair'),"html.parser").getText()
games_this_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/')
print('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/week/'+str(this_week+2))
games_next_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/week/'+str(this_week))
confs={}
conferences=BeautifulSoup(loadUrl('http://espn.go.com/college-football/teams'),"html.parser")
conferences_list=conferences.findAll('div',{'class':'mod-teams-list-medium'})
for conference in conferences_list:
	conf_name=conference.find('div',{'class':'mod-header'}).getText()
	teamms=conference.findAll('a',{'class':'bi'})
	for teamm in teamms:
		confs[teamm.getText().replace(';','').strip()]=conf_name
order=[]
ap_teams=[]
last_week_ranks={}
old_ranks={}
def apProcess(ap,pre=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	global last_week_ranks
	ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)','Southern Cal':'USC','Southern California':'USC'}
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
		if pre=='last_week_': last_week_ranks[team]=rank
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
			team=team_data[::-1].replace(';','')
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
		if team[0].count('Texas A&M') != 0: team[0]='Texas A&M'
		if team[1].count('Texas A&M') != 0: team[1]='Texas A&M'
		if not team[0] in teams: teams[team[0]]={}
		if not team[1] in teams: teams[team[1]]={}
		if game['competitions'][0]['competitors'][0]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='vs. '+team[1]
			teams[team[1]][pre+'game']='vs. '+team[0] # change to '@' after bowl season
		elif game['competitions'][0]['competitors'][1]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='vs. '+team[1] #change to '@' after bowl season
			teams[team[1]][pre+'game']='vs. '+team[0]
		if int(teamscores[0]) < int(teamscores[1]):
			teams[team[0]][pre+'score']='**L** '+teamscores[0]+'-'+teamscores[1]
			teams[team[1]][pre+'score']='**W** '+teamscores[1]+'-'+teamscores[0]
		elif int(teamscores[1]) < int(teamscores[0]):
			teams[team[0]][pre+'score']='**W** '+teamscores[0]+'-'+teamscores[1]
			teams[team[1]][pre+'score']='**L** '+teamscores[1]+'-'+teamscores[0]
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
apProcess(ap_last_week,'last_week_')
weeks_ct=this_week
while weeks_ct > 0:
	apProcess(BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/2015/'+str(weeks_ct)),"html.parser"),'week_'+str(weeks_ct)+'_')
	weeks_ct=weeks_ct-1
#print (last_week_ranks)
rcfb_conversions={'Louisiana-Monroe':'ULM','Louisiana Monroe':'ULM','Florida Atlantic':'FAU','South Florida':'USF','Southern California':'USC','Miami (FL)':'Miami','Florida Intl':'Florida International','Stephen F Austin':'Stephen F. Austin','Texas San Antonio':'UTSA','Southern Mississippi':'Southern Miss','Louisiana Lafayette':'Louisiana','Presbyterian College':'Presbyterian','Monmouth':'Monmouth (IL)','Massachusetts':'UMass','Hawaii':"Hawai'i",'NC State':'North Carolina State'}
for team,data in teams.items():
		if team in rcfb_conversions:
			teamString=rcfb_conversions[team]
		else: teamString=team
		team_flair=flair[flair.find('['+teamString+']'):]
		team_flair=team_flair[:team_flair.find(')')+1].strip()
		if len(team_flair) == 0 or team_flair[0] != '[' or team_flair[-1] != ')':
			print ('No flair record for '+teamString+'. Perhaps a mismatch between ESPN and /r/cfb?'+teamString)
		data['flair']=team_flair
ork='-1'
for team in teams:
	if team in confs: 
		if not 'conference' in teams[team] or teams[team]['conference'].strip() == '': teams[team]['conference']=confs[team]
		if teams[team]['conference'] in conf_flairs: 
			teams[team]['confFlair']=conf_flairs[teams[team]['conference']]
#print (teams['Texas A&M'])

final_text='Rk| |Team|Chg|Votes (Chg)|Last week|Record|Next Week|Hi/Lo (yr)\n:--|:--|:--|:--|:--|:--|:--|:--|:--:|\n'
for team in order:
	teamData=teams[team]
	hi_rank=26
	lo_rank=0
	lo_week=''
	weeks_ct=this_week
	while weeks_ct > 0:
		#if weeks_ct==1 and team=='Baylor': print(teamData)
		if 'week_'+str(weeks_ct)+'_rank' in teamData and teamData['week_'+str(weeks_ct)+'_rank'] != '' and teamData['week_'+str(weeks_ct)+'_rank'] != 'NR' and teamData['week_'+str(weeks_ct)+'_rank'] != 'NA':
			if int(hi_rank) > int(teamData['week_'+str(weeks_ct)+'_rank']): hi_rank=teamData['week_'+str(weeks_ct)+'_rank']
			if lo_rank != 'NR' and (teamData['week_'+str(weeks_ct)+'_rank']=='NR' or int(lo_rank) < int(teamData['week_'+str(weeks_ct)+'_rank'])): lo_rank=teamData['week_'+str(weeks_ct)+'_rank']
		else: 
			lo_rank='NR'
			lo_week=str(weeks_ct)
		weeks_ct=weeks_ct-1
	if hi_rank==26: hi_rank='NR'
	if lo_rank==0:lo_rank='NR'
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

	if 'votes' in teamData:
		if not 'last_week_votes' in teamData:
			teamData['last_week_votes']='0'
		voteChange=str(int(teamData['votes'].replace(',',''))-int(teamData['last_week_votes'].replace(',','')))
		if voteChange[0] != '-': voteChange='+'+voteChange
		votes=teamData['votes']+' ('+voteChange+')'
	else: votes='N/A'

	if 'Record' in teamData and teamData['Record'].strip() != '': record=teamData['Record']+', '
	else: record=''

	if 'confRecord' in teamData: confRecord=teamData['confRecord']
	else: confRecord='N/A'

	if 'conference' in teamData and teamData['conference'].strip() != '': conference=teamData['conference']
	else:
		if team in confs: conference=confs[team]
		else: conference=' conference'
	if conference in conf_flairs: conference=conf_flairs[conference]
	if not 'first_place_votes' in teamData or teamData['first_place_votes'].strip() == '':
		teamData['first_place_votes']=''
	else:
		teamData['first_place_votes']=' ('+teamData['first_place_votes']+')'

	if ork != 'NR' and rk == 'NR':
		final_text+='\n\nOthers receiving votes:\n\n'+'Rk| |Team|Chg|Votes (Chg)|Last week|Record|Next Week|Hi/Lo (yr)\n:--|:--|:--|:--|:--|:--|:--|:--|:--:|\n'
	ork=rk
	thisRow=[rk,teamData['flair'],team+teamData['first_place_votes'],rankChange,votes,last_week,record+confRecord+' '+conference,teamData['next_week_game'],str(hi_rank)+'/'+str(lo_rank)]
	final_text+='|'.join(thisRow)+'\n'
open('output.txt','w').write(final_text)
#records for teams on byes
