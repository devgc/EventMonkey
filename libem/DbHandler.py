#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import logging

DB_LOGGER = logging.getLogger('DbHandler')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DbConfig():
    def __init__(self,db_type=None,db=None,host=None,port=None,user=None,passwd=None):
        self.db_type = db_type
        self.db = db
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        
    def GetDbHandle(self):
        dbhandle = DbHandler(
            self
        )
        
        return dbhandle
    
class DbHandler():
    def __init__(self,db_config,table=None):
        #Db Flags#
        self.db_config = db_config
        
    def InitDb(self):
        pass
        
    def CreateTableFromMapping(self,tbl_name,field_mapping,primary_key_str,field_order):
        dbh = self.GetDbHandle()
        
        string = "CREATE TABLE IF NOT EXISTS {0:s} (\n".format(tbl_name)
        for field in field_order:
            string += "{0:s} {1:s},\n".format(field,field_mapping[field])
        
        if primary_key_str is not None:
            string = string + primary_key_str
        else:
            string = string[0:-2]
        
        string = string + ')'
        
        cursor = dbh.cursor()
        
        cursor.execute(string)
    
    def CreateInsertString(self,table,row,column_order,INSERT_STR=None):
        columns = ', '.join(column_order)
        
        in_row = []
        
        #logging.debug('column_order type: {}'.format(str(type(column_order))))
        
        if type(column_order) == dict:
            for key in column_order:
                in_row.append(row[key])
                
        elif type(column_order) == list:
            '''Issue here...'''
            if type(row) == list:
                cnt = 0
                for key in column_order:
                    in_row.append(row[cnt])
                    cnt += 1
            else:
                for key in column_order:
                    in_row.append(row[key])
            
        if self.db_config.db_type == 'sqlite':
            placeholders = ','.join('?' * len(in_row))
        else:
            raise Exception('Unsupported db type')
        
        if self.db_config.db_type == 'sqlite':
            if INSERT_STR == None:
                INSERT_STR = 'INSERT OR IGNORE'
            
            sql = '{} INTO {} ({}) VALUES ({})'.format(INSERT_STR,table,columns, placeholders)
            
        return sql
    
    def InsertFromListOfLists(self,table,rows_to_insert,column_order,INSERT_STR=None):
        dbh = self.GetDbHandle()
        sql_c = dbh.cursor()
        
        #Create SqlString#
        sql = self.CreateInsertString(
            table,
            column_order,
            column_order,
            INSERT_STR=None
        )
        
        for row in rows_to_insert:
            sql_c.execute(sql,row)
            
        dbh.commit()
    
    def InsertFromListOfDicts(self,table,rows_to_insert,column_order,INSERT_STR=None):
        dbh = self.GetDbHandle()
        sql_c = dbh.cursor()
        
        for row in rows_to_insert:
            in_row = []
            sql = self.CreateInsertString(
                table,
                row,
                column_order,
                INSERT_STR=None
            )
            
            for key in column_order:
                in_row.append(row[key])
            try:
                sql_c.execute(sql,in_row)
            except Exception as e:
                DB_LOGGER.error("[ERROR] {}\n[SQL] {}\n[ROW] {}".format(str(e),sql,str(row)))
        
        dbh.commit()
    
    def DropTable(self,tbl_name):
        dbh = self.GetDbHandle()
        
        string = "DROP TABLE IF EXISTS {0:s}".format(tbl_name)
        
        cursor = dbh.cursor()
        try:
            cursor.execute(string)
        except:
            pass
        
        dbh.commit()
    
    def CreateView(self,view_str):
        dbh = self.GetDbHandle()
        cursor = dbh.cursor()
        try:
            cursor.execute(view_str)
            dbh.commit()
        except Exception as e:
            logging.error(str(e))
        
    def GetRecordCount(self,table):
        '''Get the record count for a given table'''
        dbh = self.GetDbHandle()
        sql_c = dbh.cursor()
        
        sql_string = 'SELECT COUNT(*) FROM {}'.format(table)
        
        sql_c.execute(sql_string)
        row = sql_c.fetchone()
        
        return row[0]
    
    def GetDbHandle(self):
        '''Create database handle based off of databaseinfo'''
        dbh = None
        
        if self.db_config.db_type == 'sqlite':
            dbh = sqlite3.connect(
                self.db_config.db,
                #isolation_level=None,
                timeout=10000
            )
        else:
            pass
        
        return dbh
    
    def FetchRecords(self,sql_string,row_factory=None):
        '''Generator for return fields from sql_string
        
        Args:
            sql_string: SQL statement to execute
            row_factory: How to handle rows.
                -MySQL: MySQLdb.cursors.DictCursor
        
        Yields:
            list of column names,
            row
        '''
        dbh = self.GetDbHandle()
        
        column_names = []
        
        if self.db_config.db_type == 'sqlite':
            if row_factory == type(dict):
                dbh.row_factory = dict_factory
            else:
                dbh.row_factory = sqlite3.Row
            
            sql_c = dbh.cursor()
        else:
            raise Exception('Unknown Database Type {}'.format(self.db_config['db_type']))
        
        sql_c.execute(sql_string)
        
        for desc in sql_c.description:
            column_names.append(
                desc[0]
            )
        
        for record in sql_c:
            yield column_names,record
            
    def GetDbTransaction(self):
        return DbTransaction(self)
    
class DbTransaction():
    def __init__(self,dbHandler):
        self.dbHandler = dbHandler
        self.dbh = self.dbHandler.GetDbHandle()
        self.cur = self.dbh.cursor()
        
    def InsertDict(self,table,row,or_str='',column_order=None):
        if self.dbHandler.db_config.db_type == 'sqlite':
            if column_order is None:
                columns = ', '.join(row.keys())
                placeholders = ':'+', :'.join(row.keys())
                query = 'INSERT %s INTO %s (%s) VALUES (%s)' % (or_str,table,columns,placeholders)
                
                self.cur.execute(query,row.values())
            else:
                in_row = []
                query = self.CreateInsertString(
                    table,
                    row,
                    column_order,
                    INSERT_STR=None
                )
                
                for key in column_order:
                    in_row.append(row.get(key))
                
                self.cur.execute(query,in_row)
        else:
            raise Exception('Unknown DB Type {}'.format(
                self.dbHandler.db_config.db_type))
        
    def CreateInsertString(self,table,row,column_order,INSERT_STR=None):
        columns = ', '.join(column_order)
        
        in_row = []
        for key in column_order:
            in_row.append(row.get(key,None))
            
        if self.dbHandler.db_config.db_type == 'sqlite':
            placeholders = ','.join('?' * len(in_row))
        else:
            raise Exception('Unsupported db type')
        
        if self.dbHandler.db_config.db_type == 'sqlite':
            if INSERT_STR == None:
                INSERT_STR = 'INSERT OR IGNORE'
            
            sql = '{} INTO {} ({}) VALUES ({})'.format(INSERT_STR,table,columns, placeholders)
            
        return sql
    
    def Commit(self):
        self.dbh.commit()
        self.dbh.close()
    