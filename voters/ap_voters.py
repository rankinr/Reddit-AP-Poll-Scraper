# This has been tested in Python 3.5 with BeautifulSoup 4 installed.

from bs4 import BeautifulSoup
import json, urllib.request
from collections import Counter
import statistics
import copy,operator
ap_conversions={'Mississippi':'Ole Miss', 'W. Kentucky':'Western Kentucky','Brigham Young':'BYU','Miami':'Miami (FL)','Southern Cal':'USC'}
def loadUrl(url):
	try:
		local_url=url[url.find('//')+2:].replace('/','.')
		data=open(local_url,encoding='utf8').read()
	except:
		data=urllib.request.urlopen(url).read().decode('utf-8','ignore')
		open(local_url,'w',encoding='utf8').write(data)
	return data
ap_teams=[]
teams_ranks={}
def apProcess(ap,pre=''):
	global teams
	global order
	global ap_teams # to prevent from overwriting rankings on the second round if AP hasn't updated the others receiving votes div
	global teams_ranks
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
		teams[team][pre+'votes']=votes
		teams[team][pre+'conference']=conference
		teams[team][pre+'record']=record
		teams[team][pre+'first_place_votes']=first_place_votes
		teams_ranks[team]=int(rank)
		if pre=='': order.append(team)
	ap_other=ap.find('div',{'class':'poll-footer'})
	other_rk=25
	if ap_other != None:
		other_rk+=1
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
			teams_ranks[team]=int(other_rk)
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
	
ap_main=BeautifulSoup(loadUrl('http://collegefootball.ap.org/poll/'),"html.parser")
teams={}
order=[]
apProcess(ap_main)
votes={}
votes_with_nr={}
votes_with_26={}
votes_with_voters={}
voter_urls={}
voters=ap_main.findAll('span',{'class':'poll-voter'})
total_ranks=0
voter_diff={}
for voter in voters:
	#print ('http://collegefootball.ap.org'+str(voter.find('a')['href']))
	v_url=BeautifulSoup(loadUrl('http://collegefootball.ap.org'+str(voter.find('a')['href'])),"html.parser")
	rank=1
	voter_name=str(v_url)
	voter_name=voter_name[voter_name.find('As Voted by'):]
	voter_name=voter_name[voter_name.find('>')+1:]
	voter_name=str(voter_name[:voter_name.find('<')])
	if not voter_name in voter_diff: voter_diff[voter_name]=0
	voter_urls[voter_name]='http://collegefootball.ap.org'+str(voter.find('a')['href'])
	votes_list_check=list(range(1,26))
	for vote in v_url.findAll('td',{'class':'tname'}):
		team=vote.a.getText().strip()
		if team in ap_conversions: team=ap_conversions[team]
		if not team in votes:
			votes[team]=[]
			votes_with_nr[team]=[]
			votes_with_26[team]=[]
		voter_diff[voter_name]+=abs(teams_ranks[team]-int(rank))
		votes[team].append(int(rank))
		total_ranks+=int(rank)
		votes_list_check.pop(votes_list_check.index(int(rank)))
		votes_with_nr[team].append(int(rank))
		votes_with_26[team].append(int(rank))
		if not team in votes_with_voters: votes_with_voters[team]={}
		if not str(rank) in votes_with_voters[team]: votes_with_voters[team][str(rank)]=[]
		votes_with_voters[team][str(rank)].append(voter_name)
		rank+=1
	if len(votes_list_check) != 0:
		print (votes_list_check)
		print (voter)
final_text='Team|Min|Max|Mode|Mean|Median\n:--|:--|:--|:--|:--|:--|\n'
for a,b in votes_with_nr.items():
	while len(b) < len(voters): b.append('NR')
for a,b in votes_with_26.items():
	while len(b) < len(voters): b.append(26)
for team in order:
	a=team
	if a in votes:
		b=votes[a]
		maxx=str(max(votes_with_26[a]))
		if maxx in votes_with_voters[a] and len(votes_with_voters[a][maxx]) < 4:
			c=0
			mold=maxx
			maxx+=' ('
			for voter in votes_with_voters[a][mold]:
				if c!=0: maxx+=', '
				c=1
				#maxx+='['+voter+']('+voter_urls[voter]+')' # makes the post too long :(
				maxx+=voter
			maxx+=')'
		if maxx=='26': maxx='NR'
		minn=str(min(b))
		if minn in votes_with_voters[a] and len(votes_with_voters[a][minn]) < 4:
			c=0
			mold=minn
			minn+=' ('
			for voter in votes_with_voters[a][mold]:
				if c!=0: minn+=', '
				c=1
				#minn+='['+voter+']('+voter_urls[voter]+')' # Makes the post too long! :(
				minn+=voter
			minn+=')'
		data=Counter(votes_with_nr[a])
		mode=data.most_common(1)[0][0]
		mode=str(mode)
		mean=str(round(float(sum(b)/len(b)),1))
		median=str(statistics.median(votes_with_26[a]))
		if median == '26': median='NR'
		final_text+=a+'|'+maxx+'|'+minn+'|'+mode+'|'+mean+'|'+median+'\n'
print (total_ranks)
voter_c = reversed(sorted(voter_diff.items(), key=operator.itemgetter(1)))
ct = 0
final_text+='\n\nMost controversial ballots:\n\nVoter|Average Difference from Poll\n:--|:--|\n'
print (voter_c)
for c in voter_c:
	a=c[0]
	b=c[1]
	a='['+a+']('+voter_urls[a]+')'
	ct+=1
	if ct <= 10: final_text+=a+'|'+str(round(b/25,1))+'\n'
open('output.txt','w').write(final_text)
