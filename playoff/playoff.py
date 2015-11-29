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
ap_this_week=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/'),"html.parser")
cfp_this_week=BeautifulSoup(urllib.request.urlopen('http://www.collegefootballplayoff.com/view-rankings/?t='+str(int(time.time()))).read().decode('utf-8','ignore'),"html.parser")
last_week='9'
#if last_week.count('Week') != 0: last_week=last_week.replace('Week','').strip()
#this_week=int(last_week[last_week.find(' ')+1:].strip())
#last_week=this_week-1
this_week=13
last_week=12

conf_flairs={'ACC':'[ACC](#l/acc)','American':'[American](#l/aac)','American Athletic':'[American](#l/aac)','The American':'[American](#l/aac)','Big 12':'[Big 12](#l/big12)','Big Ten':'[Big Ten](#l/bigten)','Conference USA':'[Conference USA](#l/cusa)','Division I FBS Independents':'[FBS Independents](#l/indep)','FBS Independents':'[FBS Independents](#l/indep)','Mid-American':'[MAC](#l/mac)','Mountain West':'[Mountain West](#l/mwc)','Pac-12':'[Pac-12](#l/pac12)','SEC':'[SEC](#l/sec)','Sun Belt':'[Sun Belt](#l/sunbelt)'}
#print (last_week)
#print (this_week)
teams={}
flair=BeautifulSoup(loadUrl('https://www.reddit.com/r/CFB/wiki/inlineflair'),"html.parser").getText()
games_this_week=loadUrl('http://espn.go.com/college-football/scoreboard/_/group/80/year/2015/seasontype/2/week/'+str(last_week))
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
def cfpProcess(ap,pre='',week=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	global last_week_ranks
	ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)','Southern Cal':'USC'}
	ap_table=ap.find('div', {'class':'rankings-table-week-'+str(week)+'-rankings'}).find('table')
	#print (ap_table)
	rows=ap_table.findAll('tr')
	for row in rows:
		cols=row.findAll('td')
		if len(cols) > 0:
			rank=cols[0].getText()
			team=cols[1].getText().strip()
			if team in ap_conversions: team=ap_conversions[team]
			team=team.replace(' St.',' State')
			if not team in teams: teams[team]={}
			teams[team][pre+'rank']=rank
			if pre=='last_week_': last_week_ranks[team]=rank
			if pre=='cfp_': order.append(team)
def rcfbProcess(ap):
	global teams
	ap_table=ap.find('table')
	rows=ap_table.findAll('tr')
	for row in rows:
		col=row.findAll('td')
		team=col[1].findAll('a')[1].getText()
		if team in teams: teams[team]['rcfb_rank']=col[0].getText()
		else: print ('No match for rcfb rank for '+team+'-maybe mismatch with ESPN?')
def apProcess(ap,pre=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	global last_week_ranks
	ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)','Southern Cal':'USC'}
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
		#if pre=='last_week_': last_week_ranks[team]=rank
		teams[team][pre+'votes']=votes
		teams[team][pre+'conference']=conference
		teams[team][pre+'record']=record
		teams[team][pre+'first_place_votes']=first_place_votes
		#if pre=='': order.append(team)
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
			if team == 'Texas A&M': conference='SEC'
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
			#if pre=='': order.append(team)
def coachesProcess(ap):
	global teams
	ap_table=ap.findAll('table',{'class':'rankings'})[1]
	rows=ap_table.findAll('tr')
	for row in rows:
		cols=row.findAll('td')
		if len(cols) != 0:
			try:
				team=cols[1].find('span',{'class':'team-names'}).getText()
				if team in teams: teams[team]['coaches_rank']=cols[0].getText()
				else: print ('No match for coaches rank for '+team+'-maybe mismatch with ESPN?')
			except:
				zzzzz=1
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
		if pre=='next_week_':
			teams[team[0]][pre+'game_raw']=team[1].strip()
			teams[team[1]][pre+'game_raw']=team[0].strip()
		if game['competitions'][0]['competitors'][0]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='vs. '+team[1]
			teams[team[1]][pre+'game']='@ '+team[0]
			if pre == 'next_week_':
				teams[team[0]][pre+'game_raw_sym']='vs. '
				teams[team[1]][pre+'game_raw_sym']='@ '
		elif game['competitions'][0]['competitors'][1]['homeAway'] == 'home':
			teams[team[0]][pre+'game']='@ '+team[1]
			teams[team[1]][pre+'game']='vs. '+team[0]
			if pre == 'next_week_':
				teams[team[0]][pre+'game_raw_sym']='@ '
				teams[team[1]][pre+'game_raw_sym']='vs. '
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
		teams[team[0]]['rcfb_rank']='NR'
		teams[team[1]]['rcfb_rank']='NR'
		teams[team[0]]['coaches_rank']='NR'
		teams[team[1]]['coaches_rank']='NR'
