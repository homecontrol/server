import logging as log, json
from homecontrol.signal import Signal
from homecontrol.common import JSONEncoder

class Job(object):

    def __init__(self):
        
        self.id = None
        
        self.name = None
        self.description = None
        self.cron = None

        self.signals = []
    
    @staticmethod
    def sql_create(sql):
        
        sql.execute("CREATE TABLE IF NOT EXISTS jobs ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'name' TEXT NOT NULL, "
                    "'description' TEXT DEFAULT NULL, "
                    "'cron' TEXT DEFAULT NULL)")
        
        sql.execute("CREATE TABLE IF NOT EXISTS jobs_signals ( "
                    "job_id INTEGER NOT NULL, "
                    "signal_id INTEGER DEFAULT NULL, "
                    "position INTEGER NOT NULL, "
                    "PRIMARY KEY(job_id, signal_id, position), "
                    "FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE, "
                    "FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE)")
        return
    
    @staticmethod
    def sql_load(sql, job_id = None, order_by = None):
        Job.sql_create(sql)
        
        if job_id != None:
            sql.execute("SELECT id, name, description, cron "
                        "FROM jobs WHERE id=? LIMIT 0,1", (job_id,))
            
        else:
            if order_by == None: order_by = "name"
            sql.execute("SELECT id, name, description, cron "
                        "FROM jobs ORDER BY ?", (order_by,))
            
        result = sql.fetchall()
        
        if job_id != None and result == None:
            raise Exception("Could not find job id %i" % job_id)
            return None
        
        jobs = []
        for data in result:
            job = Job()
            (job.id, job.name, job.description, job.cron) = data
            
            sql.execute("SELECT signal_id FROM jobs_signals "
                        "WHERE job_id=? ORDER BY Position ASC", (job_id,))
            
            for (signal_id,) in sql.fetchall():
                job.add_signal(Signal.sql_load(sql, signal_id=signal_id))
                
            if job_id != None: return job
            jobs.append(job)
            
        return jobs
    
    def sql_save(self, sql):
        Job.sql_create(sql)
        
        if self.name == None:
            raise Exception("Job name not specified.")
        
        if self.id == None:

            sql.execute("INSERT INTO jobs (name, description, cron) "
                        "VALUES (?, ?, ?)", (self.name, self.description, self.cron))
            self.id = sql.lastrowid
            
            log.debug("Created job id %s" % str(self.id))
        else:

            sql.execute("UPDATE jobs "
                        "SET name = ?, description = ?, cron = ? "
                        "WHERE id = ?", (self.name, self.description, self.cron, int(self.id)))
            
            log.debug("Updated job id %s" % str(self.id))
        
        sql.execute("DELETE FROM jobs_signals WHERE job_id=?", (self.id,))
        
        for i in range(0, len(self.signals)):
            signal = self.signals[i]
            signal.sql_save(sql)
            sql.execute("INSERT INTO jobs_signals (job_id, signal_id, position) "
                        "VALUES (?, ?, ?)", (self.id, signal.id, i))
            
        return self
        
    def sql_delete(self, sql):
        Job.sql_create(sql)
        
        if self.id is None:
            raise Exception("Attempt to delete non-existing job.")
        
        sql.execute("DELETE FROM jobs WHERE id = ?", (self.id,))
        self.id = None
        return
    
    def add_signal(self, signal = None):
        self.signals.append(signal)
        
    @staticmethod
    def from_json(data):
        
        if type(data) != type({}):
            data = json.loads(str(data).strip())
        
        job = Job()
        if "id" in data and data["id"] != None: job.id = str(data["id"])
        job.name = str(data["name"])
        
        # Optional attributes
        if job.description == None: job.description = None
        else: job.description = str(data["description"])
        
        if job.cron == None: job.cron = None
        else: job.cron = str(data["cron"])
        
        for s in data["signals"]:
            job.add_signal(Signal.from_json(s))

        return job
        
    def to_json(self):
        
        obj = {}
        obj["id"] = self.id
        obj["name"] = self.name
        obj["description"] = self.description
        obj["cron"] = self.cron
        obj["signals"] = self.signals
        
        return json.dumps(obj, cls=JSONEncoder)