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
from django.template import Variable

register = template.Library()

def modalconfirm(context, linkid, question, yesfunction, nofunction=None ):
    def get_function_name_and_args(function_and_args):
        if not function_and_args:
            return None, []
        
        function_and_args = function_and_args.strip()
        function_and_args_list = function_and_args.split('(')
        
        #just funcname 
        if len(function_and_args_list) == 1:
            function_name = function_and_args_list[0]            
            return function_name, []
        
        function, args_as_string = function_and_args_list
        args_as_string = args_as_string.strip(')')
        #just funcname()
        if args_as_string == '':
            return function, []
        
        #funcname(arg1, 'arg2',...)
        args = args_as_string.split(',')               
        function_name, function_args = function, [arg.strip() for arg in args]                    
        return function_name, function_args

    def replace_variable_content(variable_name, context):
        """
        replaces all {{varname}} ocurrences in a string with the value
        """
        pieces = variable_name.split('{{')
        replaced_string = ''        
        for piece in pieces:
            variable_replaced = piece
            close_var_index = piece.find('}}')
            if close_var_index != -1:
                variable_replaced = str(Variable(piece[:close_var_index]).resolve(context))+piece[close_var_index+2:]
            replaced_string += variable_replaced
        return replaced_string 
    
    linkidnew = replace_variable_content(linkid, context)
    yesfunction, yesargs = get_function_name_and_args(yesfunction)
    nofunction, noargs = get_function_name_and_args(nofunction)
            
    yes_function_args = [Variable(arg).resolve(context) for arg in yesargs]
    no_function_args = [Variable(arg).resolve(context) for arg in noargs]
        
    context = {'link_id': linkidnew,
                'question': question,
                'yes_function': yesfunction,
                'yes_function_args': ', '.join([str(arg) for arg in yes_function_args]),
                'no_function': nofunction,
                'no_function_args': ', '.join([str(arg) for arg in no_function_args]),
            }
    
    return context

register.inclusion_tag("lib/modalconfirm.html", takes_context=True)(modalconfirm)
