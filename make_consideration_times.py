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
consideration_times_file = open( folder + 'ConsiderationTimes.txt', 'w' )
consideration_times_verbose_file = open( folder + 'ConsiderationTimesVerbose.txt', 'w' )
consideration_times_html_index_file = open( folder + 'consideration_times_index.html', 'w' )
missing_entries_file = open( folder + 'MissingEntries.txt', 'w' )
club_champs_date_str = '19/9/2015'
maximum_age = 21 # Any swimmer older will be excluded

club_champs_date = helpers.ParseDate_dmY( club_champs_date_str )
consideration_date = datetime.date( club_champs_date.year - 1, club_champs_date.month, club_champs_date.day )
consideration_date_str = consideration_date.strftime( '%d/%m/%Y' )
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

all_swimmer_times = []
entries = {}
    
def process_swimmer( swimmer, swims ):
  age = helpers.CalcAge( swimmer.date_of_birth, club_champs_date )
 
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
  swims_by_event = []
  for i in range( 0, num_events ):
    swims_by_event.append( [] )
  for swim in swims:
    # Append to the list according to short course event code
    swims_by_event[ swim.event.get_short_course_event_code() ].append( swim )
    
  # Sort the swims in each event by date
  for i in range( 0, num_events ):
    swims_by_event[i].sort( key=attrgetter('date') )

  swimmer_times = SwimmerTimes( swimmer, full_name )
  all_swimmer_times.append( swimmer_times )
  
  print( full_name + ', ' + str( age ) )
  for i in range( 0, num_events ):
    event = short_course_events[i]
    event_swims = swims_by_event[i]
    pb_swim = None
    interp_swim = None
    for swim in event_swims:
      if swim.date <= consideration_date:
        # This swim is earlier than the consideration date.
        # Is it a PB?
        if (pb_swim is None) or (swim.short_course_race_time < pb_swim.short_course_race_time):
          pb_swim = swim
      else:
        if pb_swim is None:
          # There was no time set before the consideration date
          break
        else:
          if swim.short_course_race_time < pb_swim.short_course_race_time:
            # This is the first swim after the consideration date that's a PB.
            interp_swim = swim
            break
    consideration_time = None
    if pb_swim is None:
      nt_time = get_nt_consideration_time( i, swimmer.is_male, age )
      if nt_time is None:
        consideration_time = ConsiderationTime( event, None, 'No PB as of ' + consideration_date_str + ', and no time specified in the NT table' )
      else:
        consideration_time = ConsiderationTime( event, nt_time, 'No PB as of ' + consideration_date_str + ', so consideration time taken from the NT table' )
    else:
      if interp_swim is not None:
        # Interpolate the PB between the pre-consideration-date PB and the first PB
        # race after the consideration date
        interpolation_val = float( (consideration_date - pb_swim.date).days ) / float( (interp_swim.date - pb_swim.date).days )
        consideration_race_time = (interp_swim.short_course_race_time * interpolation_val) + (pb_swim.short_course_race_time * (1 - interpolation_val))
        consideration_time = ConsiderationTime( event, consideration_race_time, 'Interpolated between ' + pb_swim.meet + ' ' + pb_swim.date.strftime( "%d/%m/%Y" ) + ' (' + str( RaceTime( pb_swim.short_course_race_time ) ) + ') and ' + interp_swim.meet + ' ' + interp_swim.date.strftime( "%d/%m/%Y" )+ ' (' + str( RaceTime( interp_swim.short_course_race_time ) ) + ')' )
      else:
        consideration_time = ConsiderationTime( event, pb_swim.short_course_race_time, 'From ' + pb_swim.meet + ' on ' + pb_swim.date.strftime( "%d/%m/%Y" ) )
    swimmer_times.consideration_times.append( consideration_time )

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
    consideration_times_file.write( '\n' )
  swimmer = swimmer_times.swimmer
  consideration_times_file.write( str( swimmer ) + '\n' )
  for consideration_time in swimmer_times.consideration_times:
    if consideration_time.time is not None:
      consideration_times_file.write( consideration_time.event.short_name_without_course() + '|' + str( RaceTime( consideration_time.time ) ) + '\n' )
  first = False
consideration_times_file.close()    

first = True
for swimmer_times in all_swimmer_times:
  if not first:
    consideration_times_verbose_file.write( '\n' )
  swimmer = swimmer_times.swimmer
  age = helpers.CalcAge( swimmer.date_of_birth, club_champs_date )
  consideration_times_verbose_file.write( swimmer_times.full_name + ', ' + str( age ) + '\n' )
  for consideration_time in swimmer_times.consideration_times:
    if consideration_time.time is not None:
      consideration_times_verbose_file.write( '\n' + consideration_time.event.short_name_without_course() + ': ' + str( RaceTime( consideration_time.time ) ) + '\n' )
      consideration_times_verbose_file.write( consideration_time.reason + '\n' )
  first = False
consideration_times_verbose_file.close()

_HTML_TOP = """<!DOCTYPE html>
<html>
<head>
	<title>Club Champs 2015 Consideration Times</title>
</head>
<!-- Prevent phones and tablets from pretending to be higher resolution than they actually are -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<body><h1>Winsford ASC Club Championships 2015 Scoring Consideration Times</h1>"""

_HTML_BOTTOM = """</body></html>"""

consideration_times_html_index_file.write( _HTML_TOP )
for swimmer_times in all_swimmer_times:
  swimmer = swimmer_times.swimmer
  age = helpers.CalcAge( swimmer.date_of_birth, club_champs_date )
  
  html = '<a href="'
  page_name = 'individuals/' + str( swimmer.asa_number ) + '.html'
  html += page_name
  html += '">' + swimmer.first_name + ' ' + swimmer.last_name + '</a><br/>'
  consideration_times_html_index_file.write( html + '\n' )
  
  consideration_times_html_file = open( folder + page_name, 'w' )
  consideration_times_html_file.write( _HTML_TOP )
  
  html = '<h2>' + swimmer_times.full_name + ', ' + str( age ) + '</h2>'
  consideration_times_html_file.write( html )
  for consideration_time in swimmer_times.consideration_times:
    if consideration_time.time is not None:
      html = '<p>' + consideration_time.event.short_name_without_course() + ': ' + str( RaceTime( consideration_time.time ) ) + '<br/>'
      html += consideration_time.reason + '</p>'
      consideration_times_html_file.write( html )
      
  consideration_times_html_file.write( _HTML_BOTTOM )
  consideration_times_html_file.close()
  
consideration_times_html_index_file.write( _HTML_BOTTOM )
consideration_times_html_index_file.close()

# Write out the list of entries that we haven't processed any data for
for entry, processed in entries.iteritems():
  if not processed:
    missing_entries_file.write( entry + '\n' )
missing_entries_file.close()    
