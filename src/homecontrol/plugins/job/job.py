from homecontrol.plugin import Plugin
from bootstrap import Bootstrap
import homecontrol.job, inspect, homecontrol.signal

class Job(Bootstrap):
    
    def handle_request(self, handler, method, path=None, args={}, data=None):
        """ HTTP wrapper for job base class.
        
        Determines job, function and their appropriate arguments from the 
        given URL invokes it within the appropriate context. The return data 
        of the appropriate method will be converted into JSON and added to the
        http response. 
        
        Example:
            Invoke a method of the job base class within a job context:
            http://localhost:4000/job/<id>/<func>/<args>
            
            Note that if the method name starts with "sql_" prefix, a SQL 
            cursor will be added to the "sql" argument.
            
            Invoke a static method of the job base class: 
            http://localhost:4000/job/<func>/<arg>
        """
        
        token = path.split("/")
        
        if len(token) < 2:
            self.log_error("Skip invalid path \"%s\"." % path)
            return False
        
        # Support missing job id's e.g. for creating new jobs.
        job_id = None
        
        try:
            job_id = int(token[1])
            method_name = token[2]
            token = token[2:]
        except ValueError:
            job_id = None
            method_name = token[1]
            token = token[1:]
        
        # Load job from database
        job = homecontrol.job.Job
        if job_id is not None:
            job = homecontrol.job.Job.sql_load(self.sql(), job_id)
        
        # Auto-add sql cursor if this is a sql method!
        if method_name.startswith("sql_") and "sql" not in args:
            args["sql"] = self.sql()
        
        if not hasattr(job, method_name):
            self.log_error("No such method \"%s\"" % method_name)
            return False

        method = getattr(job, method_name)
        if not callable(method):
            self.log_error("Method \"%s\" not callable" % method)
            return False
        
        if data != None:
            self.send_json_response(handler, method(data, **args))
            return True

        self.send_json_response(handler, method(**args))
        return True
    
    def view(self, handler, job_id):

        job = homecontrol.job.Job.sql_load(self.sql(), job_id)

        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html", 
            html_form_data = {"name": job.name},
            job = job,
            signals = homecontrol.signal.Signal.sql_load(self.sql()))
                
        return True
    
    def create(self, handler):
        
        job = homecontrol.job.Job()

        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html",
            job = job,
            signals = homecontrol.signal.Signal.sql_load(self.sql()))
                
        return True
        
        