# Local AI Web Hook

This project extends [Local AI](https://github.com/ivostoykov/localAI) with pre-query functionality.

---

# Usage

## Installation
Clone this repository to any location of your choice.

## Start/Stop
Open a terminal in the project directory and run:


```
python app.py
```

A simple server will start on port 10001. You can specify an alternate port by passing it as a parameter to the command line:

```
python app.py 10002
```

**Note:** You may need to use `python3` instead of `python` in this command depending on your configuration.

## Hooks
As this is a Python project, all files must be Python scripts and must be located inside the `api/` directory; its contents are otherwise unrestricted.

## Calls

To list all available hooks, send a `GET` request to the root URL:

```
http://localhost:10001/
```

assuming the default port is used.

The response will be a list containing all available files and their functions.
```
   1. file: test.py; func: ['helloWorld']
   2. file: parsefile.py; func: ['do_Parse']
```

**Note:** Regardless of the requested data format, the response will have a `Content-Type` header set to `text/plain`.

Any other request must call the server `api/` endpoint (See [Examples](#examples) below).

## Consuming the hook

Requests expect four components, which are optional except for one:
1. File (required)
2. Function name (optional)
3. Post data (optional)
4. Attachment (optional)

You can provide any or all of these components when making a request.

## Examples

1. Calling a file:
```
http://localhost:10001/api/test
```

In this scenario, `test.py` file must define a default function that can handle the request.

2. To invoke a specific function, include its name in the URL path, separated from the file name by a slash ('/').

```
http://localhost:10001/api/test/helloWorld
```

Both scenarios are handled as both `GET` and `POST` requests, with the result returned as plain text.

When sending data via `POST`, you can provide it in either a `key=value` format (as FormData) or JSON format. Files must be sent using form-multipart encoding.

### Reading Web Resource

A simple example of how to fetch web content which can be passed next to the model as a context is available [here](api/readweb.py)

#### Usage

```
curl -X POST http://localhost:10001/api/readweb -H "Content-Type: application/json" -d '{"resource":"https://github.com/ivostoykov/localAI"}'
```