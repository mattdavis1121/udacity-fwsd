#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""DELETE FROM matches;""")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""DELETE FROM players;""")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""SELECT COUNT(*) FROM players;""")
    players = cur.fetchall()[0][0]
    conn.close()
    return players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    # Prep insert statment
    sql = """INSERT INTO players (name) VALUES (%s)"""
    args = (name,)

    # Insert
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    conn.close()



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
    sql = """SELECT  p.player_id,
            p.name,
            (SELECT COUNT(*)
            FROM matches
            WHERE winner_id = p.player_id) as wins,
            (SELECT COUNT(*)
            FROM matches
            WHERE winner_id = p.player_id
            OR loser_id = p.player_id) as matches
            FROM players p
            ORDER BY wins;"""
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    standings = cur.fetchall()
    conn.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    sql = """INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s);"""
    args = (winner, loser)
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    conn.close()


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
    standings = playerStandings()
    pairings = []
    pairing = []
    for i, player in enumerate(standings):

        # Store in named variables for easier reading
        player_id = player[0]
        player_name = player[1]

        # Store player's data
        pairing += [player_id, player_name]

        if i % 2 == 1:                      # Players 1, 3, 5, 7, etc
            pairing_tuple = tuple(pairing)  # Convert to tuple to meet spec
            pairings.append(pairing_tuple)  # Store in final list
            pairing = []                    # Reset pairing to empty list for
                                            # next iteration

    return pairings
