#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import bs4

def GetDictionary(xml_string,force_list=[]):
    soup = BeautifulSoup(xml_string,'xml')
    
    xml = Xml(
        soup,
        force_list=force_list
    )
    
    return xml
    
class Xml(dict):
    def __init__(self,soup,force_list):
        setattr(self,'depth',0)
        setattr(self,'force_list',force_list)
        setattr(self,'current_field_str','')
        
        for tag in soup.children:
            ttype = dict
            tag_dict = self._ProcessTag(tag,ttype)
            if tag_dict is not None:
                self.update(tag_dict)
        
    def _ProcessTag(self,tag,ttype):
        '''
        args
            tag: The tag to parse into dict struct
            ttype: dict or list
        return
            tag_dict: dictionary representing tag
        '''
        if type(tag) == bs4.element.NavigableString:
            return None
        
        # Add current item name
        self.current_field_str = self.current_field_str + u'{}'.format(tag.name)
        
        if ttype == list:
            current_tag = {}
            current_tag[tag.name] = {}
        else:
            current_tag = {}
            current_tag[tag.name] = {}
        
        #Get Tag Attributes#
        attr_flag = False
        if hasattr(tag,'attrs'):
            if len(tag.attrs) > 0:
                attr_flag = True
                if ttype == list:
                    current_tag.update(tag.attrs)
                else:
                    current_tag[tag.name].update(tag.attrs)
                
        # Get Tag String#
        if tag.string is not None:
            tstr = tag.string
            if ttype == list:
                current_tag.update({
                    '#text':tag.string
                })
            else:
                current_tag[tag.name].update({
                    '#text':tag.string
                })
        
        # Iterate children tags#
        for next_tag in tag.children:
            #Skip if item is String (not tag)#
            if type(next_tag) == bs4.element.NavigableString:
                continue
            
            #We are diving down a tag, so increase depth#
            self.depth += 1
            
            next_name = self.current_field_str + u'.' + next_tag.name
            
            #Check if next tag needs to be list#
            if CheckTagIsList(next_name,self.force_list,next_tag):
                ttype = list
            
            self.current_field_str = self.current_field_str + u'.'
            #Get Dictionary of next Tag#
            tag_dict = self._ProcessTag(
                next_tag,
                ttype
            )
            self.current_field_str = self.current_field_str[:-1]
            
            #Determine how to add to current tag#
            if ttype == dict:
                #Update if type dict#
                current_tag[tag.name].update(tag_dict)
            elif ttype == list:
                if next_tag.name not in current_tag[tag.name]:
                    current_tag[tag.name][next_tag.name] = []
                current_tag[tag.name][next_tag.name].append(tag_dict)
            else:
                raise Exception('Bad Tag Type')
            
            #We are coming up a tag, so decrease depth#
            self.depth -= 1
            
        # Remove last item name
        self.current_field_str = self.current_field_str[:-len(tag.name)]
        
        return current_tag

def CheckTagIsList(current_field_str,force_list,tag):
    if current_field_str in force_list:
        return True
    else:
        test = tag.parent.find_all(tag.name)
        if len(test) > 1:
            return True
    
    return False
    