import sys
from bootstrap import Bootstrap
from homecontrol.event import Event
from homecontrol.signal import Signal
from homecontrol.job import Job

class Scheduler(Bootstrap):
    
    def __init__(self, server):
        super(Scheduler, self).__init__(server)
        
        for job in Job.sql_load(self.sql()):
            
            if job.cron == None:
                continue
            
            self.log_debug("Schedule job \"%s\" ... " % job.name)
            #self.server.scheduler.add_cron_job(job.run, job.cron)

    def handle_request(self, handler, method, path=None, args={}, data=None):

        if path == "/":
            self.send_html_response(
                handler=handler, 
                html_file="assets/html/index.html", 
                devices=self.get_devices())

            return True

        return False
    
    def load_signals(self, handler, order_by = "name"):
        
        signals = Signal.sql_load(self.sql(), order_by=order_by)
        self.send_json_response(handler, signals)
    
    def save_signal(self, handler, data):
        
        try:
            
            signal = Signal.from_json(data)
            signal = signal.sql_save(self.sql())
            self.sql_commit()
    
        except Exception, e:
            self.log_error(e)
            self.send_json_response(handler, str(e), 400)
            return

        self.send_json_response(handler, signal)

    def load_jobs(self, handler, order_by = "name"):
        
        jobs = Job.sql_load(self.sql(), order_by=order_by)
        self.send_json_response(handler, jobs)
    
    def save_job(self, handler, data):

        job = Job.from_json(data)
        job = job.sql_save(self.sql())
        self.sql_commit()

        try:
            pass
        except Exception, e:
            self.log_error(e)
            self.send_json_response(handler, str(e), 400)
            return

        self.send_json_response(handler, job)
    