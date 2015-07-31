MTMonkey Public API
===================

This API is used from clients to communicate with an MTMonkey application server.
See below for the internal API used between the application server and the individual
workers.

Requests
--------

The MTMonkey service server accepts requests via POST and GET HTTP
method with the following parameters.

### Parameters

-   *action*: string, function name -- the only
    option is *translate*, other may be used for testing purposes (**required**)
-   *sourceLang*: string -- ISO 639-1 code of the source language (*cs*,
    *en*, *de*, *fr*) (**required**)
-   *targetLang*: string -- ISO 639-1 code of the target language (*cs*,
    *en*, *de*, *fr*) (**required**)
-   *systemId*: string -- an aditional identification of the system variant that 
    should be used for translation (optional, default = empty string)
-   *alignmentInfo*: boolean -- request alignment information (optional,
    default = "false")
-   *text*: string -- text to be translated in UTF-8 character encoding
    (**required**)
-   *nBestSize*: integer -- maximum number of distinct translation 
    variants to return
    (optional, default = 1, i.e. one best translation is provided, the
    maximum value is set to 10).
-   *tokenize*: boolean -- indicates whether the input should be tokenized 
    according to the rules for the source languge
    (optional, default = "true")
-   *segment*: boolean -- indicates whether the input should be split
    into individual sentences before translation
    (optional, default = "true")
-   *detokenize*: boolean -- indicates whether the translation result
    should be detokenized according to the rules for the target languge
    (optional, default = "true")


### GET Method

Maximum length of GET queries depends on the current web server and
client HTTP library. But it is not recommended to translate sentences
longer than 2000 characters via this method. Based on RFC 2616, the
server returns 414 (Request-URI Too Long) status if a URL is longer than
10,000 bytes. An example of a HTTP GET query is following:

**http://URL/PATH?sourceLang=en&targetLang=fr&text=TEXT**

### POST Method

The requests via the POST method conform to the JSON format.

An example of a request in JSON format is given below:

```json
{
    "action": "translate",
    "sourceLang": "en",
    "targetLang": "de",
    "text": "I got a flu."
}
```

Response
--------

MTMonkey response conforms also the JSON format via HTTP. If the service
is available, the return HTTP code is always 200 OK – even if the server
is not able to translate a given input (in that case there is a special
error message sent in the response, see below). HTTP error codes other
then 200 OK retain their usual meaning (e.g. 500 Internal Error).

### Parameters

The response structure includes:

-   *errorCode* (number): error code (see below), returned always
-   *errorMessage* (string): a description of the error, returned always
-   *translation* (list of structures): contains the translated data as a list of 
    sentences, each of which contains the following:

    -   *translated* (list of structures): list of translations of one sentence
        (of length 1 by default, or longer if n-best lists were requested)

        -   *text* (string): translated text in UTF-8 character encoding
        -   *score* (number): translation score, expressing quality of
            translation, meaningful only for comparison of multiple translations
            of the same sentence
        -   *rank* (integer): rank of the translation option (ranked according
            to the scoring, counting from 0; this may be omitted as the rank
            is given by the order in the *translated* list)
        -   Further items if alignment information or multiple translation
            options are requested (see below).

    -   *src-tokenized* (string): tokenization of the source sentence (for
        the translation of multiple sentences and/or alignment information)
    
    -   *src* (string): source sentence in its original form (optional)
    
    -   *errorMessage* (string): if the translation of the particular sentence fails,
        this may contain a detailed error description (optional)
    
    -   *errorCode* (number):: if the translation of the particular sentence fails,
        this may contain a detailed error code (optional)


-   *translationId*: string, globally unique ID of the transaction 
    (may be omitted)

-   *timeWork*: string (float + units), the amount of time the worker took to translate 
    the request (optional)

-   *timeWait*: string (float + units), the amount of the translation has waited
    to be processed (optional)


An example response with one translation:

```json
{
    "errorCode": 0, 
    "errorMessage": "OK",
    "translation": [
        {
            "translated": [
                {
                    "text": "Es ist in Ordnung, aber ich muss die Pille.", 
                    "score": 100,
                    "rank": 0
                }
            ], 
        }
    ], 
    "translationId": "794dab3aaa784419b9081710c5cddb54"
}
```

An example response when translation finished with error:
```json
{
    "errorCode": 1,
    "errorMessage": "System is temporarily down"
}
```

#### Service Error Codes

| Error Code  | Description                                 | Meaning                                                                       |
|-------------|---------------------------------------------|-------------------------------------------------------------------------------|
| 0           | OK                                          | When everything went well and the query has been translated.                  |
| 1           | System is temporarily down                  | Particular required workers are currently off. Try again later.               |
| 2           | System busy                                 | Everything is running but system is currently overloaded. Try again later.    |
| 3           | Invalid language pair / system ID                       | Unknown language pair or system ID.                                                        |
| 5           | Parse error, missing or invalid argument …  | Any parse error or missing attribute.                                         |
| 8           | Unexpected worker error                     | Worker experienced an unknown error during the translation. Try again later.  |
| 99          | Some sentences could not be translated      | The MT system was not able to translate some of the input sentences.          |

#### HTTP Errors

You can also obtain HTTP errors other than 200 OK. They retain their
original meaning.

Advanced features
-----------------

### Alignment information

