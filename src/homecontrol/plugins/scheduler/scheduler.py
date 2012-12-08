import sys, copy
from bootstrap import Bootstrap
from homecontrol.event import Event
from homecontrol.signal import Signal
from homecontrol.job import Job

class Scheduler(Bootstrap):
    
    def __init__(self, server):
        super(Scheduler, self).__init__(server)
        
        self.job_store = {}
        self.schedule_all_jobs()

    def schedule_all_jobs(self, handler = None):
        
        for job in Job.sql_load(self.sql()):
            
            if job.cron == None or len(job.cron) == 0:
                continue
            
            self.schedule_job(job)
                
        if handler != None:
            handler.send_json_response("ok");
            
    def schedule_job(self, job=None, job_id=None, sql=None):
        
        if job == None:
            if job_id == None:
                raise AttributeError("Neither \"job\" nor \"job_id\" specified!");            
            job = Job.sql_load(sql, job_id=job_id)        
        
        self.log_debug("Schedule job \"%s\", id \"%i\"" % (job.name, job.id))
        
        cron = None
        if job.id in self.job_store:
            (job, cron) = self.job_store[job.id]
        
        if cron != None:            
            self.log_debug("Job \"%s\", id \"%i\" already scheduled, skip." % (job.name, job.id))
            return
        
        try:
            cron = self.server.scheduler.add_cron_job(job.run, kwargs={ "devices": self.server.devices }, **job.cron)
        except (ValueError, TypeError) as e:
            self.log_error("Error when scheduling job \"%s\", id \"%i\", cron \"%s\": %s" % (job.name, job.id, job.cron, e))
            cron = None
            
        self.job_store[job.id] = (job, cron)
            
    def unschedule_job(self, job=None, job_id=None, sql=None):
        
        if job == None:
            if job_id == None:
                raise AttributeError("Neither \"job\" nor \"job_id\" specified!");            
            job = Job.sql_load(sql, job_id=job_id)
                
        self.log_debug("Unschedule job \"%s\", id \"%i\"" % (job.name, job.id))
        
        if job.id not in self.job_store:
            self.log_debug("Job \"%s\", id \"%i\" not scheduled, skip." % (job.name, job.id))
            return
        
        (job, cron) = self.job_store[job.id]
        self.server.scheduler.unschedule_job(cron)
        self.job_store[job.id] = (job, None)
            
    def get_next_run(self, handler, job_id):
        job_id = int(job_id)
        
        if job_id not in self.job_store: return None;
        (job, cron) = self.job_store[job_id]
        
        if cron != None: handler.send_json_response(str(cron.next_run_time))

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