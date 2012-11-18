import sys
from bootstrap import Bootstrap
from homecontrol.event import Event
from homecontrol.signal import Signal
from homecontrol.job import Job

class Scheduler(Bootstrap):
    
    def __init__(self, server):
        super(Scheduler, self).__init__(server)
        
        for job in Job.sql_load(self.sql()):
            
            if job.cron == None or len(job.cron) == 0:
                continue
            
            self.log_debug("Schedule job \"%s\" ... " % job.name)
            
            try:
                
                def run_job(): job.run(server.devices)
                self.server.scheduler.add_cron_job(run_job, **job.cron)
                
            except (ValueError, TypeError) as e:
                self.log_error("Error when scheduling job \"%s\", cron \"%s\": %s" % (job.name, job.cron, e)) 

    def view(self, handler):

        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html", 
            devices=self.get_devices())
    
    def load_signals(self, handler, order_by = "name"):
        
        signals = Signal.sql_load(self.sql(), order_by=order_by)
        handler.send_json_response(signals)
    
    def save_signal(self, handler):
        
        try:
            
            signal = Signal.from_json(handler.get_post_data())
            signal = signal.sql_save(self.sql())
            self.sql_commit()
    
        except Exception, e:
            self.log_error(e)
            handler.send_json_response(str(e), 400)
            return

        handler.send_json_response(signal)

    def load_jobs(self, handler, order_by = "name"):
        
        jobs = Job.sql_load(self.sql(), order_by=order_by)
        handler.send_json_response(jobs)
    
    def save_job(self, handler):

        job = Job.from_json(handler.get_post_data())
        job = job.sql_save(self.sql())
        self.sql_commit()

        try:
            pass
        except Exception, e:
            self.log_error(e)
            handler.send_json_response(str(e), 400)
            return

        handler.send_json_response(job)