# Winsford ASC Google AppEngine App
#   find_qualifiers.py
#   Reads a text file containing all swims for all swimmers in the club
#   and figures out who qualifies for the events listed in qualifying_times.py
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
import math

from operator import attrgetter

from swim import Swim
from swimmer import Swimmer
from race_time import RaceTime

from event import short_course_events
from qualifying_times import get_qualifying_time

folder = 'f:/SwimLists/'
swim_list_file = open( folder + 'SwimList.txt', 'r' )
qt_file = open( folder + 'Qualifiers.txt', 'w' )
qt_html_file = open( folder + 'Qualifiers.html', 'w' )
age_on_date_str = '31/12/2016'
earliest_pb_date_str = '8/6/2015'
maximum_age = 21 # Any swimmer older will be excluded

level_4_meets = {
"Winsford  Club Championships"
}
# Swimmers that are in our database that no longer swim for Winsford
excluded_swimmers = {
"Alisha Hawkins",
"Ashley Hogg"
}

age_on_date = helpers.ParseDate_dmY( age_on_date_str )
earliest_pb_date = helpers.ParseDate_dmY( earliest_pb_date_str )
num_events = len( short_course_events )

class ConsiderationTime():
  def __init__(self, event, time, reason, is_nt):
    self.event = event
    self.time = time
    self.reason = reason
    self.is_nt = is_nt

class SwimmerTimes():
  def __init__(self, swimmer, full_name):
    self.swimmer = swimmer
    self.full_name = full_name
    self.consideration_times = []

all_swimmer_times = []
entries = {}
    
def process_swimmer( swimmer, swims ):
  age = helpers.CalcAge( swimmer.date_of_birth, age_on_date )
 
  full_name = swimmer.full_name()
  if full_name in excluded_swimmers:
    return;

  if age > maximum_age:
    return
  
  # Find PB in the qualifying window, and qualifying PB
  pb_by_event = []
  qual_pb_by_event = []
  for i in range( 0, num_events ):
    pb_by_event.append( None )
    qual_pb_by_event.append( None )
  for swim in swims:
    if swim.date >= earliest_pb_date:
      event_code = swim.event.get_short_course_event_code()
      swim.converted_time = swim.race_time
      swim.qualifies = not (swim.meet in level_4_meets)
      if not swim.event.is_long_course():
        swim.converted_time = swim.event.convert_time( swim.race_time )
        # Truncate to 0.1s
        swim.converted_time = math.floor(swim.converted_time * 10) * 0.1
      
      pb = pb_by_event[ event_code ]
      qual_pb = qual_pb_by_event[ event_code ]
      if swim.qualifies and ((qual_pb is None) or (swim.converted_time < qual_pb.converted_time)):
        qual_pb_by_event[ event_code ] = swim
      if (pb is None) or (swim.converted_time < pb.converted_time):
        pb_by_event[ event_code ] = swim

  printed_name = False
  for i in range( 0, num_events ):
    pb = qual_pb_by_event[i]
    if pb is None:
      pb = pb_by_event[i]
    if pb is not None:
      qt = get_qualifying_time( i, swimmer.is_male, age )
      if qt is not None:
        race_time = pb.converted_time
        if race_time <= qt:
          tag_class = "qualified"
          if not pb.qualifies:
            tag_class = "not-qualified"
          if not printed_name:
            qt_file.write( full_name + " (" + str(age) + ")\n" )
            qt_html_file.write( '<tr class="name"><th colspan="5">' + full_name + " (" + str(age) + ")</th></tr>\n" )
            printed_name = True
          qt_file.write( "\t" + pb.event.short_name_without_course() + "\t" + str( RaceTime( race_time ) ) + "\t" + pb.meet + "\t" + pb.date.strftime( '%d/%m/%Y' ) + "\n" )
          qt_html_file.write( '<tr class="' + tag_class + '"><td> </td><td>' + pb.event.short_name_without_course() + "</td><td>" + str( RaceTime( race_time ) ) + "</td><td>" + pb.meet + "</td><td>" + pb.date.strftime( '%d/%m/%Y' ) + "</td></tr>\n" )
  if printed_name:
    qt_file.write( "\n" )

qt_html_file.write( '<table>' )    

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

# print( 'Writing file' )
# first = True
# for swimmer_times in all_swimmer_times:
  # if not first:
    # consideration_times_file.write( '\n' )
  # swimmer = swimmer_times.swimmer
  # consideration_times_file.write( str( swimmer ) + '\n' )
  # for consideration_time in swimmer_times.consideration_times:
    # if consideration_time.time is not None:
      # is_pb_str = 'pb'
      # if consideration_time.is_nt:
        # is_pb_str = 'nt'
      # consideration_times_file.write( consideration_time.event.short_name_without_course() + '|' + str( RaceTime( consideration_time.time ) ) + '|' + is_pb_str + '\n' )
  # first = False
qt_file.close()    

qt_html_file.write( '</table>' )    
qt_html_file.close()    