espnProcess(games_this_week,'last_week_')
espnProcess(games_next_week,'next_week_')
apProcess(ap_this_week)
cfpProcess(cfp_this_week,'last_week_',last_week-1)
cfpProcess(cfp_this_week,'cfp_',last_week-1)
rcfbProcess(BeautifulSoup(loadUrl('http://rcfbpoll.com/current-rankings.php'),"html.parser"))
coachesProcess(BeautifulSoup(loadUrl('http://espn.go.com/college-football/rankings'),"html.parser"))
#cfpProcess(ap_last_week,'last_week_')
rcfb_conversions={'South Florida':'USF','Miami (FL)':'Miami','Florida Intl':'Florida International','Stephen F Austin':'Stephen F. Austin','Texas San Antonio':'UTSA','Southern Mississippi':'Southern Miss','Louisiana Lafayette':'Louisiana','Presbyterian College':'Presbyterian','Monmouth':'Monmouth (IL)','Massachusetts':'UMass','Hawaii':"Hawai'i",'Louisiana Monroe':'Louisiana-Monroe','NC State':'North Carolina State'}
for team,data in teams.items():
		if team in rcfb_conversions: teamString=rcfb_conversions[team]
		else: teamString=team
		team_flair=flair[flair.find('['+teamString+']'):]
		team_flair=team_flair[:team_flair.find(')')+1].strip()
		if len(team_flair) == 0 or team_flair[0] != '[' or team_flair[-1] != ')':
			print ('No flair record for '+teamString+'. Perhaps a mismatch between ESPN and /r/cfb?')
		data['flair']=team_flair
ork='-1'
final_text='Rk| |Team|Chg|Last week|Record|Next Week|AP (Chg)|\n:-:|:--|:--|:-:|:--|:--|:--|:-:|\n'
for team in teams:
	if team in confs: 
		if not 'conference' in teams[team] or teams[team]['conference'] == '': teams[team]['conference']=confs[team]
		if teams[team]['conference'] in conf_flairs: 
			teams[team]['confFlair']=conf_flairs[teams[team]['conference']]
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
		if teamNextWeek in teams and 'cfp_rank' in teams[teamNextWeek] and teams[teamNextWeek]['cfp_rank'] != 'NR':
			teamData['next_week_game']=teamData['next_week_game'][:teamData['next_week_game'].find(' ')].strip()+' ('+teams[teamNextWeek]['cfp_rank']+') '+teamData['next_week_game'][teamData['next_week_game'].find(' ')+1:].strip()
	if 'cfp_rank' in teamData: rk=teamData['cfp_rank']
	else: rk='NR'

	votes='N/A'

	if 'Record' in teamData and teamData['Record'].strip() != '': record=teamData['Record']+', '
	else: record=''

	if 'confRecord' in teamData: confRecord=teamData['confRecord']
	else: confRecord='N/A'

	if 'conference' in teamData and teamData['conference'].strip() != '': conference=teamData['conference']
	else:
		if team in confs: 
			conference=confs[team]
			if teams[team]['conference'] == '' or not 'conference' in teams[team]: teams[team]['conference']=confs[team]
		else: 
			conference=' conference'
			teams[team]['conference']='conference'
	if conference in conf_flairs: 
		teams[team]['confFlair']=conf_flairs[conference]
		conference=conf_flairs[conference]

	if ork != 'NR' and rk == 'NR':
		ork=rk
	if 'rank' in teamData and 'cfp_rank' in teamData and teamData['rank'] != 'NR' and teamData['rank'] != 'NA' and teamData['rank'].strip() != '' and teamData['cfp_rank'] != 'NR':
		ap_rank_diff=str(int(teamData['rank'])-int(teamData['cfp_rank']))
	else: ap_rank_diff='NA'
	# last_week_ = cfp last week; cfp_ = cfp this week; '' = ap this week
	if 'last_week_rank' in teamData and 'cfp_rank' in teamData and teamData['last_week_rank'] != 'NR' and teamData['last_week_rank'] != 'NA' and teamData['last_week_rank'].strip() != '' and teamData['cfp_rank'] != 'NR':
		lw_rank_diff=str(int(teamData['last_week_rank'])-int(teamData['cfp_rank']))
	else: lw_rank_diff='NA'
	if lw_rank_diff=='0': lw_rank_diff='-'
	if lw_rank_diff.count('-') == 0 and lw_rank_diff != 'NA': lw_rank_diff='+'+lw_rank_diff
	if ap_rank_diff=='0': ap_rank_diff='-'
	if ap_rank_diff.count('-') == 0 and ap_rank_diff != 'NA': ap_rank_diff='+'+ap_rank_diff
	print (team)
	if not 'rank' in teamData: teamData['rank']='NR'
	thisRow=[rk,teamData['flair'],team,lw_rank_diff,last_week,record+confRecord+' '+conference,teamData['next_week_game'],teamData['rank']+' ('+ap_rank_diff+')']
	final_text+='|'.join(thisRow)+'\n'
ip=open('input.html').read()
ip=ip[:ip.find('teams=jQuery.parseJSON(\'')+len('teams=jQuery.parseJSON(\'')]+json.dumps(teams).replace("'","\\'")+ip[ip.find("')"):]
open('input.html','w').write(ip)
open('data.txt','w').write(json.dumps(teams))
open('output.txt','w').write(final_text)
#records for teams on byes
