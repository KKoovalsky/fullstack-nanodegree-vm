#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import numpy
import math

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
	"""Remove all the match records from the database."""
	DB = connect()
	c = DB.cursor()
	c.execute("delete from matches;")
	DB.commit()
	DB.close()


def deletePlayers():
	"""Remove all the player records from the database."""
	DB = connect()
	c = DB.cursor()
	c.execute("delete from players;")
	DB.commit()
	DB.close()


def countPlayers():
	"""Returns the number of players currently registered."""
	DB = connect()
	c = DB.cursor()
	c.execute("select coalesce((select count(id) as num from players),0);")
	result = c.fetchone()
	DB.commit()
	DB.close()
	return result[0]


def registerPlayer(name):
	"""Adds a player to the tournament database.
  
	The database assigns a unique serial id number for the player.  (This
	should be handled by your SQL database schema, not in your Python code.)
  
	Args:
	name: the player's full name (need not be unique).
	"""
	DB = connect()
	c = DB.cursor()
	c.execute("insert into players (name) values (%s)", (name,))
	DB.commit()
	DB.close()


def playerStandings():
	"""Returns a list of the players and their win records, sorted by wins.

	The first entry in the list should be the player in first place, or a player
	tied for first place if there is currently a tie.

	Returns:
	A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
	"""
	DB = connect()
	c = DB.cursor()
	c.execute("select subq1.id, players.name, wins, matches from \
	(select id, count(winner) as wins from players left join matches on id = winner group by id) as subq1, \
	(select id, (count(left_id) + count(right_id))/2 as matches from players left join matches on id = left_id or id = right_id group by id) as subq2, \
	players where subq1.id = subq2.id and subq1.id = players.id order by wins desc;")
	results = c.fetchall()
	DB.close()
	return results;

def reportMatch(winner, loser):
	"""Records the outcome of a single match between two players.
	
	Args:
	winner:  the id number of the player who won
	loser:  the id number of the player who lost
	"""
	
	DB = connect()
	c = DB.cursor()
	if winner > loser:
		c.execute("insert into matches (left_id, right_id, winner) values(%s, %s, %s)", (loser, winner, winner,))
	else:
		c.execute("insert into matches (left_id, right_id, winner) values(%s, %s, %s)", (winner, loser, winner,))
	DB.commit()
	DB.close()
 
 
def swissPairings():
	"""Returns a list of pairs of players for the next round of a match.
  
	Assuming that there are an even number of players registered, each player
	appears exactly once in the pairings.  Each player is paired with another
	player with an equal or nearly-equal win record, that is, a player adjacent
	to him or her in the standings.
  
	Returns:
		A list of tuples, each of which contains (id1, name1, id2, name2)
		id1: the first player's unique id
		name1: the first player's name
		id2: the second player's unique id
		name2: the second player's name
	"""
	i = 0
	j = 1
	k = 0
	left = []
	right = []
	matches_nr = []
	DB = connect()
	c = DB.cursor()
	pStand = playerStandings()
	dim = numpy.shape(pStand)
	if dim[0] % 2 == 1:
		try:
			c.execute("insert into players (id, name) values (0, 'bye')")
			c.commit()
		except RuntimeError:
			pass
	matches_nr = int(math.ceil(dim[0]/2))
	pMatches = [(0, "", 0, "")] * matches_nr
	while k < matches_nr:
		if pStand[0][0] > pStand[j][0]:
			left = pStand[j]
			right = pStand[0]
		else:
			left = pStand[0]
			right = pStand[j]
		c.execute("select * from matches where left_id = %s and right_id = %s", (left[0], right[0],))
		if c.rowcount == 0:
			pMatches[i] = [left[0], left[1], right[0],right[1]]
			numpy.delete(pStand, 0, 0)
			numpy.delete(pStand, j - 1, 0)
			i = i + 1
			j = 1
		else:
			j = j + 1
		k = k + 1
	DB.close()
	return pMatches
	


