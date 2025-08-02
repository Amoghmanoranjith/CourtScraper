## Delhi High court
- https://delhihighcourt.nic.in/app/get-case-type-status

## Captcha workaround approach
- The page gets captcha, captcha audio everytime captcha is reloaded (the captcha is plain text in html elements)
- the page uses two tokens XSRF-TOKEN and hc_application_session (both expire in 2hrs after generation)
- captcha validation is a POST request to https://delhihighcourt.nic.in/app/validateCaptcha which takes takes both cookies as request cookies along with a token regenerated at page loading and returns a new pair of cookies along with captcha validation success
- removing the hc_application cookie causes a validation failure response
- the web page based upon this success makes a request to **https://delhihighcourt.nic.in/app/generate-captcha with input case parameters**
- however cookies and token are not validated at this (tested by removing the cookies in postman)
- so i directly use this api thus completely bypassing the need to get token and cookies
