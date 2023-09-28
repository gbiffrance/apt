
### Run the APT server

See `docker.compose.yml` as example

### Create GBIF Installation for the APT server

```
POST https://api.gbif.org/v1/installation
 {
     "organizationKey":"replace_by_your_organization_key", 
     "type":"HTTP_INSTALLATION", 
     "title":"replace_by_title", 
     "description":"replace_by_description",
     "endpoints": {"url":"replace_by_you_apt_public_url"}
 }

```

You can execute it with curl

```
curl -u user:password -X POST https://api.gbif-uat.org/v1/installation -d { replace_by_json_content }
```

You will get you installation key

