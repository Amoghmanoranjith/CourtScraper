## Delhi High court
- https://delhihighcourt.nic.in

## Captcha workaround approach
- Analysed the requests being sent using network devtools.
- The page gets captcha, and captcha audio everytime from generate-captcha api (the captcha is plain text in html elements and can be webscraped using beautiful soup).
- The page uses two tokens XSRF-TOKEN and hc_application_session (both expire in 2hrs after generation).
- Captcha validation is a POST request to https://delhihighcourt.nic.in/app/validateCaptcha which takes takes both cookies as request cookies along with a token regenerated at page loading and returns a new pair of cookies along with captcha validation success.
- Removing the hc_application cookie returns a CSRF token mismatch during captcha validation.
- The web page, based upon validation success makes a request to **https://delhihighcourt.nic.in/app/get-case-type-status** with input case parameters.
- However cookies and token are not validated at this (tested by removing the cookies in postman).
- So i directly use this api thus completely bypassing the need to get token and cookies and perform captcha validation.
