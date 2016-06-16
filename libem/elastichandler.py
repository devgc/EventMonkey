#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# reload(sys)
# sys.setdefaultencoding('UTF8')
import logging
import os
import json
import md5
import datetime
import re

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk as es_bulk
from elasticsearch import helpers

#logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

ELASTIC_LOGGER = logging.getLogger('ElasticHandler')

class EsConfig():
    def __init__(self,host=None):
        self.host = host
        
    def GetEsHandler(self):
        esHandler = EsHandler(
            self
        )
        
        return esHandler
    
class EsHandler():
    def __init__(self,esConfig):
        self.current_index = None
        self.esh = Elasticsearch(
            esConfig.host,
            timeout=100000
        )
        
    def CheckForIndex(self,index_name):
        return self.esh.indices.exists(index_name)
    
    def IndexRecord(self,index,doc_type,record):
        '''
        Index a single record
        IN
            self: EsHandler
            index: the index name
            doc_type: the document type to index as
            record: The dictionary record to be indexed
        '''
        #Create hash of our record to be the id#
        m = md5.new()
        m.update(json.dumps(record))
        hash_id = m.hexdigest()
        
        #Index the record#
        res = self.esh.index(
            ignore=[400], #This will ignore fields if the field doesnt match the mapping type (important for fields where timestamp is blank)
            index=index,
            doc_type=doc_type,
            id=hash_id,
            body=record
        )
        
    def BulkIndexRecords(self,records):
        '''
        Bulk Index Records
        IN
            self: EsHandler
            records: a list of records to bulk index
        '''
        ELASTIC_LOGGER.debug('[starting] Indexing Bulk Records')
        success_count,failed_items = es_bulk(
            self.esh,
            records,
            chunk_size=10000,
            raise_on_error=False
        )
        
        if len(failed_items) > 0:
            ELASTIC_LOGGER.error('[PID {}] {} index errors'.format(
                os.getpid(),len(failed_items)
            ))
            for failed_item in failed_items:
                ELASTIC_LOGGER.error(unicode(failed_item))
        
        ELASTIC_LOGGER.debug('[finished] Indexing Bulk Records')
        
    def CheckForMapping(self,doc_type,index=None):
        '''
        Check if a mapping exists for a given document type
        IN
            self: EsHandler
            index: the name of the index
            doc_type: the document type
        OUT
            True - Mapping exists for doc_type in index
            False - Mapping does not exists for doc_type in index
        '''
        index = self._SetIndex(index)
        
        mapping = self.esh.indices.get_mapping(
            index = index,
            doc_type = doc_type
        )
        
        count = len(mapping.keys())
        
        if count > 0:
            return True
        
        return False
    
    def InitializeMapping(self,doc_type,mapping,index=None):
        '''
        Create mapping for a document type
        IN
            self: EsHandler
            index: the name of the index
            doc_type: the document type
            mapping: The dictionary mapping (not a json string)
        '''
        index = self._SetIndex(index)
        
        self.esh.indices.put_mapping(
            doc_type=doc_type,
            index=index,
            body=mapping['mappings']
        )
    
    def InitializeIndex(self,index=None):
        '''
        Create an index
        IN
            self: EsHandler
            index: the name of the index to create
        '''
        index = self._SetIndex(index)
        
        request_body = {
            "settings" : {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                'analysis': {
                    'analyzer': {
                        'file_path': {
                            'type': 'custom',
                            'tokenizer': 'path_hierarchy',
                            'filter': ['lowercase']
                        }
                    }
                }
            },
        }
        
        res = self.esh.indices.create(
            index = index,
            body = request_body
        )
    
    def GetRecordsFromFile_Result(self,query_file,index=None):
        ''' **NEEDS WORK - NOT COMPLETE**
        Return results based off of a query from a json file
        IN
            self: EsHandler
            index: the index name
            query_file: the file that contains a query
        OUT
            None: This returns none because this function is not complete
        '''
        index = self._SetIndex(index)
        
        with open(query_file,'rb') as qfh:
            query = json.load(qfh)
            
        qfh.close
        
        result = self.esh.search(
            index=index,
            scroll='60s',
            size=1000,
            body=query
        )
        
        total_hits = result['hits']['total']
        
        scroll_size = total_hits
        
        while (scroll_size > 0):
            scroll_id = result['_scroll_id']
            
            result = self.esh.scroll(
                scroll_id=scroll_id,
                scroll='60s'
            )
            records = result['hits']['hits']
            
            for hit in records:
                yield hit
            scroll_size -= len(records)
    
    def FetchRecordsFromQuery(self,query,index=None):
        '''
        Yield hits based off of a query from a json str
        IN
            self: EsHandler
            query: the query (can be dictionary or json str)
            index: the index name
        OUT
            hit: Yields hits for the query
        '''
        #If query is a string, load from json#
        if isinstance(query,str) or isinstance(query,unicode):
            query = json.loads(query)
            
        index = self._SetIndex(index)
        
        result = self.esh.search(
            index=index,
            scroll='60s',
            size=1000,
            body=query
        )
        
        total_hits = result['hits']['total']
        
        scroll_size = total_hits
        
        while (scroll_size > 0):
            scroll_id = result['_scroll_id']
            
            for hit in result['hits']['hits']:
                yield hit
                
            scroll_size -= len(result['hits']['hits'])
            
            result = self.esh.scroll(
                scroll_id=scroll_id,
                scroll='60s'
            )
    
    def GetRecordsFromQueryStr_Dict(self,json_str,mapping,index=None):
        '''
        Return dictionary of results based off of mapping list. The last item in the
        mapping list should be unique, otherwise reocrds can overwrite records.
        
        This function attempts to emulate perl dbi's fetchall_hashref([key,key,...]).
        
        IN
            self: EsHandler
            json_str: query
            mapping: list of mapping keys
            index: The index to search. default=None (if None, will use self.current_index)
        OUT
            record_dict: dictionary of hits based off of mapping
        '''
        query = json.loads(json_str)
        record_dict = {}
        
        if index == None:
            if self.current_index == None:
                msg = 'No index given, and no current index specified. Pass in index=INDEX or use EsHandler.SetCurrentIndex(INDEX) first'
                raise Exception(msg)
            else:
                index = self.current_index
        
        result = self.esh.search(
            index=index,
            scroll='60s',
            size=1000,
            body=query
        )
        
        scroll_size = result['hits']['total']
        
        while (scroll_size > 0):
            scroll_id = result['_scroll_id']
            
            for hit in result['hits']['hits']:
                #eumerated mapping#
                emapping = []
                #for each key in mapping, enumerate the value#
                for key in mapping:
                    emapping.append(
                        hit['_source'][key]
                    )
                
                #Set current level#
                current_level = record_dict
                
                #set markers#
                c = 1
                lp = len(emapping)
                
                #create dictionary keys based off of enumerated mapping#
                for key in emapping:
                    if key not in current_level:
                        if lp == c:
                            current_level[key] = hit
                        else:
                            current_level[key] = {}
                    current_level = current_level[key]
                    c += 1
            #update scroll size#
            scroll_size -= len(result['hits']['hits'])
            
            #update result#
            result = self.esh.scroll(
                scroll_id=scroll_id,
                scroll='60s'
            )
            
        return record_dict
    
    def SetCurrentIndex(self,index_name):
        '''
        Set the current index to index_name.
        IN
            self: EsHandler
            index_name: name of the index
        '''
        self.current_index = index_name
        
    def _SetIndex(self,index):
        if index == None:
            if self.current_index == None:
                msg = 'No index given, and no current index specified. Pass in index=INDEX or use EsHandler.SetCurrentIndex(INDEX) first'
                raise Exception(msg)
            else:
                index = self.current_index
        
        return index
    
if __name__ == '__main__':
    pass