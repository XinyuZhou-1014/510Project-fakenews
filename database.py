import sqlite3

class TextDb_Sqlite():
    def __init__(self, dbname="fakenews.db", tblname="headline_body"):
        self.dbname = dbname
        self.tblname = tblname
        flag = self.reset()
        # do something on flag

    def _basic_execute(self, command_list, bool_list, info_success="success", info_fail="failed"):
        flag = False
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            for command, boolean in list(zip(command_list, bool_list)):
                if boolean:
                    cursor.execute(command)
            if info_success is not None:
                print(info_success)
            flag = True
        except sqlite3.Error as e:
            print ("%s:" % info_fail, e.args[0])
            flag = False
        finally:
            cursor.close()
            conn.commit()
            conn.close()
            return flag

    def _basic_read(self, command, info_success="Read success", info_fail="Read fail"):
        values = False
        try:
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            cursor.execute(command)
            values = cursor.fetchall()
            print(info_success)
        except sqlite3.Error as e:
            print ("%s:" % info_fail, e.args[0])
            values = False
        finally:
            cursor.close()
            conn.commit()
            conn.close()
            return values

    def _convert(self, list_data):
        h, b, y = [], [], []
        for data in list_data:
            _, headline, body, label = data
            h.append(headline)
            b.append(body)
            y.append(label)
        return h, b, y

    def reset(self, drop_old=False):
        command_list = ["drop table if exists %s" % self.tblname,
                        """create table if not exists %s 
                        (
                          id INT primary key, 
                          Headline TINYTEXT, 
                          body TEXT, 
                          Label TINYINT
                        )""" % (self.tblname)
                       ]
        bool_list = [drop_old, True]
        info_success="success reset %s/%s" % (self.dbname, self.tblname)
        info_fail="fail to reset"
        return self._basic_execute(command_list, bool_list, info_success, info_fail)

    def write(self, headlines, bodies, labels=None):
        # convert single to list
        if not isinstance(headlines, list):
            headlines = [headlines]
        if not isinstance(bodies, list):
            bodies = [bodies]
        if labels is None:
            labels = [-1] * len(bodies)
        elif not isinstance(labels, list):
            labels = [labels]

        # check length
        try:
            assert len(headlines) == len(bodies)
            assert len(bodies) == len(labels)
        except AssertionError:
            print ("different number among headlines, bodies and labels")

        command_list = []
        bool_list = []
        for i in range(len(labels)):
            command = '''insert into %s 
                         (id, headline, body, label) 
                         values (NULL, \'%s\', \'%s\', \'%s\')
                      ''' % (self.tblname, headlines[i], bodies[i], labels[i])
            command_list.append(command)
            bool_list.append(True)
        info_success = "Insert success"
        info_fail = "Error when insert"
        return self._basic_execute(command_list, bool_list, info_success, info_fail)

    def read_all(self, convert=True):
        # can't use basic_execute because it has return value
        command = 'select * from %s' % (self.tblname)
        info_success = "Read all success"
        info_fail = "Read all fail"
        res = self._basic_read(command, info_success, info_fail)
        if convert:
            return self._convert(res)
        else:
            return res

    def read_labeled(self, convert=True):
        # can't use basic_execute because it has return value
        command = '''select * from %s 
                     where label = 0 or label = 1 or label = 2 or label = 3
                  ''' % (self.tblname)
        info_success = "Read all success"
        info_fail = "Read all fail"
        res = self._basic_read(command, info_success, info_fail)
        if convert:
            return self._convert(res)
        else:
            return res
    
    # too powerful...
    '''
    def execute(self, command, info_success=None, info_fail=None, show_info_length=20):
        # leave %s in command as tblname
        try:
            command = command % self.tblname
        except TypeError:
            print("Please leave table name as %s")
            return False
        command_list = [command]
        if info_success is None:
            info_success = "User command <%s> success" % command[show_info_length]
        if info_fail is None:
            info_fail = "User command <%s> fail" % command[:show_info_length]
        return self._basic_execute(command_list, [True], info_success, info_fail)
    '''

    def stream_write(self):
        pass


if __name__ == "__main__":
    db = TextDb_Sqlite()
    db.reset(drop_old=True)
    db.write("i love fox", "a fox is running across a sleeping dog.", "2")
    db.write("i love fox", "a fox is running across a sleeping dog.", "-1")
    db.write("i love fox", "a fox is running across a sleeping dog.", "3")
    db.write("dfsdff", "kjljqdqdjq", "2")
    db.write("asaf", "sfas")
    print(db.read_labeled())


