import os
import json
import subprocess
import tempfile
import cgi
import shutil
from http.server import SimpleHTTPRequestHandler
from datetime import datetime
from logger import logger

class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def traverse_api_directory(self):
        result = []
        for root, _, files in os.walk('api'):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    relative_path = os.path.relpath(path, start='api')
                    module_name = os.path.splitext(relative_path.replace(os.sep, '.'))[0]
                    functions = self.get_functions(path)
                    result.append(f"file: {relative_path}; func: {functions}")
 
        return '\n'.join(f"{str(i + 1).rjust(4)}. {entry}" for i, entry in enumerate(result))

    def get_functions(self, file_path):
        functions = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith('def '):
                    function_name = line.strip().split('(')[0][4:]
                    functions.append(function_name)
        return functions

    def run_python_script(self, script_path, function_name=None, post_data={}, files=[]):
        logger.debug(f"{self.run_python_script.__name__}: script_path: {script_path}, function_name: {function_name}, post_data: {str(post_data)}, files: {str(files)}")
        command = ["python3", script_path]
        command.append(function_name if function_name is not None else "")


        if not isinstance(post_data, str):
            post_data = json.dumps(post_data)

        command.append(post_data)

        if not isinstance(files, str):
            files= json.dumps(files)

        command.append(files)
        logger.debug(f"{self.run_python_script.__name__} - command: {str(command)}")
        result = subprocess.run(command, capture_output=True, text=True, bufsize=0)
        logger.debug(f"{self.run_python_script.__name__} - result: {str(result)}")
        return result.stdout

    def check_api_path(self):
        if not self.path.startswith("/api"):
            message = f"Request path must start with /api/ but received {self.path}"
            logger.error(message)
            self.send_error(404, message)
            return False
        return True

    def get_script_and_function(self):
        path = self.path
        file_path = "." + path + ".py"

        if os.path.isfile(file_path):
            return file_path, None

        file_path, function_name = os.path.split(path)
        file_path = "." + file_path + ".py"

        if not os.path.isfile(file_path):
            raise FileNotFoundError("Endpoint not found!")

        return file_path, function_name

    def delete_lai_files(self):
        temp_dir = tempfile.gettempdir()
        today = datetime.today()
        for filename in os.listdir(temp_dir):
            if filename.lower().startswith('lai_'):
                filepath = os.path.join(temp_dir, filename)
                try:
                    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_date < today:
                        os.remove(filepath)
                except Exception:
                    pass

    def do_GET(self):
        self._set_headers()
        self.delete_lai_files()
        if self.path == '/':
            result = self.traverse_api_directory()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(result).encode())
            return

        if not self.check_api_path():
            return

        file_path, function_name = self.get_script_and_function()

        try:
            result = self.run_python_script(file_path, function_name)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(result).encode())
        except json.JSONDecodeError:
            logger.error("Invalid JSON output!")
            self.send_error(500, "Invalid JSON output!")

    def do_POST(self):
        self.delete_lai_files()
        if not self.check_api_path():
            return

        file_path, function_name = self.get_script_and_function()
        content_type = self.headers.get('Content-Type')

        if not content_type:
            self.send_error(400, "Content-Type header is missing")
            return

        if 'multipart/form-data' in content_type:
            self.handle_multipart_form_data(file_path, function_name)
        else:
            self.handle_non_multipart_form_data(file_path, function_name)

    def handle_multipart_form_data(self, file_path, function_name):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type']})

        if not form.list:
            self.send_error(400, "No form data provided")
            return

        post_data = {}
        files = []

        for field in form.keys():
            field_item = form[field]

            if field_item.filename:
                file_data = field_item.file.read()
                temp_dir = tempfile.mkdtemp(prefix='lai_')
                temp_file_path = os.path.join(temp_dir, field_item.filename)
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(file_data)
                files.append(temp_file_path)
#                post_data[field] = temp_file_path
            else:
                post_data[field] = field_item.value

        if not files:
            self.send_error(400, "No file provided")
            return

        self.process_request(file_path, function_name, post_data, files)

    def handle_non_multipart_form_data(self, file_path, function_name):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        logger.debug(f"content_length : {content_length }; post_data type: {type(post_data)}; post_data : {str(post_data)}")

        if not post_data:
            self.send_error(400, "Empty request body")
            return

        self.process_request(file_path, function_name, post_data, [])

    def process_request(self, file_path, function_name, post_data, files):
        logger.debug(f"file_path: {file_path}; function_name: {function_name}; post_data: {str(post_data)}; files: {str(files)}")
        try:
            result = self.run_python_script(file_path, function_name, post_data, files)
            logger.debug(f"result type: {type(result)}; result: {str(result)}")

            if not result.strip():  # Check if result is empty or only contains whitespace
                result = {"econtent": "empty"}

            if isinstance(result, dict):
                result = json.dumps(result).encode()
            elif isinstance(result, str):
                result = result.encode()
            else:
                raise TypeError(f"Expected either a string or JSON. Got {type(result)}")

            self._set_headers()
            self.wfile.write(result)

        except json.JSONDecodeError as je:
            logger.error(je)
            logger.error(f"result: {str(result)}")
            self.send_error(500, "Invalid JSON output from script")
        except Exception as e:
            logger.error(e)
            logger.error(str(result))
        finally:
            self.cleanup_temp_files(files)


    def cleanup_temp_files(self, files):
        for file_path in files:
            os.remove(file_path)
        if files:
            shutil.rmtree(os.path.dirname(files[0]))