In the response (JSON document), the application server can also provide
phrase alignment information (see the *alignmentInfo* parameter). Phrase
alignment is a matching between phrases (consecutive words) from the
source sentence to phrases in the target (translated) sentence. In other
words, each part of a particular alignment information matches a
sequence of consecutive words from the source sentence with a sequence
of consecutive words from the target sentence. The word sequences are
identified by *start* and *end* indices, indexing starts with a zero.

As for tokenization, you obtain the following attributes:

-   *src-tokenized*: string, space separated sequence of input tokens
    (one per sentence)

-   *tokenized*: string, space separated sequence of output tokens
    (one per n-best list variant)

-   *alignment-raw*: phrase alignment information (one per n-best list variant)


```json
{
    "errorCode": 0, 
    "errorMessage": "OK", 
    "translation": [
        {
            "translated": [
                {
                    "text": "Es ist in Ordnung, aber ich muss die Pille.", 
                    "tokenized": "Es ist in Ordnung , aber ich muss die Pille .", 
                    "alignment-raw": [
                        {
                            "src-start": 0, 
                            "tgt-start": 0, 
                            "src-end": 1, 
                            "tgt-end": 1
                        }, 
                        {
                            "src-start": 2, 
                            "tgt-start": 2, 
                            "src-end": 4, 
                            "tgt-end": 5
                        }, 
                        {
                            "src-start": 5, 
                            "tgt-start": 6, 
                            "src-end": 6, 
                            "tgt-end": 7
                        }, 
                        {
                            "src-start": 7, 
                            "tgt-start": 8, 
                            "src-end": 7, 
                            "tgt-end": 8
                        }, 
                        {
                            "src-start": 8, 
                            "tgt-start": 9, 
                            "src-end": 8, 
                            "tgt-end": 9
                        }, 
                        {
                            "src-start": 9, 
                            "tgt-start": 10, 
                            "src-end": 9, 
                            "tgt-end": 10
                        }
                    ]
                }
            ], 
            "src-tokenized": "it 's ok , but i need that pill .", 
        }
    ], 
    "translationId": "794dab3aaa784419b9081710c5cddb54"
}
```

The meaning of indices is as follows:

-   *src-start*: the start of an interval of tokenized words of the
    source sentence (we are indexing from 0)

-   *src-end*: the end of an interval of tokenized words (inclusive)

-   *tgt-start*: the start of an interval of tokenized words of the
    translated sentence (we are indexing from 0)

-   *tgt-end*: the end of an interval of tokenized words (inclusive)

The indexes refer to tokenized text in *src-tokenized* and
*tgt-tokenized*.

### Multiple translation options

If the *nBestSize* value in the request is set to 2 or more, the service
provides the specified number of the best translation options. Each of
them is provided with a score.

An example of a response with two translation options.

```json
{
    "errorCode": 0, 
    "errorMessage": "OK",
    "translation": [
        {
            "translated": [
                {
                    "text": "Es ist in Ordnung, aber ich muss die Pille.",
                    "score": 100,
                    "rank": 0
                },
                {
                    "text": "Es ist OK, aber ich brauche diese Pille.",
                    "score": 96,
                    "rank": 1
                }
            ], 
        }
    ], 
    "translationId": "794dab3aaa784419b9081710c5cddb54"
}
```

Testing from the command line / browser window
----------------------------------------------

MTMonkey can be easily tested using the standard `curl` tool as in
the example below:

```bash
    curl -i -H "Content-Type: application/json" -X POST -d '{ "action":"translate", "sourceLang":"en", "targetLang":"de", "text": "It works." }' http://URL/PATH
```

This command sends a well-formed JSON request via HTTP POST method and
displays the response.


The GET method can be tested directly from the browser by providing the following URL format:

```
    http://URL/PATH?action=translate&sourceLang=en&targetLang=de&text=It+works.
```

MTMonkey internal API
=====================

The internal API is used in the communication between an MTMonkey application server 
and the individual workers. Two methods of communication are supported on the application
server side: XML-RPC and JSON. The worker implementation included in this package communicates 
via XML-RPC, whereas JSON support has been added to simplify alternative worker implementations.

An XML-RPC worker should support the following main method:

- **process_task** (multiple parameters) – this is used to request a translation, and should return
    the translated text. The internal format of both the request and the response is exactly
    the same as in the public API (see above for list of parameters).

Alternatively, a JSON worker should accept the same requests and produce the same responses
as described in the public API. The communication channel (XML-RPC or JSON) must be given 
to the application server in the configuration file (see ``config-example/appserver.cfg``
for details).

In addition, XML-RPC workers may support the following method for testing purposes:

- **alive_check** (no parameters) – this returns ``1`` if the worker is currently running.

### Testing from the command line

First save the XML request to a file `myquery.xml`
```xml
<?xml version="1.0"?>
<methodCall>
  <methodName>process_task</methodName>
  <params><param><value><struct>
    <member><name>action</name><value><string>translate</string></value></member>
    <member><name>sourceLang</name><value><string>en</string></value></member>
    <member><name>targetLang</name><value><string>de</string></value></member>
    <member><name>text</name><value><string>This is a test.</string></value></member>    
  </struct></value></param></params>
</methodCall>
```
Now use it with ``curl``:
```bash
curl -X POST -d @myquery.xml http://WORKER-URL:PORT/PATH
```
