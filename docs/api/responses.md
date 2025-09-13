### 2xx Responses

1. 200 OK
```json
HTTP/1.1 200 OK
{
  "data": {
    "query": "..."
  }
}
```

### 4xx Errors

1. 400 Bad Request
```json
HTTP/1.1 400 Bad Request
{
  "errors": [{
    "message": "Maximum query length is 50000 characters",
    "extensions": {
      "code": "400"
    }
  }]
}
```

2. 401 Unauthorized
```json
HTTP/1.1 401 Unauthorized
{
  "errors": [{
    "message": "Invalid access token",
    "extensions": {
      "code": "401"
    }
  }]
}
```

3. 404 Not Found
```json
HTTP/1.1 404 Not Found
{
  "errors": [{
    "message": "Invalid API version",
    "extensions": {
      "code": "404"
    }
  }]
}
```

4. 429 Too Many Requests
```json
HTTP/1.1 429 Too Many Requests
{
  "errors": [{
    "message": "Too many requests",
    "extensions": {
      "code": "429"
    }
  }]
}
```


### Error handling

The response for the errors object contains additional detail to help you debug your operation.

The response for mutations contains additional detail to help debug your query. To access this, you must request userErrors.

Properties: 
errors (array): A list of all errors returned
    errors[n].message (string): Contains details about the error(s).
    errors[n].extensions (object): Provides more information about the error(s) including properties and metadata.
        extensions.code (string): Shows error codes common to Shopify. Additional error codes may also be shown.


### Error Code & Description:
1. 400
- Bad Request: The server will not process the request.

2. 401
- Unauthorized: A call was made with an invalid API client (for example, using tokens that don't exist) or against an invalid Organization (for example, one that is disabled).

3. 404
- Not found: The resource isn’t available. This occurs when querying for something that has been deleted.

4. 429
- Too Many Requests: The client has exceeded the rate limit.

5. 500
- Internal Server Error: An internal error occurred in Shopify. Check out the Shopify status page for more information.
