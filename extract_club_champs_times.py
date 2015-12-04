# Winsford ASC Google AppEngine App
#   make_consideration_times.py
#   Reads a text file containing all swims for all swimmers in the club
#   and figures out a scoring consideration time for each swimmer for each
#   event based on their PB, or an interpolated PB from a year before
#   the date of the club champs.
#
# Copyright (C) 2014 Oliver Wright
#    oli.wright.github@gmail.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program (file LICENSE); if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.import logging

import logging
import time
import datetime
import helpers
import re

from operator import attrgetter

from swim import Swim
from swimmer import Swimmer
from race_time import RaceTime

from event import short_course_events
from nt_consideration_times import get_nt_consideration_time

folder = 'f:/SwimLists/'
swim_list_file = open( folder + 'SwimList.txt', 'r' )
entry_list_file = open( folder + 'EntryList.txt', 'r' )
missing_entries_file = open( folder + 'MissingEntriesForRaceTimes.txt', 'w' )
race_times_file = open( folder + 'RaceTimes.txt', 'w' )
club_champs_start_date_str = '12/9/2015'
club_champs_end_date_str = '19/9/2015'
maximum_age = 21 # Any swimmer older will be excluded
club_champs_meet_name = 'Winsford  Club Championships'

club_champs_start_date = helpers.ParseDate_dmY( club_champs_start_date_str )
club_champs_end_date = helpers.ParseDate_dmY( club_champs_end_date_str )
num_events = len( short_course_events )

class ConsiderationTime():
  def __init__(self, event, time, reason):
    self.event = event
    self.time = time
    self.reason = reason

class SwimmerTimes():
  def __init__(self, swimmer, full_name):
    self.swimmer = swimmer
    self.full_name = full_name
    self.consideration_times = []
    self.swim_by_event = []

all_swimmer_times = []
entries = {}
    
def process_swimmer( swimmer, swims ):
  age = helpers.CalcAge( swimmer.date_of_birth, club_champs_end_date )
 
  full_name = swimmer.full_name()
  if not full_name in entries:
    full_name = swimmer.alternate_name()
    if not full_name in entries:
      print( 'Excluding ' + full_name + ', ' + str( age ) + '. Not in entry list.' )
      return

  if age > maximum_age:
    print( 'Excluding ' + full_name + ', ' + str( age ) + '. Too old.' )
    return
  
  entries[ full_name ] = True
  
  # Categorise swims by event
  swim_by_event = []
  for i in range( 0, num_events ):
    swim_by_event.append( None )
  for swim in swims:
    # Append to the list according to short course event code
    if (swim.meet == club_champs_meet_name) and (swim.date >= club_champs_start_date) and( swim.date <= club_champs_end_date):
      # This is a club champs swim
      swim_by_event[ swim.event.get_short_course_event_code() ] = swim
    
  swimmer_times = SwimmerTimes( swimmer, full_name )
  swimmer_times.swim_by_event = swim_by_event
  all_swimmer_times.append( swimmer_times )
  
  print( full_name + ', ' + str( age ) )

# Read the entry list    
print( 'Reading entry list' )
for line in entry_list_file:
  #line = line.split('\n')[0]
  #names = line.split()
  names = re.split('[,\n ]', line)
  print( names )
  full_name = names[1] + ' ' + names[0]
  entries[ full_name ] = False
    
# Read the swim list
reading_swims = False
swimmer = None
swims = []
for line in swim_list_file:
  if reading_swims:
    if len( line ) <= 1:
      # Empty line.  So we've finished reading all the swims for a swimmer
      reading_swims = False
      process_swimmer( swimmer, swims )
      swims = []
    else:
      # Expect the line to be a Swim
      swim = Swim( line )
      swims.append( swim )
  else:
    # Expect the line to be a Swimmer
    swimmer = Swimmer( line )
    reading_swims = True

# We've read the entire file.
if reading_swims:
  # We won't have processed the final swimmer...
  reading_swims = False
  process_swimmer( swimmer, swims )
  swims = []
  
# Now we produce the output files

print( 'Writing file' )
first = True
for swimmer_times in all_swimmer_times:
  if not first:
    race_times_file.write( '\n' )
  swimmer = swimmer_times.swimmer
  race_times_file.write( str( swimmer ) + '\n' )
  for swim in swimmer_times.swim_by_event:
    if swim is not None:
      race_times_file.write( swim.event.short_name_without_course() + '|' + str( RaceTime( swim.race_time ) ) + '\n' )
  first = False
race_times_file.close()    

# Write out the list of entries that we haven't processed any data for
for entry, processed in entries.iteritems():
  if not processed:
    missing_entries_file.write( entry + '\n' )
missing_entries_file.close()    
