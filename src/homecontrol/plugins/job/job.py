from homecontrol.plugin import Plugin
from bootstrap import Bootstrap
import homecontrol.job, inspect, homecontrol.signal

class Job(Bootstrap):
        
    def view(self, handler, job_id):

        job = homecontrol.job.Job.sql_load(self.sql(), job_id)

        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html", 
            html_form_data = {"name": job.name},
            job = job,
            signals = homecontrol.signal.Signal.sql_load(self.sql()),
            devices = self.get_devices())
    
    def create(self, handler):
        
        job = homecontrol.job.Job()

        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html",
            job = job,
            signals = homecontrol.signal.Signal.sql_load(self.sql()),
            devices = self.get_devices())