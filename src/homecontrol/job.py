import logging as log
from homecontrol.signal import Signal

class Job(object):

    def __init__(self):
        
        self.id = None
        
        self.name = None
        self.description = None
        self.cron = None

        self.signals = []
    
    @staticmethod
    def sql_create(sql):
        
        sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'jobs' ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'name' TEXT NOT NULL, "
                    "'description' TEXT DEFAULT NULL, "
                    "'cron' TEXT DEFAULT NULL)")
        
        sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'jobs_signals' ( "
                    "job_id INTEGER NOT NULL, "
                    "signal_id INTEGER DEFAULT NULL, "
                    "position INTEGER NOT NULL, "
                    "PRIMARY KEY(job_id, signal_id), "
                    "FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE, "
                    "FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE)")
        return
    
    @staticmethod
    def sql_load(sql, job_id):
        Job.sql_create(sql)
        
        sql.execute("SELECT id, name, description, cron "
                    "FROM 'jobs' WHERE id=? LIMIT 0,1", (job_id,))
            
        data = sql.fetchone()
        if data == None:
            raise Exception("Could not find job id %i" % job_id)
        
        job = Job()
        (job.id, job.name, job.description, job.cron) = data
        
        sql.execute("SELECT signal_id FROM 'jobs_signals' "
                    "WHERE job_id=? ORDER BY Position ASC", (job_id,))
        
        for (signal_id,) in sql.fetchall():
            job.add_signal(Signal.sql_load(sql, signal_id=signal_id))
            
        return job
    
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
        
        sql.execute("DELETE FROM jobs_signal WHERE job_id=?", (self.id,))
        for signal in self.signals:
            signal.sql_save(sql)
            sql.execute("INSERT INTO jobs_signals (job_id, signal_id) "
                        "VALUES (?, ?)", (self.id, signal.id))
        return
        
    def sql_delete(self, sql):
        Job.sql_create(sql)
        
        if self.id is None:
            raise Exception("Attempt to delete non-existing job.")
        
        sql.execute("DELETE FROM jobs WHERE id = ?", (self.id,))
        self.id = None
        return
    
    def add_signal(self, signal):
        self.signals.append(signal)
        
    @staticmethod
    def from_json(data):
        
            data = json.loads(data)
            
            job = Job()
            if "id" in data: job.id = str(data["id"])
            job.name = str(data["name"])
            job.description = str(data["description"])
            job.cron = str(data["cron"])
            
            # Optional attributes
            if job.description == "": job.description = None
            if job.cron == "": job.cron = None
            
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
        
        # Optional attributes
        if self.description == None: obj["description"] = "";
        if self.cron == None: obj["cron"] = "";
        
        return json.dumps(obj, cls=JSONEncoder)