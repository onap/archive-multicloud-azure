## Multicloud Azure Plugin
This plugin is a part of multicloud component which contains the capability
to talk to Azure cloud based on the Service Principal credentials fetched
from AAI.

The initial version of this plugin will provide the API to register a Cloud
region. The plugin will provide both versions(v0 and v1) of API for
cloud registration.

#### Provided APIs:

**/api/multicloud-azure/v0/(?P<vimid>[0-9a-z-A-Z\-\_]+)/registry**
