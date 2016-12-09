#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import collections
import geoip2
import geoip2.database
from geoip2.errors import AddressNotFoundError
import json

class IpHandler():
    def __init__(self):
        pass
    
    def GetIpInfo(self,ip_address):
        ip_info = collections.OrderedDict([])
        if self.city_reader:
            try:
                city_info = self.city_reader.city(ip_address)
                ip_info['ip'] = ip_address
                ip_info['continent'] = city_info.continent.names['en']
                ip_info['country'] = city_info.country.names['en']
                ip_info['iso_code'] = city_info.country.iso_code
            except AddressNotFoundError:
                ip_info['ip'] = ip_address
            
        return ip_info
    
    def AttachGeoDbs(self,geodb_path):
        self.geodb_path = geodb_path
        self.city_reader = None
        self.country_reader = None
        
        for root, subdirs, files in os.walk(self.geodb_path):
            for filename in files:
                if filename == 'GeoLite2-City.mmdb':
                    self.city_reader = geoip2.database.Reader(os.path.join(self.geodb_path,'GeoLite2-City.mmdb'))
                elif filename == 'GeoLite2-Country.mmdb':
                    self.country_reader = geoip2.database.Reader(os.path.join(self.geodb_path,'GeoLite2-Country.mmdb'))