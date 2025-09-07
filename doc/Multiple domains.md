# Multiple domains in Zulip

## Doesn't work out of the box
As I indicated in https://github.com/zulip/zulip/issues/35945

Although Zulip requires that all organizations in a single server instance share a domain and differ only by subdomain, e.g. a.example.com and b.example.com, it's pretty easy to support completely distinct domains by the use of a reverse proxy, e.g. a.example.com and b.alternate.com.

But one area where support is lacking is in attachments: when trying to add an attachment or image to a message, the frontend makes its requests not to the current hostname b.alternate.com but to the original hostname b.example.com.

If the frontend were to make its requests to a url which didn't specify the origin, e.g. /api/v1/tus/3/eb/lvvV1jcG5Sk7FEUh1v20OneN/foo.png, and instead just let the browser apply the current hostname b.alternate.com, then this problem would be obviated.

Why requests from b.alternate.com to b.example.com fail: I'm thinking in particular of the PATCH request which the frontend makes to https://b.example.com/api/v1/tus/3/eb/lvvV1jcG5Sk7FEUh1v20OneN/foo.png. We run into a CORS error, and we can get past that by having the reverse proxy rewrite the Access-Control-Allow-... headers, but we can't get the frontend to provide authentication in the PATCH request because it won't send cookies across origins, so ultimately, we get a 401 Unauthorized response.

## Change script tags to not specify origin
The script tags currently specify the origin, and they all specify the EXTERNAL_HOST origin, regardless of what domain/subdomain is actually loaded for the page, e.g.
```html
<script src="https://duckofdoom.com/static/webpack-bundles/app.519be03733d467d8e138.js" defer crossorigin="anonymous" nonce="c2abbb58b377e912ac379f2a299f2c291da7fdf24fe5e1a2"></script>
```

These urls appear to be assembled in the function `webpack_entry` in `zerver/lib/templates.py`. Perhaps I can remove the origin there. (I'd have to commit the changes to the image, though.)
```bash
# Replace the line that says `staticfiles_storage.url(settings.WEBPACK_BUNDLES + filename)`
# Maybe this cmd isn't quite right, but it's close
sed -i '220 c\            staticfiles_storage.url(settings.WEBPACK_BUNDLES + filename).removeprefix(staticfiles_storage.base_url.removesuffix("/static/"))' /home/zulip/deployments/current/zerver/lib/templates.py
```
Then commit the changes on the docker image and restart the container. (Oh, committing appears not to even be necessary.)

Well, that didn't work. Even after getting the scripts to load from relative urls, it's still making requests to
https://famchat.duckofdoom.com/api/v1/tus/3/72/Q-OD5w2ljURNOkh6124FWKH2/hart.png

## Examining the javascript
`web/src/upload.ts`
```js
export let upload_files = (...)
// ...
const uppy = new Uppy<ZulipMeta, TusBody>({...})
// ...
uppy.use(Tus, {...})
// ...
upload_files(uppy, config, files);
```

Looks like the frontend is getting that url from the Location header in the response to the POST to
https://famchat.markhamanderson.com/api/v1/tus/

I can see these clues in the server logs (in development mode):
```
2025/09/05 03:52:33.636569 level=INFO event=RequestIncoming method=POST path="" requestId=""
2025/09/05 03:52:33.636678 level=DEBUG event=HookInvocationStart type=pre-create id=""
2025-09-05 03:52:33.639 INFO [zr] 127.0.0.1       POST    200   1ms /api/internal/tusd (15@zulip via Go-http-client)
2025/09/05 03:52:33.639971 level=DEBUG event=HookInvocationFinish type=pre-create id=""
2025/09/05 03:52:33.640288 level=INFO event=UploadCreated method=POST path="" requestId="" id=2/81/X5JqX3ukQqh5ZDUN6Fe9p4rn/hart.png size=15528 url=http://localhost:9991/api/v1/tus/2/81/X5JqX3ukQqh5ZDUN6Fe9p4rn/hart.png
2025/09/05 03:52:33.640309 level=INFO event=ResponseOutgoing method=POST path="" requestId="" id=2/81/X5JqX3ukQqh5ZDUN6Fe9p4rn/hart.png status=201 body=""
```

Apparently, zulip ships with a tus binary, and i guess zulip nginx preverse proxies the post request to tus, so tus is the one returning the post response with the Location header that I want to change.  but since I'm using apache to run a reverse proxy upstream of that, I might as well use apache to rewrite that location heater with `Header edit Location ^https://famchat.duckofdoom.com/api/v1/tus/(.*) https://famchat.markhamanderson.com/api/v1/tus/\1`

## Change realm url
So that pages like the login page don't show the user the wrong url, update `def url` in `zerver/models/realms.py`:
```bash
# in container:
cd /home/zulip/deployments/current
sed -E -e '/\s*def url\(self\) -> str:/ {n; s|^(\s*)return (.*)|\1return (\2).replace("famchat.duckofdoom.com", "famchat.markhamanderson.com")|}' -i zerver/models/realms.py
grep -F 'settings.EXTERNAL_URI_SCHEME + self.host' zerver/models/realms.py
# on host:
docker commit zulip_zulip_1 zulip/docker-zulip:11.0-0
docker-compose restart zulip
```
