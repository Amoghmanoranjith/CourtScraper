## Delhi High court
- https://delhihighcourt.nic.in

## Captcha workaround approach
- Analysed the requests being sent using network devtools.
- The page gets captcha, and captcha audio everytime from generate-captcha api (the captcha is plain text in html elements and can be webscraped using beautiful soup).
- The page uses two tokens XSRF-TOKEN and hc_application_session (both expire in 2hrs after generation).
- Captcha validation is a POST request to https://delhihighcourt.nic.in/app/validateCaptcha which takes takes both cookies as request cookies along with a token regenerated at page loading and returns a new pair of cookies along with captcha validation success.
- Removing the hc_application cookie returns a CSRF token mismatch during captcha validation.
- The web page, based upon validation success makes a request to **https://delhihighcourt.nic.in/app/get-case-type-status** with input case parameters.
- However cookies and token are not validated at this point(tested using postman).
- So i directly use this api thus completely bypassing the need to get token and cookies and performing captcha validation.

## Docker setup
-  docker run -e DB_URI="postgresql://neondb_owner:npg_K2PbWU9pyrxi@ep-weathered-bush-a14y86ex-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require" -p 8000:8000 courtscraper


## API 
hosted on 0.0.0.0 port 8000 
### GET /
- serve index.html, the frontend

### POST /scrape
- utilise the scraper object to scrape using body parameters
- Body:
    - case_type
    - case_number
    - case_year
- handle missing fields in data
- log the request and raw response in postgresql db

### GET /download
- return the file binary for requested pdf file
- handle missing document_id in url params
- if pdf does not exist return failed to fetch error




