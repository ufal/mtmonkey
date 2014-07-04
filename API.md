MTMonkey API description
========================

Requests
--------

The MTMonkey service server accepts requests via POST and GET HTTP
method with the following parameters.

### Parameters

-   *action*: string, function name -- for testing purposes the only
    option is *translate*. Stable version provides additional service
    functions (**required**)
-   *sourceLang*: string -- ISO 639-1 code of the source language (*cs*,
    *en*, *de*, *fr*) (**required**)
-   *targetLang*: string -- ISO 639-1 code of the target language (*cs*,
    *en*, *de*, *fr*) (**required**)
-   *alignmentInfo*: string -- request alignment information (optional,
    default = "false")
-   *nBestSize*: integer -- maximum number of translation options
    (optional, default = 1, i.e. one best translation is provided, the
    maximum value is set to 10).
-   *detokenize*: boolean -- indicates whether the translation result
    should be detokenized according to the rules for the target languge
    (optional, default = "true")
-   *text*: string -- text to be translated in UTF-8 character encoding
    (**required**, maximum length is limited to 100 words)

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

    {
        "action": "translate",
        "sourceLang": "en",
        "targetLang": "de",
        "text": "I got a flu."
    }

Response
--------

MTMonkey response conforms also the JSON format via HTTP. If the service
is available, the return HTTP code is always 200 OK – even if the server
is not able to translate a given input (in that case there is a special
error message sent in the response, see below). HTTP error codes other
then 200 OK retain their usual meaning (e.g. 500 Internal Error).

### Parameters

The response structure includes one or more *translation* structures
(depending on the presence of *nBestSize* parameter) or an *error*
structure.

The **translation** structure consists of:

-   *translated*: list of translations (of length 1, by default, or
    longer if n-best lists requested)
-   *translationId*: string, globally unique ID of the transaction

The **translated** item consists of:

-   *text*: string, translated text in UTF-8 character encoding
-   *score*: number, translation score, expressing quality of
    translation, meaningful only for comparison of multiple translations
    of one query
-   *rank*: integer, rank of the translation option (ranked according
    the scoring, counting from 0)
-   Further items if alignment information or multiple translation
    options are requested (see below).

The **error** structure consists of:

-   *errorCode*: number, code of the error
-   *errorMessage*: detailed description of the error

An example response with one translation:

    {
        "errorCode": 0, 
        "translation": [
            {
                "translated": [
                    {
                        "text": "Es ist in Ordnung, aber ich muss die Pille.", 
                        "score": 100,
                        "rank": 0
                    }
                ], 
                "translationId": "794dab3aaa784419b9081710c5cddb54"
            }
        ], 
        "errorMessage": "OK"
    }

An example response when translation finished with error:

    {
        "errorCode": 1,
        "errorMessage": "System is temporarily down"
    }

#### Service Error Codes

  Error Code   Description                                  Meaning
  ------------ -------------------------------------------- ------------------------------------------------------------------------------
  0            OK                                           When everything went well and the query has been translated.
  1            System is temporarily down                   Particular required workers are currently off. Try again later.
  2            System busy                                  Everything is running but system is currently overloaded. Try again later.
  3            Invalid language pair                        Unknown language pair.
  5            Parse error, missing or invalid argument …   Any parse error or missing attribute.
  8            Unexpected worker error                      Worker experienced an unknown error during the translation. Try again later.

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

-   *tgt-tokenized*: string, space separated sequence of output tokens

-   *alignment-raw*: phrase alignment information


```
{
    "errorCode": 0, 
    "translation": [
        {
            "translated": [
                {
                    "text": "Es ist in Ordnung, aber ich muss die Pille.", 
                    "tgt-tokenized": "Es ist in Ordnung , aber ich muss die Pille .", 
                    "src-tokenized": "it 's ok , but i need that pill .", 
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
            "translationId": "794dab3aaa784419b9081710c5cddb54"
        }
    ], 
    "errorMessage": "OK"
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

    {
        "errorCode": 0, 
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
                "translationId": "794dab3aaa784419b9081710c5cddb54"
            }
        ], 
        "errorMessage": "OK"
    }

Testing from the command line
-----------------------------

MTMonkey can be easily tested using the standard tool **curl** [5] as in
the example below:

    curl -i -H "Content-Type: application/json" -X POST -d '{ "action":"translate", "sourceLang":"en", "targetLang":"de", "text": "It works." }' http://URL/PATH

This command sends a well-formed JSON request via HTTP POST method and
displays the response.
