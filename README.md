# libre-hardware-exporter
Prometheus exporter for Libre Hardware Monitor

# What is this repo doing?
You are able to export all Libre Hardware Monitor Data to Prometheus.

# Requirements
- Python
- nssm
- Libre Hardware Monitor

# Installation

``` yaml
scrape_configs:
  - job_name: 'libre_exporter'
    static_configs:
      - targets: ['$YOUR.GAMING.MACHINE.IP:9187']
```

