# app
This repo contains the code for our sentiment analysis web application.

## Installation

### Helm-Chart Installation
To install the application as a helm chart, run the following command from the root directory of this repository:
- `helm install <app-name> .\app-chart\`

### Docker Installation
- `docker build .`

### Monitoring
We have introduced 2 domain-specific metrics:

- button_counter
