# Winsford ASC Club Champs Scoring System
#   qualifying_times.py
#   The times to use for calculating who qualifies for what
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from event import Event
from event import short_course_events
from race_time import RaceTime

_min_age = 12
_max_age = 17

_BOYS_SPREADSHEET_DATA_STR = """50 Free	31.6	29.9	28.8	27.2	27.1	26.9
100 Free	1:09.9	1:04.9	1:02.5	59.1	58.8	58.5
200 Free	2:29.7	2:21.8	2:15.6	2:06.5	2:05.8	2:05.0
400 Free	5:15.9	5:00.3	4:47.6	4:33.4	4:31.0	4:28.6
1500 Free	20:33.2	19:29.9	18:49.6	17:49.9	17:37.9	17:25.6
50 Breast	41.9	38.8	36.7	34.7	34.5	34.4
100 Breast	1:33.1	1:27.0	1:19.7	1:15.0	1:14.6	1:14.2
200 Breast	3:18.5	3:05.9	2:52.7	2:44.8	2:44.8	2:44.8
50 Fly	34.9	33.3	31.8	29.2	29.2	29.2
100 Fly	1:17.7	1:14.4	1:10.5	1:03.0	1:02.5	1:02.5
200 Fly	2:58.9	2:46.1	2:39.2	2:26.5	2:26.5	2:26.5
50 Back	37.4	35.7	33.5	31.8	31.5	31.2
100 Back	1:17.8	1:14.3	1:09.7	1:05.5	1:05.1	1:04.5
200 Back	2:51.4	2:43.0	2:31.3	2:22.4	2:22.4	2:22.4
200 IM	2:52.9	2:41.2	2:34.1	2:24.9	2:24.5	2:22.8
400 IM	6:10.0	5:48.8	5:35.9	5:04.8	5:04.8	4:58.3"""

_GIRLS_SPREADSHEET_DATA_STR = """50 Free	33.2	31.9	31.3	30.2	30.2	30.1
100 Free	1:10.5	1:07.8	1:06.5	1:04.2	1:04.2	1:04.2
200 Free	2:30.9	2:25.8	2:23.3	2:17.6	2:16.8	2:16.0
400 Free	5:18.8	5:06.7	5:02.6	4:49.6	4:49.6	4:49.6
800 Free	10:55.5	10:32.9	10:19.8	9:47.3	9:47.3	9:47.3
50 Breast	40.8	39.3	38.8	37.8	37.8	37.7
100 Breast	1:30.8	1:25.4	1:24.2	1:22.1	1:22.1	1:22.0
200 Breast	3:15.0	3:02.7	3:01.9	2:59.5	2:59.5	2:59.5
50 Fly	35.7	34.2	33.5	32.3	32.3	32.3
100 Fly	1:20.5	1:14.3	1:12.7	1:09.3	1:09.3	1:09.3
200 Fly	3:05.4	2:55.6	2:45.2	2:37.5	2:37.3	2:37.1
50 Back	38.3	36.5	35.5	34.2	34.2	34.2
100 Back	1:19.7	1:16.0	1:14.0	1:10.3	1:10.3	1:10.2
200 Back	2:49.1	2:41.7	2:38.6	2:32.6	2:32.2	2:32.0
200 IM	2:51.3	2:43.8	2:42.7	2:36.6	2:36.3	2:36.0
400 IM	6:12.6	5:50.1	5:41.8	5:26.3	5:26.3	5:26.3"""

def _parse_spreadsheet_data( spreadsheet_data ):
  rows = spreadsheet_data.split( '\n' )

  num_events = len( short_course_events )
  qt_by_event = [ None ] * num_events
  expected_num_columns = _max_age - _min_age + 2
  
  for row in rows:
    columns = row.split( '\t' )
    # Parse the event name
    event_code = Event.create_from_str( columns[0], 'S' ).event_code
    if len( columns ) != expected_num_columns:
      raise RuntimeError( "Unexpected number of columns in spreadsheet data" )
    qt_for_event = []
    qt_by_event[ event_code ] = qt_for_event
    for i in range( 1, expected_num_columns ):
      if len( columns[i] ) == 0:
        qt_for_event.append( None )
      else:
        qt_for_event.append( float( RaceTime( columns[i] ) ) )
  return qt_by_event
        
_boys_qt_by_event = _parse_spreadsheet_data( _BOYS_SPREADSHEET_DATA_STR )
_girls_qt_by_event = _parse_spreadsheet_data( _GIRLS_SPREADSHEET_DATA_STR )
    
def get_qualifying_time( event_code, is_male, age ):
  qt_for_event = None
  if is_male:
    qt_for_event = _boys_qt_by_event[ event_code ]
  else:
    qt_for_event = _girls_qt_by_event[ event_code ]
  if qt_for_event is None:
    return None
  qt_age = age
  if age < _min_age:
    qt_age = _min_age
  if age > _max_age:
    qt_age = _max_age
  return qt_for_event[ qt_age - _min_age ]