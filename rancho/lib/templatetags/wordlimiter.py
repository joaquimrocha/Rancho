########################################################################
# Rancho - Open Source Group/Project Management Tool
#    Copyright (C) 2008 The Rancho Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

from django import template

register = template.Library()

def wordlimiter(context, text='', number_of_words=25):
    """
    Displays *approximately* the amount of words described by the argument number_of_words from the text (in reading order).
    """
    
    words = text.split()
    
    if number_of_words<len(words):
        words = words[:number_of_words]
        number_to_limit = len(' '.join(words))
        text = text[:number_to_limit]
        text = text[:max(text.rfind(' '), text.rfind('\n'))]+'...'

    return { 'text' : text }

register.inclusion_tag("lib/wordlimiter.html", takes_context=True)(wordlimiter)
