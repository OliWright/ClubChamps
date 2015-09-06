# Winsford ASC Club Champs Scoring System
#   swimmer.py
#   Lightweight version of the GAE swimmer model used for off-line processing
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

import datetime
import helpers

class Swimmer():
  # Constructor.  Passed in a row of text describing the swimmer.
  def __init__(self, str):
    tokens = str.split( '|' )
    num_tokens = len( tokens )
    self.is_male = False
    if tokens[4] == 'M':
      self.is_male = True
    self.asa_number = int( tokens[0] )
    self.last_name = tokens[1]
    self.first_name = tokens[2]
    self.known_as = tokens[3]
    self.date_of_birth = helpers.ParseDate_dmY( tokens[5] )
    
  def full_name(self):
    return self.first_name + " " + self.last_name

  def alternate_name(self):
    return self.known_as + " " + self.last_name
    
  def date_of_birth_str(self):
    return self.date_of_birth.strftime("%d/%m/%Y")

  # Output the whole Swimmer in string format, with fields separated by '|' characters.
  # This is mirrored in swimmer.js
  def __str__(self):
    gender = "F"
    if self.is_male:
      gender = "M"
    return str( self.asa_number ) + "|" + self.last_name + "|" + self.first_name + "|" + self.known_as + "|" + gender + "|" + self.date_of_birth_str()
