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
 
def rcfbProcess(ap,pre=''):
	global teams
	ap_table=ap.find('table')
	rows=ap_table.findAll('tr')
	for row in rows:
		col=row.findAll('td')
		team=col[1].findAll('a')[1].getText()
		rcfb_conv={'USC':'Southern California'}
		if team in rcfb_conv: team=rcfb_conv[team]
		if team in teams: teams[team][pre+'rcfbrank']=col[0].getText()
		else: 
			teams[team]={}
			teams[team][pre+'rcfbrank']=col[0].getText()
			print ('No match for rcfb rank for '+team+'-maybe mismatch with ESPN?')
		if pre=='': order.append(team)
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
#espnProcess(games_this_week,'last_week_')
#espnProcess(games_next_week,'next_week_')
apProcess(ap_this_week)
rcfbProcess(BeautifulSoup(loadUrl('http://rcfbpoll.com/current-rankings.php'),"html.parser"))
rcfbProcess(BeautifulSoup(loadUrl('http://rcfbpoll.com/old-rankings.php'),"html.parser"),'last_week') #must get this manually before new ones come out
coachesProcess(BeautifulSoup(loadUrl('http://espn.go.com/college-football/rankings'),"html.parser"))
#cfpProcess(ap_last_week,'last_week_')
rcfb_conversions={'South Florida':'USF','Miami (FL)':'Miami','Florida Intl':'Florida International','Stephen F Austin':'Stephen F. Austin','Texas San Antonio':'UTSA','Southern Mississippi':'Southern Miss','Louisiana Lafayette':'Louisiana','Presbyterian College':'Presbyterian','Monmouth':'Monmouth (IL)','Massachusetts':'UMass','Hawaii':"Hawai'i",'Louisiana Monroe':'Louisiana-Monroe','NC State':'North Carolina State'}
print ('a')
for team,data in teams.items():
		if team in rcfb_conversions: teamString=rcfb_conversions[team]
		else: teamString=team
		team_flair=flair[flair.find('['+teamString+']'):]
		team_flair=team_flair[:team_flair.find(')')+1].strip()
		if len(team_flair) == 0 or team_flair[0] != '[' or team_flair[-1] != ')':
			print ('No flair record for '+teamString+'. Perhaps a mismatch between ESPN and /r/cfb?')
		data['flair']=team_flair
ork='-1'
final_text='Rk| |Chg|AP (Chg||Coaches (Chg)|\n:-:|:--|:--|:--|:--|\n'
print ('b')
for team in order:
	teamData=teams[team]
	if not 'rcfbrank' in teamData: teamData['rcfbrank']='NR'
	if not 'rank' in teamData: teamData['rank']='NR'
	if not 'coaches_rank' in teamData: teamData['coaches_rank']='NR'
	if not 'last_week_rcfbrank' in teamData: teamData['last_week_rcfbrank']='NR'
	rankChange='NA'
	coaches_rankChange='NA'
	ap_rankChange='NA'
	if 'rcfbrank' in teamData and 'last_week_rcfbrank' in teamData and teamData['rcfbrank'] != 'NR' and teamData['last_week_rcfbrank'] != 'NR': rankChange=str(int(teamData['last_week_rank'])-int(teamData['rank']))
	if 'rank' in teamData and 'rcfbrank' in teamData and teamData['rank'] != 'NR' and teamData['rcfbrank'] != 'NR': ap_rankChange=str(int(teamData['rank'])-int(teamData['rcfbrank']))
	if 'coaches_rank' in teamData and 'rcfbrank' in teamData and teamData['coaches_rank'] != 'NR' and teamData['rcfbrank'] != 'NR' and teamData['coaches_rank'].strip() != '': 
		coaches_rankChange=str(int(teamData['coaches_rank'])-int(teamData['rcfbrank']))
	if coaches_rankChange != 'NA' and int(coaches_rankChange) > 0: coaches_rankChange='+'+coaches_rankChange
	elif coaches_rankChange != 'NA' and  int(coaches_rankChange) == 0: coaches_rankChange='-'
	if rankChange != 'NA' and int(rankChange) > 0: rankChange='+'+rankChange
	elif rankChange != 'NA' and  int(rankChange) == 0: rankChange='-'
	if ap_rankChange != 'NA' and int(ap_rankChange) > 0: ap_rankChange='+'+ap_rankChange
	elif ap_rankChange != 'NA' and  int(ap_rankChange) == 0: ap_rankChange='-'
	
	
	thisRow=[teamData['rcfbrank'],teamData['flair'],rankChange,teamData['rank']+' ('+ap_rankChange+')',teamData['coaches_rank']+' ('+coaches_rankChange+')']
	final_text+='|'.join(thisRow)+'\n'
open('output.txt','w').write(final_text)
#records for teams on byes
